from typing import Optional

from pydantic import BaseModel, HttpUrl


class IndexerOutputModel(BaseModel):
    name: str
    alias: Optional[str] = None
    url: Optional[HttpUrl] = None

    class Config:
        from_attributes = True
