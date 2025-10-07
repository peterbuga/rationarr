from typing import Optional

from pydantic import HttpUrl, PostgresDsn
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URI: PostgresDsn
    DEBUG: bool = False
    PROWLARR_HOST: HttpUrl
    PROWLARR_APIKEY: str
    FLARESOULVERR_URL: Optional[HttpUrl] = None
    INTERVAL_SCRAPE: int = 2 * 3600


settings = Settings()
