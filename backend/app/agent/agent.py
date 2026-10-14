import json
import logging
from dataclasses import dataclass, field

from langchain_core.messages import BaseMessage, ToolMessage
from langchain_core.tools import BaseTool
from pydantic import ValidationError

from app.agent.llm import LLMClient
from app.core.exceptions import LLMUnavailableError

logger = logging.getLogger("roh.agent")

MAX_STEPS = 4


@dataclass
class ToolStep:
    name: str
    args: dict
    result: dict


@dataclass
class AgentRun:
    answer: str
    steps: list[ToolStep] = field(default_factory=list)


class SupportAgent:
    def __init__(self, llm: LLMClient, tools: list[BaseTool]):
        self.llm = llm
        self.tools = tools
        self.tools_by_name = {t.name: t for t in tools}

    def run(self, messages: list[BaseMessage]) -> AgentRun:
        conversation = list(messages)
        steps: list[ToolStep] = []

        for _ in range(MAX_STEPS):
            ai_message = self.llm.generate(conversation, self.tools)
            conversation.append(ai_message)

            if not ai_message.tool_calls:
                return AgentRun(answer=ai_message.content.strip(), steps=steps)

            for call in ai_message.tool_calls:
                result = self._run_tool(call["name"], call["args"])
                steps.append(ToolStep(call["name"], call["args"], result))
                conversation.append(
                    ToolMessage(
                        content=json.dumps(result, default=str),
                        tool_call_id=call["id"],
                        name=call["name"],
                    )
                )

        logger.error("Agent hit the step limit")
        raise LLMUnavailableError("Roh could not finish that request. Please try again.")

    def _run_tool(self, name: str, args: dict) -> dict:
        tool = self.tools_by_name.get(name)
        if tool is None:
            logger.warning("Model asked for an unknown tool: %s", name)
            return {"error": "Unknown tool."}
        try:
            return tool.invoke(args)
        except ValidationError as exc:
            problems = "; ".join(e["msg"] for e in exc.errors())
            return {"error": f"Invalid input: {problems}"}
        except Exception:
            logger.exception("Tool %s failed", name)
            return {"error": "The tool failed. Tell the customer you could not complete this."}