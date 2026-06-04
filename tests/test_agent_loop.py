"""Exercises the agent's tool-calling loop with a scripted fake LLM.

No network / API key needed: we replace the Groq client with a fake that emits
a tool call, then a final answer, and assert the loop dispatches the tool, feeds
the result back, and returns the final text plus any chart produced.
"""

from __future__ import annotations

from dataclasses import dataclass

from langchain_core.messages import AIMessage

import data_analyst.agent.analyst_agent as agent_mod
from data_analyst.agent.analyst_agent import AnalystAgent
from data_analyst.core.session import AnalystSession


class _FakeLLM:
    """Returns pre-scripted AIMessages on successive ``invoke`` calls."""

    def __init__(self, scripted: list[AIMessage]):
        self._scripted = scripted
        self._i = 0

    def bind_tools(self, tools):  # noqa: ARG002 - signature parity only
        return self

    def invoke(self, messages):  # noqa: ARG002
        msg = self._scripted[self._i]
        self._i += 1
        return msg


@dataclass
class _FakeSettings:
    max_agent_iterations: int = 6


def test_agent_runs_tool_then_answers(monkeypatch, sample_df):
    scripted = [
        AIMessage(
            content="",
            tool_calls=[
                {
                    "name": "run_operation",
                    "args": {"operation": "sum", "target_column": "sales"},
                    "id": "call_1",
                    "type": "tool_call",
                }
            ],
        ),
        AIMessage(content="Total sales are 1,050 across all regions."),
    ]
    fake = _FakeLLM(scripted)
    monkeypatch.setattr(agent_mod, "get_llm", lambda: fake)
    monkeypatch.setattr(agent_mod, "get_settings", lambda: _FakeSettings())

    session = AnalystSession()
    session.load(sample_df, "sample.csv")
    agent = AnalystAgent(session)

    resp = agent.run("what are total sales?")

    assert "1,050" in resp.text
    # The tool ran and populated the session's result table.
    assert not session.last_table.empty


def test_agent_without_data_short_circuits(monkeypatch):
    monkeypatch.setattr(agent_mod, "get_llm", lambda: _FakeLLM([]))
    monkeypatch.setattr(agent_mod, "get_settings", lambda: _FakeSettings())
    agent = AnalystAgent(AnalystSession())
    resp = agent.run("anything")
    assert "upload" in resp.text.lower()
