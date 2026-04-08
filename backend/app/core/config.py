from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # API
    api_cors_allow_origin: str = "*"

    # Storage
    uploads_root: str = "./data/uploads"
    outputs_root: str = "./data/outputs"

    # Models / AI keys (used later by other services)
    gemini_api_key: str = ""
    whisper_model_name: str = "medium"
    gpu_device: str = "cuda:0"

    # Auth (MVP: signed session token; swap with NextAuth/JWT later)
    auth_secret: str = "dev-change-me-dev-change-me-dev-change-me-2026"
    auth_token_ttl_seconds: int = 60 * 60 * 24 * 14


settings = Settings()

