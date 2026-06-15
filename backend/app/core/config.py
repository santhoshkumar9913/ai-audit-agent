from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    gemini_api_key: str
    mongodb_url: str = "mongodb://localhost:27017"
    mongodb_db: str = "audit_agent"
    upload_dir: str = "./uploads"

    model_config = {"env_file": ".env"}


settings = Settings()
