"""The tool-calling data-analyst agent.

Implements a transparent ReAct-style loop: the LLM is bound to the session's
tools, and on each iteration we execute any tool calls it requests, feed the
results back, and continue until it produces a final natural-language answer (or
we hit the iteration cap).
"""

from __future__ import annotations

from dataclasses import dataclass, field

import pandas as pd
from langchain_core.messages import (
    AIMessage,
    BaseMessage,
    HumanMessage,
    SystemMessage,
    ToolMessage,
)

from ..config import get_settings
from ..llm.client import get_llm
from ..core.session import AnalystSession
from .prompts import SYSTEM_PROMPT
from .tools import build_tools


@dataclass
class AgentResponse:
    """What one ``run`` produces for the UI."""

    text: str
    chart_path: str | None = None
    table: pd.DataFrame = field(default_factory=pd.DataFrame)


class AnalystAgent:
    """Stateful agent bound to one :class:`AnalystSession`."""

    def __init__(self, session: AnalystSession) -> None:
        self.session = session
        self._tools = build_tools(session)
        self._tools_by_name = {t.name: t for t in self._tools}
        self._llm = get_llm().bind_tools(self._tools)
        self._max_iterations = get_settings().max_agent_iterations

    def run(self, question: str) -> AgentResponse:
        """Answer one question, running tools as needed."""
        if not self.session.has_data:
            return AgentResponse("Please upload a CSV or Excel file first so I can analyze it.")

        # Reset per-turn artifacts so a chart from a previous turn isn't reused.
        self.session.last_chart_path = None

        messages: list[BaseMessage] = [
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=question),
        ]

        for _ in range(self._max_iterations):
            ai_msg: AIMessage = self._llm.invoke(messages)
            messages.append(ai_msg)

            if not ai_msg.tool_calls:
                return AgentResponse(
                    text=_as_text(ai_msg.content),
                    chart_path=self.session.last_chart_path,
                    table=self.session.last_table,
                )

            for call in ai_msg.tool_calls:
                tool = self._tools_by_name.get(call["name"])
                if tool is None:
                    output = f"Unknown tool: {call['name']}"
                else:
                    try:
                        output = tool.invoke(call["args"])
                    except Exception as e:  # surface tool errors back to the model
                        output = f"Tool '{call['name']}' failed: {e}"
                messages.append(ToolMessage(content=str(output), tool_call_id=call["id"]))

        # Iteration budget exhausted — ask the model for a final answer with no tools.
        final = get_llm().invoke(messages + [HumanMessage(content="Give your final answer now, no more tools.")])
        return AgentResponse(
            text=_as_text(final.content),
            chart_path=self.session.last_chart_path,
            table=self.session.last_table,
        )


def _as_text(content: object) -> str:
    return content if isinstance(content, str) else str(content)
