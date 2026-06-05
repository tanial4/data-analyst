"""Gradio front-end wiring the agent to a conversation + chart + schema layout.

Each browser session gets its own :class:`AnalystAgent` (and therefore its own
:class:`AnalystSession`) stored in ``gr.State``, so users never share data.
"""

from __future__ import annotations

import html
import logging
import os

import gradio as gr

from ..agent.analyst_agent import AnalystAgent
from ..config import get_settings
from ..core.loader import load_dataframe
from ..core.session import AnalystSession
from .styles import BODY_BG, CSS, EXAMPLES, HEAD, WELCOME_MSG

# (Light-mode pinning is handled in styles.HEAD — an early <head> script + a CSS
# override of Gradio's dark variables — so it applies before the app paints.)

_EMPTY_INFO = "No dataset loaded yet. Add a CSV or Excel file above to begin."
_EMPTY_SCHEMA = "Load a dataset to inspect its columns, types, and sample values."

logger = logging.getLogger("data_analyst")


def _new_agent() -> AnalystAgent:
    return AnalystAgent(AnalystSession())


def _file_too_large(path: str, max_mb: int) -> bool:
    try:
        return os.path.getsize(path) > max_mb * 1024 * 1024
    except OSError:
        return False


def _safe(text: object) -> str:
    """HTML-escape user-controlled text (filenames, column names) before it is
    rendered as Markdown in the UI, so a crafted name can't inject markup."""
    return html.escape(str(text), quote=False)


def _dataset_summary(agent: AnalystAgent) -> str:
    df = agent.session.df
    num_cols = [_safe(c) for c in df.select_dtypes(include="number").columns.tolist()]
    cat_cols = [_safe(c) for c in df.select_dtypes(include=["object", "string", "category"]).columns.tolist()]
    missing = int(df.isna().sum().sum())
    return (
        f"**{_safe(agent.session.filename)}**\n\n"
        f"{len(df):,} rows &nbsp;·&nbsp; {len(df.columns)} columns\n\n"
        f"**Numeric** — {', '.join(num_cols[:6]) or 'none'}\n\n"
        f"**Categorical** — {', '.join(cat_cols[:6]) or 'none'}\n\n"
        f"**Missing values** — {missing:,}"
    )


def _handle_upload(file_obj, agent: AnalystAgent):
    """Load a file into the session; return (info_md, schema_md, chart_reset)."""
    if file_obj is None:
        return _EMPTY_INFO, _EMPTY_SCHEMA, None
    max_mb = get_settings().max_upload_mb
    if _file_too_large(file_obj.name, max_mb):
        return f"That file is larger than the {max_mb} MB limit.", _EMPTY_SCHEMA, None
    try:
        df = load_dataframe(file_obj.name)
        agent.session.load(df, os.path.basename(file_obj.name))
        return _dataset_summary(agent), agent.session.schema, None
    except ValueError as e:
        # load_dataframe raises ValueError with safe, user-facing messages
        # (unsupported format, empty file, ...).
        return f"Could not load that file: {e}", _EMPTY_SCHEMA, None
    except Exception:
        # Unexpected parser/IO errors may carry paths or data; log, don't show.
        logger.exception("Failed to load uploaded file")
        return "Could not read this file. Please check it is a valid CSV or XLSX.", _EMPTY_SCHEMA, None


def _handle_send(message: str, history: list, agent: AnalystAgent):
    """Run one agent turn; return (history, chart_path, cleared_input)."""
    if not message or not message.strip():
        return history, None, ""

    try:
        response = agent.run(message)
        table = response.table
        parts = [response.text]
        if table is not None and not table.empty and len(table) > 1:
            parts.append("\n\n" + table.iloc[:20, :30].to_markdown(index=False))
        reply = "\n\n".join(parts)
        chart = response.chart_path
    except Exception:
        # Don't surface raw exceptions (may contain data/paths) to the UI.
        logger.exception("Agent run failed")
        reply = "Something went wrong while analyzing your data. Please try rephrasing your question."
        chart = None

    history = history + [
        {"role": "user", "content": message},
        {"role": "assistant", "content": reply},
    ]
    return history, chart, ""


def _theme() -> gr.themes.Base:
    """A restrained, paper-and-ink theme with a single deep-teal accent."""
    # Fonts are loaded via `head` and applied in CSS; setting them on the theme
    # here triggers a Gradio theme-comparison bug, so we leave font defaults.
    return gr.themes.Soft(
        primary_hue="emerald",
        secondary_hue="emerald",
        neutral_hue="stone",
        radius_size=gr.themes.sizes.radius_sm,
        text_size=gr.themes.sizes.text_md,
    ).set(
        # Paint Gradio's own body background so nothing shows behind the app.
        body_background_fill=BODY_BG,
        body_background_fill_dark=BODY_BG,
    )


