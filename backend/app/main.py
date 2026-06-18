"""
FastAPI application entry point.

Run the dev server (from the backend/ folder):
    uv run uvicorn app.main:app --reload

  - `app.main`  -> the module path (app/main.py)
  - `:app`      -> the FastAPI() object below, named `app`
  - `--reload`  -> auto-restart on code changes (like Laravel's hot reload)

Then open http://localhost:8000/docs — FastAPI auto-generates interactive API
docs (Swagger UI) from your type hints. There's nothing like this out-of-the-box
in Laravel; it's one of FastAPI's best features.

ASGI vs WSGI (one-line version): classic PHP/Laravel runs one request per worker
synchronously (WSGI-style). FastAPI runs on ASGI, an async server interface, so a
single worker can handle many in-flight requests while they await I/O (DB, OpenAI).
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers import chat, conversations
from app.schemas import EchoRequest, EchoResponse

# Create the application object. title/version show up in the /docs page.
app = FastAPI(title=settings.app_name, version="0.1.0")

# CORS: browsers block cross-origin requests unless the server opts in. Our React
# dev server (port 5173) is a different origin from the API (port 8000), so we
# must allow it explicitly (≈ Laravel's config/cors.php).
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Attach the routers (their routes live under /api/conversations).
app.include_router(conversations.router)
app.include_router(chat.router)


# ---------------------------------------------------------------------------
# WORKED EXAMPLE — a simple GET endpoint
# ---------------------------------------------------------------------------
# `@app.get("/health")` is a DECORATOR. It registers the function below as the
# handler for GET /health (≈ Route::get('/health', ...) in Laravel).
# The dict you return is automatically serialized to JSON.
@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "app": settings.app_name}


# ---------------------------------------------------------------------------
# YOUR TASK — write a POST endpoint:  POST /echo
# ---------------------------------------------------------------------------
# Goal: accept a JSON body like  {"message": "hello"}  and return
#       {"you_said": "hello"}.
#
# Steps:
#   1. Use the @app.post("/echo") decorator (note: post, not get).
#   2. FastAPI can hand you the JSON body as a parameter. The simplest way for
#      now: declare a parameter `body: dict`. (In Phase 3 we'll replace this loose
#      dict with a typed Pydantic model — that's the proper way.)
#   3. Read body["message"] and return {"you_said": <that value>}.
#
# Uncomment and complete:
#
@app.post("/echo", response_model=EchoResponse)
async def echo(body: EchoRequest) -> EchoResponse:
    return EchoResponse(you_said=body.message)


#
# After writing it:
#   - run:  uv run uvicorn app.main:app --reload
#   - open: http://localhost:8000/docs  -> expand POST /echo -> "Try it out"
#   - send: {"message": "hello"}  -> you should get {"you_said": "hello"}
