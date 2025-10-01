from pydantic import HttpUrl, PostgresDsn
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URI: PostgresDsn
    DEBUG: bool = False
    PROWLARR_HOST: HttpUrl
    PROWLARR_APIKEY: str
    FLARESOULVERR_URL: str = None
    INTERVAL_SCRAPE: int = 3600


settings = Settings()
