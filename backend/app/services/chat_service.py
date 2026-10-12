from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
from sqlalchemy.orm import Session

from app.agent.llm import LLMClient
from app.agent.prompts import chat_prompt
from app.core.config import settings
from app.models import Message
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
        self.conversations = ConversationService(db)
        self.llm = llm

    def reply(self, user_id: int, conversation_id: int, text: str) -> list[Message]:
        conversation = self.conversations.get(user_id, conversation_id)

        history = to_langchain_messages(conversation.messages)[-MAX_HISTORY:]
        prompt = chat_prompt.invoke(
            {"agent_name": settings.agent_name, "history": history, "input": text}
        )
        answer = self.llm.generate(prompt.to_messages())

        user_msg = self.conversations.add_message(user_id, conversation_id, "user", text)
        assistant_msg = self.conversations.add_message(
            user_id, conversation_id, "assistant", answer
        )
        return [user_msg, assistant_msg]