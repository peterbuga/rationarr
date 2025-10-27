import uuid

import httpx
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Indexer
from app.utils.cookie import cookie_str_to_dict, dict_to_cookie_str


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
        self.client = None
        self.headers = {}

    async def __aenter__(self):
        self.client = httpx.AsyncClient(
            headers=self.headers,
            timeout=15,
            cookies=(self.cookie or {}),
            follow_redirects=True,
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.client:
            await self.client.aclose()

    async def set_db_session(self, session: AsyncSession):
        self.db_session = session

    async def redeem_claim(self) -> None:
        pass

    async def extract_info(self) -> None:
        pass

    async def exchange_points(
        self, total_points: float, target_points: int
    ) -> None:
        pass

    async def save_cookies(self, cookies: str | dict) -> None:
        if isinstance(cookies, dict):
            cookies = dict_to_cookie_str(cookies)

        await self.db_session.execute(
            update(Indexer)
            .where(Indexer.id == self.indexer_id)
            .values(cookie=cookies)
        )
        await self.db_session.commit()
