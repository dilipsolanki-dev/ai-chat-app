# CLAUDE.md — AI Chat App

Guidance for Claude Code when working in this repository.

## What this is
A **learning project**: a full-stack AI chat app (React + FastAPI + OpenAI + PostgreSQL),
built by an experienced Laravel/React/Postgres developer who is **learning Python**.

## ⚠️ Learning mode (important)
This is a teaching repo. When asked to implement backend/Python features:
- **Prefer explaining + leaving guided `# TODO` markers** over writing complete solutions.
- Introduce one new Python/FastAPI concept at a time; relate it to Laravel/PHP where useful.
- The user writes the core logic; you scaffold and review.
- **Exception:** if the user explicitly says "just write it" / "do it for me", write the full code.
- The React frontend is the user's home turf — less hand-holding needed there.

## Stack & layout
```
backend/   FastAPI (Python 3.12), async SQLAlchemy, Alembic, openai SDK
frontend/  React (Vite + TypeScript)
```
- `backend/app/main.py` — FastAPI app, CORS, router includes
- `backend/app/config.py` — settings via `pydantic-settings` (reads `.env`)
- `backend/app/database.py` — async engine + session factory
- `backend/app/models.py` — SQLAlchemy models (Conversation, Message)
- `backend/app/schemas.py` — Pydantic request/response models
- `backend/app/openai_client.py` — OpenAI wrapper (streaming + non-streaming)
- `backend/app/routers/` — conversations.py, chat.py (SSE)

## Commands
```bash
# Backend (run from backend/)
uv sync                                   # install/update deps
uv run uvicorn app.main:app --reload      # dev server -> :8000, docs at /docs
uv run alembic revision --autogenerate -m "msg"
uv run alembic upgrade head               # apply migrations
uv run ruff check . && uv run ruff format .

# Frontend (run from frontend/)
npm install
npm run dev                               # -> :5173
```

## Conventions
- **Python:** type hints on all functions; `async def` for I/O (DB, OpenAI).
- **I/O contracts:** every request/response body is a Pydantic model in `schemas.py`.
- **DB:** async SQLAlchemy sessions provided via `Depends()`; never block the event loop.
- **Format/lint:** `ruff` (run before committing).
- **Default model:** `gpt-4o-mini` (cost-friendly for learning).

## Secrets
- Never commit `.env`. Secrets live there: `OPENAI_API_KEY`, `DATABASE_URL`.
- `.env.example` documents required keys (no real values).

## Local services
- Postgres runs locally on `:5432`. DB name: `ai_chat`. (Docker is added in the final phase.)
