"""
Phase 5 checkpoint — prove the OpenAI integration works end to end.

Prereqs:
  1. Put a real key in backend/.env ->  OPENAI_API_KEY=sk-...
  2. Finish chat_stream() in app/openai_client.py

Run:  cd backend && uv run python try_openai.py

You should see the reply appear token-by-token (not all at once) — that's streaming.
This file is a throwaway tester, not part of the app.
"""

import asyncio

from app.openai_client import chat, chat_stream


async def main() -> None:
    history = [{"role": "user", "content": "In one sentence, what is FastAPI?"}]

    print("--- non-streaming (waits, then prints whole reply) ---")
    reply = await chat(history)
    print(reply)

    print("\n--- streaming (tokens arrive live) ---")
    async for piece in chat_stream(history):
        print(piece, end="", flush=True)  # flush so it shows immediately
    print("\n\nDone. ✅")


asyncio.run(main())
