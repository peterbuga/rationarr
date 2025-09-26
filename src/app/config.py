from pydantic import HttpUrl, PostgresDsn
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URI: PostgresDsn
    DEBUG: bool = False
    PROWLARR_HOST: HttpUrl
    PROWLARR_APIKEY: str


settings = Settings()
