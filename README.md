---
title: Data Analyst
emoji: "\U0001F4C8"
colorFrom: gray
colorTo: green
sdk: gradio
sdk_version: 6.16.0
app_file: app.py
python_version: "3.11"
pinned: false
short_description: Conversational analysis for CSV & Excel data
---

# AI Agent Data Analyst

A tool-calling LLM agent that analyzes tabular data through natural-language
conversation. Upload a CSV/Excel file, ask questions, and the agent reasons in a
loop — inspecting the schema, running deterministic pandas operations, and
rendering charts — then replies in plain language.

Built on **Groq** (`llama-3.3-70b-versatile`) + **LangChain** tool calling, with
a **Gradio** UI. Refactored from a single Google Colab notebook
(`reference/iadataanalyst_colab.py`) into a structured, tested package.

## How it works

```
question ──► AnalystAgent (LLM tool-calling loop)
                 │  picks tools, reasons, repeats up to N iterations
                 ├─ get_schema()      → dataset columns/types
                 ├─ run_operation()   → deterministic pandas compute (no LLM math)
                 └─ create_chart()    → matplotlib PNG
             ◄── natural-language answer + table + chart
```

The LLM never computes numbers itself — it orchestrates **deterministic tools**.
All math lives in `core/operations.py`; the model only decides *which* operation
and chart to run. This keeps answers accurate and the compute path testable.

## Setup

Requires Python 3.11+.

```powershell
# 1. Create / activate a virtualenv
python -m venv venv
.\venv\Scripts\Activate.ps1

# 2. Install
pip install -r requirements.txt        # or:  pip install -e ".[dev]"

# 3. Configure your Groq API key
copy .env.example .env                  # then edit .env and set GROQ_API_KEY
```

Get a key at <https://console.groq.com/keys>.

## Run

```powershell
python app.py            # or, after `pip install -e .`:  data-analyst
```

Then open the printed local URL (default <http://127.0.0.1:7860>). Set `SHARE=true`
in `.env` to expose a public tunnel.

## Test

```powershell
pytest                   # 41 tests, no API key required
```

The deterministic core (loader, filters, operations, charts, tools) is fully
covered; the agent loop is tested with a scripted fake LLM, so the suite runs
offline.

## Layout

| Path | Responsibility |
|------|----------------|
| `src/data_analyst/config.py` | Settings from env / `.env` (pydantic-settings) |
| `src/data_analyst/constants.py` | Canonical operation / agg / chart vocabularies |
| `src/data_analyst/llm/` | Groq chat-model factory |
| `src/data_analyst/core/` | Data loading, filtering, operations, session state |
| `src/data_analyst/charts/` | Matplotlib styling + chart renderers |
| `src/data_analyst/agent/` | Prompt, tools, and the tool-calling agent loop |
| `src/data_analyst/ui/` | Gradio app + CSS |
| `tests/` | pytest suite |
| `reference/` | Original Colab notebook (provenance) |

## Configuration

All settings are environment variables (see `.env.example`):

| Var | Default | Notes |
|-----|---------|-------|
| `GROQ_API_KEY` | — | **required** |
| `MODEL` | `llama-3.3-70b-versatile` | Groq model id |
| `TEMPERATURE` | `0.0` | |
| `MAX_AGENT_ITERATIONS` | `6` | Max tool-calling rounds per question |
| `SERVER_NAME` / `SERVER_PORT` | `127.0.0.1` / `7860` | |
| `SHARE` | `false` | Public Gradio tunnel |
| `AUTH_USER` / `AUTH_PASSWORD` | — | Set both to gate the app with a login |
| `MAX_UPLOAD_MB` | `50` | Reject larger uploads (memory guard) |
| `SHOW_ERROR` | `false` | Show raw tracebacks in the UI (debug only) |

## Security

This app has been hardened against the common risks of an LLM data tool:

- **No code execution** — the agent only invokes deterministic pandas operations; there is no `eval`/`exec`/`df.query`. A malicious dataset can't run code.
- **Per-session isolation** — each browser session gets its own data; nothing is shared globally.
- **Untrusted-data handling** — `contains` filters are literal (no regex injection / ReDoS); user-controlled text (filenames, column names) is HTML-escaped in the UI; dataset contents are treated as untrusted in the prompt.
- **Hardened file intake** — only CSV/XLSX; XLSX is checked against zip-bomb expansion; row count and upload size are capped.
- **No info leakage** — errors are logged server-side; users see generic messages (`SHOW_ERROR=false`).
- **No telemetry** — Gradio analytics and the monitoring dashboard are disabled.
- **Resource limits** — upload size, row count, schema size, and table-preview size are all capped.
- **Optional auth** — set `AUTH_USER`/`AUTH_PASSWORD`, **strongly recommended whenever `SHARE=true`** (a public link is otherwise open to anyone who has it).

Dependencies are CVE-clean (`pip-audit` passes). Re-run it after changing dependencies:

```powershell
pip install -e ".[dev]"
pip-audit
```

⚠️ A public `SHARE=true` link exposes the app over the internet and lets anyone with the link consume your Groq API key — keep it private, add auth, and shut it down (`Ctrl+C`) when done.
