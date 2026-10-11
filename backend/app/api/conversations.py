from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models import User
from app.schemas.conversation import (
    ConversationCreate,
    ConversationDetail,
    ConversationOut,
    MessageCreate,
    MessageOut
)

from app.services.conversation_service import ConversationService

router = APIRouter(prefix="/conversations", tags=["conversations"])


def get_conversation_service(db: Session = Depends(get_db)) -> ConversationService:
    return ConversationService(db)


@router.post("", response_model=ConversationOut, status_code=201)
def create_conversation(
    payload: ConversationCreate,
    user: User = Depends(get_current_user),
    service: ConversationService = Depends(get_conversation_service),
):
    return service.create(user.id, payload.title)


@router.get("", response_model=list[ConversationOut])
def list_conversations(
    user: User = Depends(get_current_user),
    service: ConversationService = Depends(get_conversation_service),
):
    return service.list_for_user(user.id)


@router.get("/{conversation_id}", response_model=ConversationDetail)
def get_conversation(
    conversation_id: int,
    user: User = Depends(get_current_user),
    service: ConversationService = Depends(get_conversation_service),
):
    return service.get(user.id, conversation_id)


@router.delete("/{conversation_id}", status_code=204)
def delete_conversation(
    conversation_id: int,
    user: User = Depends(get_current_user),
    service: ConversationService = Depends(get_conversation_service),
):


    service.delete(user.id, conversation_id)
@router.post(
    "/{conversation_id}/messages", response_model=list[MessageOut], status_code=201
)
def send_message(
    conversation_id: int,
    payload: MessageCreate,
    user: User = Depends(get_current_user),
    service: ConversationService = Depends(get_conversation_service),
):
    user_msg = service.add_message(user.id, conversation_id, "user", payload.content)
    # TEMPORARY: Phase 7 replaces this line with the real LLM reply.
    reply = service.add_message(
        user.id, conversation_id, "assistant", "Roh is not connected to the AI yet."
    )
    return [user_msg, reply]