def build_demo() -> gr.Blocks:
    """Construct the Gradio Blocks app. (Theme, CSS, fonts applied at launch.)"""
    # analytics_enabled=False disables Gradio's outbound usage telemetry.
    with gr.Blocks(title="Data Analyst", analytics_enabled=False) as demo:
        agent_state = gr.State()

        gr.HTML(
            '<div class="app-header">'
            '<div class="wordmark">Data Analyst</div>'
            '<div class="tagline">Conversational analysis for CSV &amp; Excel data</div>'
            "</div>"
        )

        with gr.Row(equal_height=False):
            # ── Data panel ───────────────────────────────────────
            with gr.Column(scale=2, min_width=280, elem_classes=["sidebar"]):
                gr.HTML('<div class="section-label">Data</div>')
                file_input = gr.File(
                    label="Drop a CSV or Excel file, or click to browse",
                    file_types=[".csv", ".xlsx"],
                    elem_classes=["upload-wrap"],
                )
                file_info = gr.Markdown(value=_EMPTY_INFO, elem_classes=["info-card"])

            # ── Workspace ────────────────────────────────────────
            with gr.Column(scale=5):
                with gr.Tabs():
                    with gr.Tab("Conversation"):
                        chatbot = gr.Chatbot(
                            value=WELCOME_MSG,
                            label="",
                            height=468,
                            render_markdown=True,
                            show_label=False,
                            elem_classes=["chatbot"],
                        )
                        with gr.Row(elem_classes=["starters"]):
                            chips = [
                                gr.Button(text, scale=0, size="sm", elem_classes=["chip"])
                                for text in EXAMPLES
                            ]
                        with gr.Row(elem_classes=["input-row"]):
                            chat_input = gr.Textbox(
                                placeholder="Ask a question about your data",
                                show_label=False,
                                lines=1,
                                max_lines=5,
                                scale=8,
                            )
                            send_btn = gr.Button(
                                "Send", scale=0, variant="primary", elem_classes=["btn-send"]
                            )
                            clear_btn = gr.Button("Clear", scale=0, elem_classes=["btn-ghost"])

                    with gr.Tab("Chart"):
                        chart_output = gr.Image(
                            label="", show_label=False, height=480, elem_classes=["chart-panel"]
                        )
                        gr.HTML(
                            '<p class="caption">A chart is produced automatically '
                            "whenever it helps explain the answer.</p>"
                        )

                    with gr.Tab("Schema"):
                        schema_md = gr.Markdown(value=_EMPTY_SCHEMA, elem_classes=["info-card"])

        # ── Event wiring ──────────────────────────────────────────
        demo.load(fn=_new_agent, outputs=agent_state)

        file_input.change(
            fn=_handle_upload,
            inputs=[file_input, agent_state],
            outputs=[file_info, schema_md, chart_output],
        )

        send_args = dict(
            fn=_handle_send,
            inputs=[chat_input, chatbot, agent_state],
            outputs=[chatbot, chart_output, chat_input],
        )
        send_btn.click(**send_args)
        chat_input.submit(**send_args)
        clear_btn.click(fn=lambda: (WELCOME_MSG, None), outputs=[chatbot, chart_output])

        # Starter chips populate the input (the user can edit before sending).
        for chip, text in zip(chips, EXAMPLES):
            chip.click(fn=lambda t=text: t, outputs=chat_input)

    return demo


def _bypass_proxy_for_localhost() -> None:
    """Ensure localhost is exempt from any configured HTTP proxy.

    On corporate networks a system proxy often intercepts localhost, which makes
    Gradio's startup self-check fail with "localhost is not accessible". Adding
    localhost to NO_PROXY lets the app run locally without a public share link.
    """
    hosts = "localhost,127.0.0.1,::1"
    for var in ("NO_PROXY", "no_proxy"):
        existing = os.environ.get(var, "")
        os.environ[var] = f"{existing},{hosts}" if existing else hosts


def main() -> None:
    """Console entry point: build and launch the app."""
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    _bypass_proxy_for_localhost()
    settings = get_settings()

    if settings.share and settings.auth is None:
        logger.warning(
            "SHARE=true with no auth: the public link is open to anyone who has it "
            "(they can upload data and consume your API key). Set AUTH_USER/AUTH_PASSWORD to gate it."
        )

    demo = build_demo()
    demo.launch(
        server_name=settings.server_name,
        server_port=settings.server_port,
        share=settings.share,
        show_error=settings.show_error,
        auth=settings.auth,
        max_file_size=f"{settings.max_upload_mb}mb",
        theme=_theme(),
        css=CSS,
        head=HEAD,
        enable_monitoring=False,   # no /monitoring analytics dashboard
    )


if __name__ == "__main__":
    main()
