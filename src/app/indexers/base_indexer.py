import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.utils.cookie import cookie_str_to_dict


class BaseIndexer:
    url = None
    name = None
    alias = None
    points_map = {}

    def __init__(self, id: uuid.UUID, url: str, **kwargs):
        self.indexer_id = id
        self.url = url.strip("/")
        self.db_session = None
        self.cookie = (
            cookie_str_to_dict(kwargs["cookie"]) if kwargs["cookie"] else None
        )
        self.name = kwargs["name"]
        self.type = kwargs["type"]
        self.username = kwargs["username"]
        self.password = kwargs["password"]
        self.mfa_key = kwargs["mfa_key"]

    async def set_db_session(self, session: AsyncSession):
        self.db_session = session

    async def extract_info(self) -> None:
        pass

    async def exchange_points(
        self, total_points: float, target_points: int
    ) -> None:
        pass
