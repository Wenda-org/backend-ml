from pydantic import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@db:5432/wenda"
    MODEL_PATH: str = "./models/model.joblib"
    PORT: int = 8000

    class Config:
        env_file = ".env"


settings = Settings()
