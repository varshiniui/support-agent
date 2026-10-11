from sqlalchemy.orm import Session

from app.agent.llm import LLMClient
from app.agent.prompts import build_system_prompt
from app.models import Message
from app.services.conversation_service import ConversationService

MAX_HISTORY = 20


class ChatService:
    def __init__(self, db: Session, llm: LLMClient):
        self.conversations = ConversationService(db)
        self.llm = llm

    def reply(self, user_id: int, conversation_id: int, text: str) -> list[Message]:
        conversation = self.conversations.get(user_id, conversation_id)

        history = [
            {"role": m.role, "content": m.content}
            for m in conversation.messages
            if m.role in ("user", "assistant")
        ][-MAX_HISTORY:]

        prompt = [
            {"role": "system", "content": build_system_prompt()},
            *history,
            {"role": "user", "content": text},
        ]
        answer = self.llm.generate(prompt)

        user_msg = self.conversations.add_message(user_id, conversation_id, "user", text)
        assistant_msg = self.conversations.add_message(
            user_id, conversation_id, "assistant", answer
        )
        return [user_msg, assistant_msg]