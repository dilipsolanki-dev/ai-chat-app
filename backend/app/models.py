"""
SQLAlchemy ORM models = your database tables as Python classes (≈ Eloquent models).

SQLAlchemy 2.0 uses TYPED columns:
    name: Mapped[<python_type>] = mapped_column(<db-options>)

  - `Mapped[int]`         -> the Python/type side (and NOT NULL by default)
  - `Mapped[int | None]`  -> nullable column
  - `mapped_column(...)`  -> db-side options (primary key, FK, length, defaults)

`relationship(...)` links models together (≈ Eloquent's hasMany / belongsTo).
Alembic reads these classes (via Base.metadata) to generate migrations.
"""

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


# ===========================================================================
# WORKED EXAMPLE
# ===========================================================================
class Conversation(Base):
    __tablename__ = "conversations"  # the actual table name (≈ $table in Eloquent)

    # primary_key=True -> auto-incrementing PK (Postgres SERIAL/IDENTITY).
    id: Mapped[int] = mapped_column(primary_key=True)

    title: Mapped[str] = mapped_column(String(255), default="New conversation")

    # server_default=func.now() -> Postgres sets the timestamp on INSERT
    # (DB-side default, like Laravel's $table->timestamp()->useCurrent()).
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # One conversation hasMany messages. back_populates wires both sides together.
    # cascade=... -> deleting a conversation also deletes its messages.
    messages: Mapped[list["Message"]] = relationship(
        back_populates="conversation",
        cascade="all, delete-orphan",
        order_by="Message.created_at",
    )


# ===========================================================================
# YOUR TASK — write the `Message` model.
# ===========================================================================
# Table name: "messages". Columns:
#   id            -> Mapped[int],  primary key (copy the pattern above)
#   conversation_id -> Mapped[int], a FOREIGN KEY to conversations.id.
#                      Use: mapped_column(ForeignKey("conversations.id", ondelete="CASCADE"))
#   role          -> Mapped[str],  mapped_column(String(20))   # "user"/"assistant"/"system"
#   content       -> Mapped[str],  mapped_column(Text)         # Text = unlimited length
#   created_at    -> same server_default=func.now() pattern as above
#
# Then the belongsTo side of the relationship:
#   conversation: Mapped["Conversation"] = relationship(back_populates="messages")
#
# Uncomment and complete:
#
class Message(Base):
    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(primary_key=True)
    conversation_id: Mapped[int] = mapped_column(ForeignKey("conversations.id", ondelete="CASCADE"))
    role: Mapped[str] = mapped_column(String(20))
    content: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    conversation: Mapped["Conversation"] = relationship(back_populates="messages")
