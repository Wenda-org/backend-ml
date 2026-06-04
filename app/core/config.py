from pydantic import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@db:5432/wenda"
    MODEL_PATH: str = "./models/model.joblib"
    PORT: int = 8000
    ML_API_KEY: str = "wenda-ml-internal-secret-key"

    class Config:
        env_file = ".env"


settings = Settings()
