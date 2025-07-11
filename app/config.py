from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str
    PROMPT_SENTIMENT_API_KEY: str
    OPEN_AI_API_KEY: str    
    
    model_config = SettingsConfigDict(
        env_file=Path(__file__).parent.parent / ".env",
        env_file_encoding="utf-8"
    )

    def get_db_url(self):
        return self.DATABASE_URL


    def get_sentiment_api_key(self):
        return self.PROMPT_SENTIMENT_API_KEY


    def get_openai_api_key(self):
        return self.OPEN_AI_API_KEY

        
settings = Settings()