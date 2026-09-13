from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # SQLite keeps local development self-contained and requires no database server.
    database_url: str = "sqlite:///./cognitree.db"

    # Auth
    jwt_secret_key: str = "change-this-to-a-long-random-string"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    # LLM
    google_api_key: str = ""
    google_model: str = "gemini-3.8-flash"
    llm_generation_attempts: int = 3
    llm_request_timeout_seconds: int = 30

    # Vector store
    chroma_persist_dir: str = "./chroma_data"
    embedding_model: str = "all-MiniLM-L6-v2"

    # Chunking (matches the 500-char / 50-char overlap from the project spec)
    chunk_size: int = 500
    chunk_overlap: int = 50

    # Diagnostics
    mastery_threshold: float = 0.70
    diagnostic_min_attempts: int = 2
    quiz_session_length: int = 10


settings = Settings()
