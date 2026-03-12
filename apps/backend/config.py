from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    openrouter_api_key: str = ""
    anthropic_api_key: str = ""
    s3_bucket: str = "deepthink"
    s3_api: str = ""
    s3_api_access_key_id: str = ""
    s3_api_secret: str = ""
    s3_api_token: str = ""
    llm_model: str = "anthropic/claude-sonnet-4-6"
    default_num_questions: int = 2
    data_dir: str = "data/trees"

    class Config:
        env_file = ".env"
        extra = "ignore"


@lru_cache
def get_settings() -> Settings:
    return Settings()
