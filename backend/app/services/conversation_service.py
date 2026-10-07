from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError
from app.models import Conversation


class ConversationService:
    def __init__(self, db: Session):
        self.db = db

    def create(self, user_id: int, title: str) -> Conversation:
        conversation = Conversation(user_id=user_id, title=title)
        self.db.add(conversation)
        self.db.commit()
        self.db.refresh(conversation)
        return conversation

    def list_for_user(self, user_id: int) -> list[Conversation]:
        stmt = (
            select(Conversation)
            .where(Conversation.user_id == user_id)
            .order_by(Conversation.id.desc())
        )
        return list(self.db.scalars(stmt))

    def get(self, user_id: int, conversation_id: int) -> Conversation:
        conversation = self.db.scalar(
            select(Conversation).where(
                Conversation.id == conversation_id,
                Conversation.user_id == user_id,
            )
        )
        if conversation is None:
            raise NotFoundError("Conversation not found")
        return conversation

    def delete(self, user_id: int, conversation_id: int) -> None:
        conversation = self.get(user_id, conversation_id)
        self.db.delete(conversation)
        self.db.commit()