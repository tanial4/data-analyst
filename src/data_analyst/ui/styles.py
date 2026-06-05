"""Visual design for the Gradio UI.

A restrained, editorial aesthetic: warm paper canvas, ink text, hairline borders,
a single deep-teal accent, and a serif/sans type pairing (Newsreader + Inter).
No gradients, glows, or decorative icons — hierarchy comes from type and space.
"""

from __future__ import annotations

# --- Palette (kept as constants so they can also feed the Gradio theme) -------
CANVAS = "#f4f3ef"   # warm paper
#: Page background. Fed to the theme's body_background_fill so Gradio paints it
#: in any mode (otherwise browser dark-mode shows a dark fill behind the app).
BODY_BG = CANVAS

# Injected into <head>. Two jobs:
#  1. Pin the app to the light palette regardless of the OS/browser theme. The
#     inline script runs during parse (before Gradio paints), so there's no dark
#     flash; the color-scheme meta stops the browser applying dark UA styles.
#  2. Load the web fonts (with system fallbacks if a network blocks Google Fonts).
HEAD = """
<meta name="color-scheme" content="light">
<script>
(function () {
  try {
    var u = new URL(window.location.href);
    if (u.searchParams.get('__theme') !== 'light') {
      u.searchParams.set('__theme', 'light');
      window.location.replace(u.href);
    }
  } catch (e) {}
})();
</script>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Newsreader:opsz,wght@6..72,400;6..72,500;6..72,600&family=Inter:wght@400;450;500;600&display=swap" rel="stylesheet">
"""

