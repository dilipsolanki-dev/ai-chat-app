# AI Chat App — a learning project

A full-stack AI chat application built to learn **Python / FastAPI / OpenAI / Docker**, coming
from a Laravel + React + Postgres background.

```
Browser ──HTTP/SSE──> FastAPI (uvicorn) ──> OpenAI API
                           │
                           └──> PostgreSQL (conversations, messages)
```

## Stack
- **Frontend:** React (Vite + TypeScript)
- **Backend:** FastAPI (Python 3.12), async SQLAlchemy, Alembic
- **DB:** PostgreSQL
- **LLM:** OpenAI API (`openai` SDK), default model `gpt-4o-mini`
- **Tooling:** `uv` (Python deps), `ruff` (lint/format), Docker (final phase)

## Quick start (local dev)

```bash
# 1. Backend
cd backend
cp .env.example .env          # fill in OPENAI_API_KEY + DATABASE_URL
uv sync                        # install deps into .venv
uv run alembic upgrade head    # create tables
uv run uvicorn app.main:app --reload   # http://localhost:8000/docs

# 2. Frontend (separate terminal)
cd frontend
npm install
npm run dev                    # http://localhost:5173
```

## Learning roadmap

This repo is built in phases — see the plan file. Each phase ends in a runnable checkpoint.

- [x] Phase 0 — Repo + Claude Code setup
- [x] Phase 1 — Python env + language crash-course
- [x] Phase 2 — FastAPI hello chat
- [x] Phase 3 — Pydantic schemas
- [x] Phase 4 — PostgreSQL + SQLAlchemy + Alembic
- [x] Phase 5 — OpenAI integration
- [x] Phase 6 — Chat endpoints + SSE streaming
- [x] Phase 7 — React frontend
- [x] Phase 8 — Hardening
- [x] Phase 9 — Dockerize

## Run with Docker (everything in one command)

```bash
docker compose up --build      # db + backend + frontend
# then open http://localhost:5173
docker compose down            # stop (add -v to wipe the DB volume)
```

## Share with the team via a Docker registry

Centralize the **built images** so teammates/servers *pull* them instead of rebuilding from source.
Images are tagged `dilipsolanki/ai-chat-*` in [docker-compose.yml](docker-compose.yml) — change
`dilipsolanki` to your Docker Hub username (or use `ghcr.io/<org>/...` for GitHub's registry).

### You (publisher): build & push — once per release
```bash
docker login                       # Docker Hub  (or: docker login ghcr.io)
docker compose build               # builds images AND tags them with the image: names
docker compose push                # uploads backend + frontend images to the registry
```

### Teammate / server (consumer): pull & run — no source build needed
They only need `docker-compose.yml` + a `.env`, then:
```bash
docker compose pull                # download the prebuilt images
docker compose up                  # run the whole stack
# open http://localhost:5173
```

**What is / isn't centralized:**
- ✅ **Images** (the app, frozen with its deps) live in the registry — pushed & pulled.
- ❌ **The `pgdata` volume** (your actual data) is NOT in the registry — it lives wherever the
  `db` container runs. Images = the app; volumes = the data.
- 🔑 **Secrets** (`OPENAI_API_KEY`) are never baked into images — they're passed at run time via
  env / `.env`. Keep `USE_MOCK_AI=true` to run with no key.

### Inspect the Dockerized database
```bash
docker compose exec db psql -U ai_chat -d ai_chat -c "\dt"                 # list tables
docker compose exec db psql -U ai_chat -d ai_chat -c "SELECT * FROM conversations;"
docker compose exec db psql -U ai_chat -d ai_chat                          # interactive (\q to quit)
```

### Everyday Docker commands
```bash
docker compose ps                  # what's running + health
docker compose logs -f backend     # tail backend logs
docker compose down -v             # stop AND wipe the DB volume (fresh start)
```
> Drop the `sudo` permanently: `sudo usermod -aG docker $USER`, then log out/in.

## Laravel → Python cheat sheet

| Laravel / PHP | Python / FastAPI |
|---|---|
| composer + vendor/ | `uv` + `.venv/` |
| composer.json | `pyproject.toml` |
| Routes + Controllers | FastAPI path operations |
| Form Request validation | Pydantic models |
| Eloquent | SQLAlchemy |
| artisan migrate | Alembic |
| service container / DI | `Depends()` |
| .env + config() | `pydantic-settings` |
| artisan serve | `uvicorn` |

## My learning notes
> Keep your own notes here as you go — what clicked, what confused you.
