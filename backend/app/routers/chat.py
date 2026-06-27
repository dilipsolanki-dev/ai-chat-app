"""
The chat endpoint: POST /api/conversations/{id}/chat

Flow:
  1. Validate the conversation exists.
  2. Save the user's message to Postgres.
  3. Load the full history (so the model has context).
  4. Stream the assistant's reply to the browser via SSE, while collecting it.
  5. When the stream finishes, save the assistant's full reply to Postgres.

SSE (Server-Sent Events) is a simple one-way stream over HTTP: the server keeps
the connection open and sends lines like `data: <something>\n\n`. The browser's
reader sees each as it arrives — that's how tokens show up live in the UI.

We JSON-encode each event so text containing newlines/quotes can't break the
SSE framing. The frontend will JSON.parse each `data:` payload.
"""

import json
from collections.abc import AsyncIterator

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import SessionLocal, get_db
from app.models import Conversation, Message
from app.openai_client import chat_stream
from app.schemas import ChatRequest

router = APIRouter(prefix="/api/conversations", tags=["chat"])


@router.post("/{conversation_id}/chat")
async def chat_endpoint(
    conversation_id: int,
    body: ChatRequest,
    db: AsyncSession = Depends(get_db),
) -> StreamingResponse:
    # 1. Make sure the conversation exists. db.get(Model, pk) is a fast PK lookup.
    convo = await db.get(Conversation, conversation_id)
    if convo is None:
        raise HTTPException(status_code=404, detail="Conversation not found")

    # 2. Persist the user's message.
    user_msg = Message(conversation_id=conversation_id, role="user", content=body.message)

    # Auto-title: a brand-new conversation starts with the placeholder title
    # "New conversation". On the first message, derive a title from that message
    # (first 60 chars). We commit this on the REQUEST session (`db`) — not the
    # post-stream SessionLocal() block — because `convo` was loaded on `db`, so
    # SQLAlchemy already tracks it: the single db.commit() below flushes BOTH the
    # new user_msg and this title change in one transaction. We also capture
    # title_changed / new_title into plain locals NOW, because after the commit
    # the ORM object may be expired/refreshed, and the streaming generator below
    # runs later on a different session and must not touch `convo`.
    title_changed = False
    new_title = convo.title
    if convo.title == "New conversation":
        convo.title = body.message[:60].strip() or "New conversation"
        title_changed = True
        new_title = convo.title

    db.add(user_msg)
    await db.commit()

    # 3. Load the whole conversation so the model has context (oldest first).
    result = await db.execute(
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at)
    )
    history = [{"role": m.role, "content": m.content} for m in result.scalars().all()]

    # 4 + 5. Stream the reply out, then save it.
    async def event_generator() -> AsyncIterator[str]:
        collected: list[str] = []
        # If we just set the title, push one SSE frame first so the client can
        # update the sidebar live (before any reply tokens arrive).
        if title_changed:
            yield f"data: {json.dumps({'title': new_title})}\n\n"
        try:
            async for piece in chat_stream(history):
                collected.append(piece)
                # one SSE event per token piece
                yield f"data: {json.dumps({'delta': piece})}\n\n"
        except Exception as exc:  # surface upstream (e.g. OpenAI) errors to the client
            yield f"data: {json.dumps({'error': str(exc)})}\n\n"

        # Stream finished — save the assistant's full reply. We open a FRESH session
        # here (not the injected `db`): the request's session is tied to the request
        # lifecycle, and this generator runs while the response streams out, so using
        # an independent session is the safe, predictable choice.
        full_reply = "".join(collected)
        if full_reply:
            async with SessionLocal() as save_db:
                save_db.add(
                    Message(
                        conversation_id=conversation_id,
                        role="assistant",
                        content=full_reply,
                    )
                )
                await save_db.commit()

        # Tell the client we're done (frontend stops reading on this).
        yield f"data: {json.dumps({'done': True})}\n\n"

    # media_type text/event-stream is what makes this an SSE response.
    return StreamingResponse(event_generator(), media_type="text/event-stream")
