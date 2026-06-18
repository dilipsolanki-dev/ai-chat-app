"""
Application settings.

This is the Python equivalent of Laravel's config/*.php + .env + config() helper.
`pydantic-settings` reads values from environment variables (and a .env file),
VALIDATES their types, and gives you one typed `settings` object to import anywhere.

We add the real fields (DATABASE_URL, OPENAI_API_KEY) in later phases. For now the
fields have safe defaults so the app boots without a .env file.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # SettingsConfigDict tells pydantic where to read from.
    #   env_file=".env"  -> load a .env file if present (like Laravel's .env)
    #   extra="ignore"   -> don't crash on unrelated env vars that exist on the machine
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "AI Chat API"
    # CORS: which frontend origins may call this API. Vite dev server runs on 5173.
    frontend_origin: str = "http://localhost:5173"

    # PostgreSQL connection string. Note the "+asyncpg" driver — that's what makes
    # SQLAlchemy talk to Postgres ASYNChronously (required for our async sessions).
    # Format: postgresql+asyncpg://<user>:<password>@<host>:<port>/<dbname>
    database_url: str = "postgresql+asyncpg://ai_chat:ai_chat@localhost:5432/ai_chat"

    # OpenAI — wired up in Phase 5. Empty default keeps the app bootable for now.
    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"

    # When True, the app fakes AI replies instead of calling OpenAI — so you can
    # build & test the whole app with no API quota/cost. Set USE_MOCK_AI=false in
    # .env (and add real credit) to switch to the real OpenAI API.
    use_mock_ai: bool = True

    # Log every SQL statement. Great while learning, noisy in normal use — off by default.
    sql_echo: bool = False


# Create ONE instance to import elsewhere:  `from app.config import settings`
settings = Settings()
