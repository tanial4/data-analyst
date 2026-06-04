"""CSS and static copy for the Gradio UI (ChatGPT-style light theme)."""

from __future__ import annotations

CSS = """
body, .gradio-container {
    background: #ffffff !important;
    font-family: ui-sans-serif, system-ui, -apple-system, sans-serif !important;
    color: #0d0d0d !important;
}
.gradio-container { max-width: 1100px !important; margin: 0 auto !important; }

/* Sidebar */
.sidebar {
    background: #f9f9f9 !important;
    border-right: 1px solid #e5e5e5 !important;
}
.app-title {
    font-size: 15px !important;
    font-weight: 600 !important;
    color: #0d0d0d !important;
    padding: 18px 16px 14px !important;
    border-bottom: 1px solid #e5e5e5 !important;
    display: flex; align-items: center; gap: 8px;
}

/* Upload zone */
.upload-wrap label {
    border: 1.5px dashed #d1d5db !important;
    border-radius: 10px !important;
    background: #ffffff !important;
    transition: border-color .18s, background .18s !important;
}
.upload-wrap label:hover {
    border-color: #10a37f !important;
    background: #f0fdf4 !important;
}

/* Dataset info card */
.info-card {
    background: #ffffff !important;
    border: 1px solid #e5e5e5 !important;
    border-radius: 10px !important;
    padding: 14px 16px !important;
    font-size: 13px !important;
    line-height: 1.65 !important;
    color: #374151 !important;
}
.info-card strong { color: #10a37f !important; }

/* Chatbot */
.chatbot {
    border: none !important;
    background: #ffffff !important;
    font-size: 15px !important;
}
.chatbot .message.user {
    background: #f4f4f4 !important;
    border-radius: 18px 18px 4px 18px !important;
    color: #0d0d0d !important;
    border: none !important;
    font-size: 15px !important;
    max-width: 75% !important;
    padding: 12px 16px !important;
}
.chatbot .message.bot {
    background: #ffffff !important;
    border: 1px solid #e5e5e5 !important;
    border-radius: 18px 18px 18px 4px !important;
    color: #0d0d0d !important;
    font-size: 15px !important;
    max-width: 88% !important;
    padding: 14px 18px !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.06) !important;
    line-height: 1.65 !important;
}
.chatbot .message.bot table {
    width: 100% !important; border-collapse: collapse !important;
    font-size: 13px !important; margin-top: 10px !important;
}
.chatbot .message.bot table th {
    background: #f9fafb !important; color: #374151 !important;
    padding: 8px 12px !important; font-weight: 600 !important;
    border-bottom: 1px solid #e5e7eb !important; text-align: left !important;
}
.chatbot .message.bot table td {
    padding: 7px 12px !important;
    border-bottom: 1px solid #f3f4f6 !important; color: #374151 !important;
}
.chatbot .message.bot table tr:last-child td { border-bottom: none !important; }
.chatbot .message.bot table tr:hover td { background: #f9fafb !important; }

/* Input */
.input-row {
    border-top: 1px solid #e5e5e5 !important;
    background: #ffffff !important;
    padding: 12px 4px 4px !important;
}
.input-row textarea {
    background: #f9f9f9 !important;
    border: 1px solid #d1d5db !important;
    border-radius: 12px !important;
    color: #0d0d0d !important;
    font-size: 15px !important;
    padding: 13px 16px !important;
    resize: none !important;
    line-height: 1.5 !important;
    transition: border-color .18s, box-shadow .18s !important;
}
.input-row textarea:focus {
    border-color: #10a37f !important;
    box-shadow: 0 0 0 3px rgba(16,163,127,0.12) !important;
    background: #ffffff !important;
    outline: none !important;
}

/* Buttons */
.btn-send {
    background: #10a37f !important; color: white !important;
    border: none !important; border-radius: 10px !important;
    padding: 13px 22px !important; font-size: 14px !important;
    font-weight: 600 !important; min-width: 88px !important;
    transition: background .18s !important;
}
.btn-send:hover { background: #0e9268 !important; }
.btn-clear {
    background: transparent !important; color: #9ca3af !important;
    border: 1px solid #e5e7eb !important; border-radius: 10px !important;
    padding: 13px 14px !important; font-size: 13px !important;
    transition: all .18s !important;
}
.btn-clear:hover {
    background: #f9fafb !important; color: #6b7280 !important;
}

/* Chart */
.chart-panel {
    background: #ffffff !important; border: 1px solid #e5e5e5 !important;
    border-radius: 12px !important; overflow: hidden !important;
    margin-top: 4px !important;
}
.chart-panel img { width: 100% !important; border-radius: 10px !important; }

/* Tabs */
.tab-nav {
    background: #f9f9f9 !important;
    border-bottom: 1px solid #e5e5e5 !important;
    padding: 0 8px !important;
}
.tab-nav button {
    color: #6b7280 !important; font-size: 13px !important;
    font-weight: 500 !important; padding: 10px 16px !important;
    border-bottom: 2px solid transparent !important;
    background: transparent !important; border-radius: 0 !important;
}
.tab-nav button.selected {
    color: #10a37f !important;
    border-bottom: 2px solid #10a37f !important;
}

/* Tips */
.tips-box {
    font-size: 12.5px !important; color: #6b7280 !important;
    line-height: 1.7 !important; padding: 10px 14px 14px !important;
}
.tips-box b { color: #374151 !important; }

/* Scrollbar */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: #f9fafb; }
::-webkit-scrollbar-thumb { background: #d1d5db; border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: #9ca3af; }
"""

WELCOME_MSG = [
    {
        "role": "assistant",
        "content": (
            "Hi! I'm your AI data analyst.\n\n"
            "Upload a **CSV or Excel** file in the left panel, then ask me anything about your data. I can:\n\n"
            "- Calculate averages, sums, min/max, medians\n"
            "- Group and compare categories\n"
            "- Show distributions and correlations\n"
            "- Generate charts automatically (bar, line, pie, scatter, histogram, heatmap, and more)\n"
            "- Provide full statistical summaries\n\n"
            "What would you like to analyze today?"
        ),
    }
]

EXAMPLES = [
    "Give me a summary of the dataset",
    "What is the average sales value?",
    "Show the distribution of prices",
    "Top 10 rows by highest value",
    "Group by category and sum",
    "Correlation between variables",
    "How many unique values are there?",
    "Full statistics for a column",
]
