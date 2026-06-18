"""
Conversation CRUD endpoints.

An APIRouter is a group of routes you attach to the app (≈ a Laravel controller
with a route-group prefix). Every route here lives under /api/conversations.

Async DB query pattern you'll see repeatedly:
    result = await db.execute(select(Model).where(...).order_by(...))
    rows = result.scalars().all()     # .scalars() -> model objects, not raw rows
"""

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import Conversation, Message
from app.schemas import ConversationOut, MessageOut

router = APIRouter(prefix="/api/conversations", tags=["conversations"])


# ---- WORKED EXAMPLE 1: create a conversation -------------------------------
@router.post("", response_model=ConversationOut)
async def create_conversation(db: AsyncSession = Depends(get_db)) -> Conversation:
    # `db: AsyncSession = Depends(get_db)` injects a session (the DI pattern).
    convo = Conversation()  # title uses the model's default "New conversation"
    db.add(convo)  # stage the INSERT
    await db.commit()  # run it
    await db.refresh(convo)  # reload so convo.id / convo.created_at are populated
    return convo  # response_model shapes this into ConversationOut JSON


# ---- WORKED EXAMPLE 2: list conversations ----------------------------------
@router.get("", response_model=list[ConversationOut])
async def list_conversations(db: AsyncSession = Depends(get_db)) -> list[Conversation]:
    result = await db.execute(select(Conversation).order_by(Conversation.created_at.desc()))
    return list(result.scalars().all())


# ---- YOUR TASK: list the messages in one conversation ----------------------
# Endpoint: GET /api/conversations/{conversation_id}/messages
# Return:   list[MessageOut]  (oldest first)
#
# Notes:
#  - `conversation_id: int` as a function param becomes a PATH parameter because
#    it matches {conversation_id} in the route string.
#  - Query pattern: select(Message).where(Message.conversation_id == conversation_id)
#    .order_by(Message.created_at)
#  - Return list(result.scalars().all())
#
# Uncomment and complete:
#
@router.get("/{conversation_id}/messages", response_model=list[MessageOut])
async def list_messages(conversation_id: int, db: AsyncSession = Depends(get_db)) -> list[Message]:
    result = await db.execute(
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at)
    )
    return list(result.scalars().all())
