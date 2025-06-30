import logging
import uuid

import httpx
from sqlalchemy.ext.asyncio import AsyncSession

from app.indexers.base_indexer import BaseIndexer
from app.models.scraper import Scraper
from app.schemas.unit3d import Unit3dScraperFields


class Unit3d(BaseIndexer):
    name = "Unit3d [generic]"
    api_key = None

    def __init__(self, id: uuid.UUID, **kwargs):
        super().__init__(id, **kwargs)
        self.api_key = self.api_key or kwargs["api_key"]

    async def extract_info(self, session: AsyncSession):
        async with httpx.AsyncClient() as client:
            endpoint_url = f"{self.url}/api/user?api_token={self.api_key}"
            response = await client.get(endpoint_url, timeout=10)
            response.raise_for_status()
            # logging.debug(f"{self.url} crawled {response.text}")

            scrapers = []
            for attribute, value in response.json().items():
                if attribute in Unit3dScraperFields.get_keys():
                    scrapers.append(
                        Scraper(
                            **{
                                "tracker_id": self.tracker_id,
                                "attribute": getattr(Unit3dScraperFields, attribute),
                                "value": str(value),
                            }
                        )
                    )
                else:
                    logging.debug(f"Field not tracked: {attribute} = {value}")

            session.add_all(scrapers)
            await session.commit()