CSS = """
:root { color-scheme: light; }

/* Hard override of Gradio's dark theme: redefine the dark CSS variables to the
   light palette so every component stays light even if a `.dark` class is set
   (e.g. the OS is in dark mode and the theme redirect hasn't applied yet). */
.dark {
    --body-background-fill: #f4f3ef !important;
    --background-fill-primary: #ffffff !important;
    --background-fill-secondary: #faf9f6 !important;
    --block-background-fill: #ffffff !important;
    --block-label-background-fill: #ffffff !important;
    --border-color-primary: #e3e0d8 !important;
    --border-color-accent: #2f6b5f !important;
    --body-text-color: #20201e !important;
    --body-text-color-subdued: #8a877f !important;
    --color-text-body: #20201e !important;
}
.dark, html.dark, body.dark, gradio-app.dark, .dark .gradio-container {
    background: #f4f3ef !important;
    color: #20201e !important;
}

:root {
    --canvas:   #f4f3ef;
    --surface:  #ffffff;
    --ink:      #20201e;
    --ink-2:    #5f5d57;
    --ink-3:    #8a877f;
    --line:     #e3e0d8;
    --line-2:   #eeece6;
    --accent:   #2f6b5f;
    --accent-d: #25564d;
    --accent-w: #edf3f1;
    --sans: 'Inter', ui-sans-serif, system-ui, -apple-system, 'Segoe UI', sans-serif;
    --serif: 'Newsreader', Georgia, 'Times New Roman', serif;
}

/* Cover the whole viewport so nothing shows behind the centered app. */
html, body, gradio-app, .gradio-container {
    background: var(--canvas) !important;
}
body, gradio-app { min-height: 100vh !important; }
body, .gradio-container { font-family: var(--sans) !important; color: var(--ink) !important; }
.gradio-container {
    max-width: 1180px !important; margin: 0 auto !important;
    padding: 0 22px 28px !important; background: transparent !important;
}
footer { display: none !important; }
* { letter-spacing: normal; }

/* ---- Header ---------------------------------------------------------------- */
.app-header {
    padding: 26px 2px 18px !important;
    border-bottom: 1px solid var(--line) !important;
    margin-bottom: 20px !important;
}
.app-header .wordmark {
    font-family: var(--serif) !important;
    font-size: 26px !important; font-weight: 500 !important;
    color: var(--ink) !important; letter-spacing: -0.01em !important;
    line-height: 1.1 !important;
}
.app-header .tagline {
    font-size: 11.5px !important; font-weight: 600 !important;
    text-transform: uppercase !important; letter-spacing: 0.14em !important;
    color: var(--ink-3) !important; margin-top: 7px !important;
}

/* ---- Section labels -------------------------------------------------------- */
.section-label {
    font-size: 11px !important; font-weight: 600 !important;
    text-transform: uppercase !important; letter-spacing: 0.12em !important;
    color: var(--ink-3) !important; padding: 2px 2px 10px !important;
}

/* ---- Sidebar / panels ------------------------------------------------------ */
.sidebar { padding-right: 8px !important; }

.upload-wrap label, .upload-wrap .wrap {
    border: 1px dashed var(--line) !important;
    border-radius: 10px !important;
    background: var(--surface) !important;
    color: var(--ink-2) !important;
    transition: border-color .15s, background .15s !important;
}
.upload-wrap label:hover, .upload-wrap .wrap:hover {
    border-color: var(--accent) !important;
    background: var(--accent-w) !important;
}

.info-card {
    background: var(--surface) !important;
    border: 1px solid var(--line) !important;
    border-radius: 10px !important;
    padding: 16px 18px !important;
    font-size: 13.5px !important; line-height: 1.65 !important;
    color: var(--ink-2) !important;
}
.info-card strong { color: var(--ink) !important; font-weight: 600 !important; }

/* ---- Tabs (underline style) ------------------------------------------------ */
.tab-nav, div[role="tablist"] {
    background: transparent !important;
    border-bottom: 1px solid var(--line) !important;
    padding: 0 !important; gap: 4px !important;
}
.tab-nav button, div[role="tab"] {
    color: var(--ink-3) !important; font-size: 14px !important;
    font-weight: 500 !important; padding: 10px 16px !important;
    border: none !important; border-bottom: 2px solid transparent !important;
    background: transparent !important; border-radius: 0 !important;
    margin-bottom: -1px !important;
}
.tab-nav button:hover, div[role="tab"]:hover { color: var(--ink) !important; }
.tab-nav button.selected, div[role="tab"][aria-selected="true"] {
    color: var(--ink) !important;
    border-bottom: 2px solid var(--accent) !important;
    background: transparent !important;
}

/* ---- Conversation ---------------------------------------------------------- */
.chatbot {
    border: 1px solid var(--line) !important;
    background: var(--surface) !important;
    border-radius: 12px !important;
    box-shadow: 0 1px 2px rgba(32, 32, 30, 0.04) !important;
    font-size: 14.5px !important;
}
.chatbot .message.user,
.chatbot .user .message,
.chatbot [data-testid="user"] {
    background: var(--accent-w) !important;
    border: 1px solid #dde9e5 !important;
    border-radius: 12px 12px 4px 12px !important;
    color: var(--ink) !important;
    max-width: 80% !important; padding: 11px 15px !important;
}
.chatbot .message.bot,
.chatbot .bot .message,
.chatbot [data-testid="bot"] {
    background: var(--surface) !important;
    border: 1px solid var(--line) !important;
    border-radius: 12px 12px 12px 4px !important;
    color: var(--ink) !important;
    max-width: 92% !important; padding: 13px 17px !important;
    line-height: 1.66 !important;
}
.chatbot .message.bot p:first-child { margin-top: 0 !important; }

.chatbot table {
    width: 100% !important; border-collapse: collapse !important;
    font-size: 13px !important; margin: 12px 0 4px !important;
    border: 1px solid var(--line) !important; border-radius: 8px !important;
    overflow: hidden !important;
}
.chatbot table th {
    background: #faf9f6 !important; color: var(--ink-2) !important;
    padding: 9px 12px !important; font-weight: 600 !important;
    text-align: left !important; border-bottom: 1px solid var(--line) !important;
}
.chatbot table td {
    padding: 8px 12px !important; color: var(--ink-2) !important;
    border-bottom: 1px solid var(--line-2) !important;
}
.chatbot table tr:last-child td { border-bottom: none !important; }

/* ---- Input + actions ------------------------------------------------------- */
.input-row { margin-top: 14px !important; }
.input-row textarea, .input-row input {
    background: var(--surface) !important;
    border: 1px solid var(--line) !important;
    border-radius: 10px !important;
    color: var(--ink) !important;
    font-size: 14.5px !important; font-family: var(--sans) !important;
    padding: 12px 15px !important; resize: none !important; line-height: 1.5 !important;
    transition: border-color .15s, box-shadow .15s !important;
}
.input-row textarea::placeholder { color: var(--ink-3) !important; }
.input-row textarea:focus, .input-row input:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 3px rgba(47, 107, 95, 0.12) !important;
    outline: none !important;
}

.btn-send, .btn-send button {
    background: var(--accent) !important; color: #ffffff !important;
    border: 1px solid var(--accent) !important; border-radius: 10px !important;
    padding: 12px 22px !important; font-size: 14px !important; font-weight: 500 !important;
    min-width: 92px !important; box-shadow: none !important;
    transition: background .15s, border-color .15s !important;
}
.btn-send:hover, .btn-send button:hover {
    background: var(--accent-d) !important; border-color: var(--accent-d) !important;
}
.btn-ghost, .btn-ghost button {
    background: var(--surface) !important; color: var(--ink-2) !important;
    border: 1px solid var(--line) !important; border-radius: 10px !important;
    padding: 12px 16px !important; font-size: 14px !important; font-weight: 500 !important;
    transition: background .15s, color .15s !important;
}
.btn-ghost:hover, .btn-ghost button:hover {
    background: #faf9f6 !important; color: var(--ink) !important;
}

/* ---- Starter prompts ------------------------------------------------------- */
.starters { margin: 12px 0 2px !important; gap: 8px !important; }
.chip, .chip button {
    background: var(--surface) !important; color: var(--ink-2) !important;
    border: 1px solid var(--line) !important; border-radius: 999px !important;
    padding: 7px 14px !important; font-size: 13px !important; font-weight: 450 !important;
    box-shadow: none !important; transition: border-color .15s, color .15s, background .15s !important;
}
.chip:hover, .chip button:hover {
    border-color: var(--accent) !important; color: var(--accent-d) !important;
    background: var(--accent-w) !important;
}

/* ---- Chart ----------------------------------------------------------------- */
.chart-panel {
    background: var(--surface) !important; border: 1px solid var(--line) !important;
    border-radius: 12px !important; overflow: hidden !important;
    box-shadow: 0 1px 2px rgba(32, 32, 30, 0.04) !important;
}
.chart-panel img { width: 100% !important; border-radius: 8px !important; }
.caption {
    text-align: center !important; color: var(--ink-3) !important;
    font-size: 12.5px !important; padding: 12px 0 2px !important;
}

/* ---- Scrollbar ------------------------------------------------------------- */
::-webkit-scrollbar { width: 9px; height: 9px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: #d8d4ca; border-radius: 8px; }
::-webkit-scrollbar-thumb:hover { background: var(--ink-3); }
"""

WELCOME_MSG = [
    {
        "role": "assistant",
        "content": (
            "Load a dataset on the left to begin. Once it's in, ask in plain "
            "language and I'll compute the answer and, where it helps, plot it.\n\n"
            "I work directly on your data — summaries, group comparisons, "
            "distributions, correlations, rankings, and full statistics. Ask "
            "something specific, like \"average order value by region\" or "
            "\"how is delivery time distributed\"."
        ),
    }
]

# Generic starter prompts (work on most datasets). Shown as clickable chips.
EXAMPLES = [
    "Summarize the dataset",
    "Compare totals by category",
    "Show how the main metric is distributed",
    "Correlations between numeric columns",
]
