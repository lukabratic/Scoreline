from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+psycopg://scoreline:scoreline@localhost:5432/scoreline"
    balldontlie_api_key: str = ""
    football_data_api_key: str = ""
    api_football_key: str = ""


settings = Settings()
