"""Gradio front-end wiring the agent to a chat + chart + schema interface.

Each browser session gets its own :class:`AnalystAgent` (and therefore its own
:class:`AnalystSession`) stored in ``gr.State``, so users never share data.
"""

from __future__ import annotations

import os

import gradio as gr

from ..agent.analyst_agent import AnalystAgent
from ..config import get_settings
from ..core.loader import load_dataframe
from ..core.session import AnalystSession
from ._compat import apply_gradio_client_patch
from .styles import CSS, WELCOME_MSG

apply_gradio_client_patch()


def _new_agent() -> AnalystAgent:
    return AnalystAgent(AnalystSession())


def _handle_upload(file_obj, agent: AnalystAgent):
    """Load a file into the session; return (info_md, schema_md, chart_reset)."""
    if file_obj is None:
        return "*Upload a file to get started...*", "*No data loaded yet.*", None
    try:
        df = load_dataframe(file_obj.name)
        agent.session.load(df, os.path.basename(file_obj.name))

        num_cols = df.select_dtypes(include="number").columns.tolist()
        cat_cols = df.select_dtypes(include=["object", "string", "category"]).columns.tolist()
        info = (
            f"**{agent.session.filename}** loaded ✓\n\n"
            f"**{len(df):,} rows · {len(df.columns)} columns**\n\n"
            f"**Numeric:** {', '.join(num_cols[:5]) or '—'}\n\n"
            f"**Categorical:** {', '.join(cat_cols[:5]) or '—'}\n\n"
            f"**Null values:** {int(df.isna().sum().sum()):,}"
        )
        return info, agent.session.schema, None
    except Exception as e:
        return f"Error loading file: {e}", "*No data loaded yet.*", None


def _handle_send(message: str, history: list, agent: AnalystAgent):
    """Run one agent turn; return (history, chart_path, cleared_input)."""
    if not message or not message.strip():
        return history, None, ""

    try:
        response = agent.run(message)
        table = response.table
        parts = [response.text]
        if table is not None and not table.empty and len(table) > 1:
            parts.append("\n\n" + table.head(20).to_markdown(index=False))
        reply = "\n\n".join(parts)
        chart = response.chart_path
    except Exception as e:
        reply = f"Error during analysis: {e}"
        chart = None

    history = history + [
        {"role": "user", "content": message},
        {"role": "assistant", "content": reply},
    ]
    return history, chart, ""


def build_demo() -> gr.Blocks:
    """Construct the Gradio Blocks app."""
    with gr.Blocks(css=CSS, title="Data Analyst · AI") as demo:
        agent_state = gr.State()

        with gr.Row(equal_height=True):
            # ── SIDEBAR ──────────────────────────────────────────
            with gr.Column(scale=1, min_width=260, elem_classes=["sidebar"]):
                gr.HTML(
                    '<div class="app-title">'
                    '<svg width="17" height="17" viewBox="0 0 24 24" fill="none" '
                    'stroke="#10a37f" stroke-width="2" stroke-linecap="round">'
                    '<polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/></svg>'
                    ' Data Analyst</div>'
                )
                gr.HTML(
                    '<div style="padding:12px 14px 6px;font-size:11px;font-weight:600;'
                    'color:#9ca3af;letter-spacing:.06em;text-transform:uppercase;">Dataset</div>'
                )
                file_input = gr.File(
                    label="Upload CSV or Excel",
                    file_types=[".csv", ".xlsx", ".xls"],
                    elem_classes=["upload-wrap"],
                )
                file_info = gr.Markdown(
                    value="*Upload a file to get started...*",
                    elem_classes=["info-card"],
                )

            # ── MAIN PANEL ───────────────────────────────────────
            with gr.Column(scale=3):
                with gr.Tabs():
                    with gr.Tab("Chat"):
                        chatbot = gr.Chatbot(
                            value=WELCOME_MSG,
                            label="",
                            height=500,
                            show_copy_button=True,
                            render_markdown=True,
                            type="messages",
                            elem_classes=["chatbot"],
                            avatar_images=(
                                None,
                                "https://api.dicebear.com/8.x/bottts-neutral/svg?seed=analyst&backgroundColor=b6e3f4",
                            ),
                        )
                        with gr.Row(elem_classes=["input-row"]):
                            chat_input = gr.Textbox(
                                placeholder="Ask something about your data…",
                                show_label=False,
                                lines=1,
                                max_lines=5,
                                scale=8,
                            )
                            send_btn = gr.Button("Send ↗", scale=1, variant="primary", elem_classes=["btn-send"])
                            clear_btn = gr.Button("🗑", scale=0, elem_classes=["btn-clear"])

                    with gr.Tab("Chart"):
                        chart_output = gr.Image(
                            label="",
                            show_label=False,
                            show_download_button=True,
                            height=490,
                            elem_classes=["chart-panel"],
                        )
                        gr.HTML(
                            '<p style="text-align:center;color:#9ca3af;font-size:12px;padding:10px 0 2px;">'
                            'Chart is generated automatically with each analysis</p>'
                        )

                    with gr.Tab("Schema"):
                        schema_md = gr.Markdown(
                            value="*Upload a file to inspect the dataset schema.*",
                            elem_classes=["info-card"],
                        )

        # ── Event wiring ──────────────────────────────────────────
        demo.load(fn=_new_agent, outputs=agent_state)

        file_input.change(
            fn=_handle_upload,
            inputs=[file_input, agent_state],
            outputs=[file_info, schema_md, chart_output],
        )
        send_btn.click(
            fn=_handle_send,
            inputs=[chat_input, chatbot, agent_state],
            outputs=[chatbot, chart_output, chat_input],
        )
        chat_input.submit(
            fn=_handle_send,
            inputs=[chat_input, chatbot, agent_state],
            outputs=[chatbot, chart_output, chat_input],
        )
        clear_btn.click(fn=lambda: (WELCOME_MSG, None), outputs=[chatbot, chart_output])

    return demo


def main() -> None:
    """Console entry point: build and launch the app."""
    settings = get_settings()
    demo = build_demo()
    demo.launch(
        server_name=settings.server_name,
        server_port=settings.server_port,
        share=settings.share,
        show_error=settings.show_error,
    )


if __name__ == "__main__":
    main()
