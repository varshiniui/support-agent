import json

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
from sqlalchemy.orm import Session

from app.agent.agent import SupportAgent
from app.agent.llm import LLMClient
from app.agent.prompts import chat_prompt
from app.agent.tools import build_tools
from app.core.config import settings
from app.models import Message, User
from app.services.conversation_service import ConversationService

MAX_HISTORY = 20


def to_langchain_messages(rows: list[Message]) -> list[BaseMessage]:
    messages: list[BaseMessage] = []
    for row in rows:
        if row.role == "user":
            messages.append(HumanMessage(content=row.content))
        elif row.role == "assistant":
            messages.append(AIMessage(content=row.content))
    return messages


class ChatService:
    def __init__(self, db: Session, llm: LLMClient):
        self.db = db
        self.conversations = ConversationService(db)
        self.llm = llm

    def reply(self, user: User, conversation_id: int, text: str) -> list[Message]:
        conversation = self.conversations.get(user.id, conversation_id)

        history = to_langchain_messages(conversation.messages)[-MAX_HISTORY:]
        prompt = chat_prompt.invoke(
            {"agent_name": settings.agent_name, "history": history, "input": text}
        )

        tools = build_tools(self.db, user.customer) if user.customer else []
        result = SupportAgent(self.llm, tools).run(prompt.to_messages())

        user_msg = self.conversations.add_message(user.id, conversation_id, "user", text)
        for step in result.steps:
            record = json.dumps({"args": step.args, "result": step.result}, default=str)
            self.conversations.add_message(
                user.id, conversation_id, "tool", record, tool_name=step.name
            )
        assistant_msg = self.conversations.add_message(
            user.id, conversation_id, "assistant", result.answer
        )
        return [user_msg, assistant_msg]