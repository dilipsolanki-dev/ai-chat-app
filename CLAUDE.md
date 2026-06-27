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
frontend/  React (Vite + TypeScript) — multi-conversation chat UI
```
- `backend/app/main.py` — FastAPI app, CORS, router includes
- `backend/app/config.py` — settings via `pydantic-settings` (reads `.env`)
- `backend/app/database.py` — async engine + session factory
- `backend/app/models.py` — SQLAlchemy models (Conversation, Message)
- `backend/app/schemas.py` — Pydantic request/response models
- `backend/app/openai_client.py` — OpenAI wrapper (streaming + non-streaming)
- `backend/app/routers/` — conversations.py (create / list / **DELETE** / list-messages, all
  404-guarded) and chat.py (SSE stream; **auto-titles** a conversation from its first message and
  emits a `data: {"title": ...}` SSE frame so the sidebar updates live)
- `frontend/src/api.ts` — typed client + SSE consumer `streamChat(id, msg, {onDelta,onTitle,onDone})`
- `frontend/src/hooks/` — `useConversations` (list / active id / localStorage), `useChat` (messages /
  streaming `send()`); `useChat` claims the active id via a ref so the load effect can't clobber an
  in-flight stream
- `frontend/src/components/` — Sidebar, ThreadList/ThreadItem, ChatHeader, MessageList, MessageItem
  (assistant text rendered with `react-markdown` + `remark-gfm`), Composer, EmptyState, TypingIndicator
- `frontend/nginx.conf` — prod SPA serving + `/api` proxy; `index.html` is `no-cache`, hashed
  `/assets/*` are `immutable` (so a rebuilt image shows up on a normal reload)

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

# Docker (run from repo root) — full stack in containers
sudo docker compose up --build            # db + backend + frontend -> app at :5173, api at :8000
sudo docker compose down                  # stop (add -v to also wipe the pgdata volume)
sudo docker compose exec db psql -U ai_chat -d ai_chat -c "\dt"   # inspect the dockerized DB

# Publish images to the registry (Docker Hub: dilipsolanki/ai-chat-*)
sudo docker login && sudo docker compose build && sudo docker compose push
```

## Conventions
- **Python:** type hints on all functions; `async def` for I/O (DB, OpenAI).
- **I/O contracts:** every request/response body is a Pydantic model in `schemas.py`.
- **DB:** async SQLAlchemy sessions provided via `Depends()`; never block the event loop.
- **Format/lint:** `ruff` (run before committing).
- **LLM provider:** any OpenAI-compatible API via the `openai` SDK. Default = **Groq** (free),
  model `llama-3.3-70b-versatile`, configured in `backend/.env` (`OPENAI_API_KEY` +
  `OPENAI_BASE_URL=https://api.groq.com/openai/v1` + `OPENAI_MODEL`). Switch to real OpenAI
  (empty `OPENAI_BASE_URL`) or Hugging Face by editing `.env` only — no code change.
- **No failing work at import time:** anything that can fail (constructing the OpenAI client,
  opening connections, validating credentials) goes inside a function, not at module top level.
  The OpenAI client is built lazily via `get_client()` in `openai_client.py` — otherwise simply
  importing the module crashes when no key is set (e.g. mock mode in Docker).

## Permissions (enforced by `.claude/settings.json` + `.claude/hooks/guard.py`)
This repo intentionally restricts what Claude may run — don't fight these, route around them:
- **git is read-only:** `status` / `diff` / `log` / `show` / `branch` allowed; `commit` / `push` /
  `add` / `reset` / `rebase` / `checkout` / `switch` / `merge` / … are **denied**. The user commits
  and pushes manually — hand them the commit message rather than trying to commit.
- **DB is read-only:** `psql` SELECTs and `-lqt` work; any write/DDL, `psql -f`, interactive psql, and
  `dropdb` are **denied** by the `guard.py` PreToolUse hook (heuristic keyword match — it can also
  false-positive on a read whose text contains a write keyword; just run such a query yourself).
- **Network:** `curl`/`wget` only to localhost/127.0.0.1; external hosts are denied.
- **Docker data:** `docker compose down -v`, `docker volume rm`, and prune are denied (protect pgdata).
- **Secrets:** editing any `**/.env` is denied (reading is allowed).
- **Dependency installs** (`npm install`, `uv add`, `pip install`) prompt before running.
These constrain Claude only — not the user's own terminal, and not the app's normal runtime DB writes.

## Secrets
- Never commit `.env`. Secrets live there: `OPENAI_API_KEY`, `DATABASE_URL`.
- `.env.example` documents required keys (no real values).

## Local services
- Postgres runs locally on `:5432`. DB name: `ai_chat`. (For containers, the backend reaches it
  at host `db`, not `localhost` — see `docker-compose.yml`.)
- **Docker is installed and the full stack runs** (`docker compose up --build`). App images are
  published to Docker Hub as `dilipsolanki/ai-chat-backend` and `dilipsolanki/ai-chat-frontend`;
  teammates `docker compose pull && docker compose up` with no source build. See README's
  "Share with the team via a Docker registry" section.
