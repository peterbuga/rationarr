import uuid

from sqlalchemy.ext.asyncio import AsyncSession


class BaseIndexer:
    url = None
    name = None
    alias = None

    def __init__(self, id: uuid.UUID, url: str, **kwargs):
        self.indexer_id = id
        self.url = url.strip("/")

    async def extract_info(self, session: AsyncSession):
        pass
