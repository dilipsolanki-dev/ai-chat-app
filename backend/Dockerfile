# Backend image: FastAPI + uv on Python 3.12.
#
# Concept: a Dockerfile is a recipe that builds an IMAGE (a frozen snapshot of an
# OS + your app + deps). A running instance of an image is a CONTAINER.

FROM python:3.12-slim

# Pull the `uv` binary straight from its official image (no pip install needed).
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Copy only dependency metadata first so Docker can CACHE the install layer:
# if pyproject.toml hasn't changed, this expensive step is skipped on rebuild.
COPY pyproject.toml ./
RUN uv sync --no-dev

# Now copy the rest of the app (changes here don't bust the deps cache above).
COPY . .

EXPOSE 8000

# On start: apply DB migrations, then run the server bound to 0.0.0.0 so it's
# reachable from outside the container. (--host 0.0.0.0 is the Docker equivalent
# of "listen on all interfaces".)
CMD ["sh", "-c", "uv run alembic upgrade head && uv run uvicorn app.main:app --host 0.0.0.0 --port 8000"]
