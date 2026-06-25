"""
Thin wrapper around the OpenAI SDK.

We use the `openai` SDK, but it talks to ANY OpenAI-compatible provider — real
OpenAI, Groq, Hugging Face — by just pointing `base_url` at them. We currently
use Groq (free). Switching providers is a .env change, not a code change.

Keeping all LLM calls in ONE module (instead of sprinkling them through your
routes) is the same instinct as a Laravel Service class: one place to change the
model, handle errors, swap providers, etc.

Key ideas:
  - We use AsyncOpenAI (the async client) so calls fit FastAPI's event loop.
  - "messages" is the conversation history: a list of {"role", "content"} dicts,
    where role is "system" | "user" | "assistant". The model reads the whole list
    each call — the API itself is stateless; WE supply the history (from Postgres
    in Phase 6).
"""

import asyncio
from collections.abc import AsyncIterator

from openai import AsyncOpenAI

from app.config import settings

# Build the client LAZILY, not at import time.
#
# Why: the OpenAI SDK raises if you construct AsyncOpenAI() without a key. If we
# did that at module level (`client = AsyncOpenAI(...)`), simply IMPORTING this
# file would crash whenever no key is set — even in mock mode, where we never
# call OpenAI at all. So instead we cache one client and only create it the first
# time a real call needs it. (Think: a lazily-resolved singleton from the
# service container, rather than one built eagerly on boot.)
_client: AsyncOpenAI | None = None


def get_client() -> AsyncOpenAI:
    """Return a shared AsyncOpenAI client, constructing it on first use."""
    global _client
    if _client is None:
        # base_url="" means "use the SDK default" (real OpenAI). Set it in .env to
        # point at Groq/HF. `or None` converts the empty string to the SDK's default.
        _client = AsyncOpenAI(
            api_key=settings.openai_api_key,
            base_url=settings.openai_base_url or None,
        )
    return _client

# A "system" message steers the assistant's behavior. Prepend it to every request.
SYSTEM_PROMPT = {
    "role": "system",
    "content": "You are a helpful, concise assistant inside a learning project.",
}


# ===========================================================================
# WORKED EXAMPLE — non-streaming. Sends history, waits, returns the full reply.
# ===========================================================================
def _mock_reply(messages: list[dict]) -> str:
    """A canned reply used when USE_MOCK_AI is true (no API call/cost)."""
    last_user = next(
        (m["content"] for m in reversed(messages) if m["role"] == "user"),
        "your message",
    )
    return (
        f'[mock reply] I received: "{last_user}". '
        "This is a fake response so you can build the app without OpenAI quota. "
        "Set USE_MOCK_AI=false in .env once you have a real key."
    )


_PLACEHOLDER_KEYS = {"", "sk-your-key-here", "gsk_your-groq-key-here"}


def _require_key() -> None:
    """Fail fast with a clear message when real mode is on but no key is set."""
    if settings.openai_api_key in _PLACEHOLDER_KEYS:
        raise RuntimeError(
            "No API key set. Put your provider key in backend/.env as OPENAI_API_KEY "
            "(Groq keys start with 'gsk_', from https://console.groq.com), "
            "or keep USE_MOCK_AI=true to use fake replies."
        )


async def chat(messages: list[dict]) -> str:
    """Return the assistant's complete reply as one string."""
    if settings.use_mock_ai:
        return _mock_reply(messages)
    _require_key()
    response = await get_client().chat.completions.create(
        model=settings.openai_model,
        messages=[SYSTEM_PROMPT, *messages],  # *messages spreads the list (like JS ...)
    )
    # The SDK returns a structured object; the text lives here:
    return response.choices[0].message.content or ""


# ===========================================================================
# YOUR TASK — streaming version. Yields the reply in small pieces as they arrive.
# ===========================================================================
# This is an ASYNC GENERATOR: `async def` + `yield`. It returns an async iterator
# the caller consumes with `async for piece in chat_stream(...)`.
#
# Steps:
#   1. Call the same create(...) but add  stream=True. With streaming, the SDK
#      returns an async iterator of "chunks" instead of one response object.
#        stream = await client.chat.completions.create(
#            model=settings.openai_model,
#            messages=[SYSTEM_PROMPT, *messages],
#            stream=True,
#        )
#   2. Loop over it with `async for chunk in stream:`
#   3. Each chunk carries a partial token in  chunk.choices[0].delta.content
#      — but it can be None (e.g. the first/last chunks), so guard it:
#        delta = chunk.choices[0].delta.content
#        if delta:
#            yield delta
#
async def chat_stream(messages: list[dict]) -> AsyncIterator[str]:
    """Yield the assistant's reply piece-by-piece as the API streams it."""
    if settings.use_mock_ai:
        # Simulate streaming: yield the canned reply word-by-word with a tiny delay.
        for word in _mock_reply(messages).split(" "):
            await asyncio.sleep(0.03)
            yield word + " "
        return

    _require_key()
    # stream=True -> instead of one response, the SDK gives an async iterator
    # that produces many small "chunks" as the model generates text.
    stream = await get_client().chat.completions.create(
        model=settings.openai_model,
        messages=[SYSTEM_PROMPT, *messages],
        stream=True,
    )

    # `async for` walks an ASYNC iterator (normal `for` can't await between items).
    async for chunk in stream:
        # Each chunk holds the next bit of text in .delta.content.
        # It's None on some chunks (start/end/metadata), so we skip those.
        delta = chunk.choices[0].delta.content
        if delta:
            yield delta  # hand this piece to the caller, then resume on next chunk
