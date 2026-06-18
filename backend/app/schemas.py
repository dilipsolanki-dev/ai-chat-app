"""
Pydantic schemas = the typed shapes of data going IN and OUT of the API.

Think of these as Laravel Form Requests (validation) + API Resources/DTOs
(output shaping) combined into one class.

How FastAPI uses them:
  - A request-body parameter typed as a Pydantic model  -> FastAPI parses + VALIDATES
    the JSON. Bad/missing fields return HTTP 422 automatically (no manual checks!).
  - A `response_model=` on the route             -> FastAPI shapes/filters the output.
  - Both feed the auto-generated /docs schema.

`BaseModel` is the parent class every schema inherits from.
"""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


# ===========================================================================
# WORKED EXAMPLES  (these fix the fragile /echo from Phase 2)
# ===========================================================================
class EchoRequest(BaseModel):
    # `message: str` makes the field REQUIRED and must be a string.
    # Field(...) adds validation/metadata. min_length=1 rejects empty strings.
    # The "..." means "required with no default". description shows up in /docs.
    message: str = Field(..., min_length=1, description="Text to echo back")


class EchoResponse(BaseModel):
    you_said: str


# ===========================================================================
# YOUR TASK — write the chat schemas below.
# We'll use these in Phase 4 (DB) and Phase 6 (chat endpoints).
# ===========================================================================

# `Role` is a constrained string: only these 3 values are allowed anywhere we
# annotate something as `Role`. (Like a PHP enum / a DB check constraint.)
Role = Literal["user", "assistant", "system"]


# ChatRequest: the body a user POSTs to start/continue a chat.
class ChatRequest(BaseModel):
    # Rule: field_name: Type = Field(..., constraints).  "..." = required.
    message: str = Field(..., min_length=1, description="The user's message")


# MessageOut: how we return a single stored message to the frontend.
class MessageOut(BaseModel):
    # These are plain required fields — no extra constraints needed, so no Field(...).
    id: int
    role: Role
    content: str
    created_at: datetime

    # Lets Pydantic build this model straight from a SQLAlchemy row object
    # (reading .id, .role, ... as attributes) instead of needing a dict.
    model_config = {"from_attributes": True}


# ConversationOut: how we return a conversation summary.
class ConversationOut(BaseModel):
    id: int
    title: str
    created_at: datetime

    model_config = {"from_attributes": True}
