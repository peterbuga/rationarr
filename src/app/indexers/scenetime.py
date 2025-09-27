import logging
import time
import uuid

import httpx
from bs4 import BeautifulSoup
from slugify import slugify
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.indexers.base_indexer import BaseIndexer
from app.models import Scraper
from app.models.indexer import Indexer
from app.schemas.scenetime import ScenetimeScraperFields
from app.utils.cookie import cookie_str_to_dict, dict_to_cookie_str
from app.utils.url import build_url


class Scenetime(BaseIndexer):
    alias = "ST"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cookies = kwargs["cookie"]

    async def extract_info(self, session: AsyncSession):
        headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Cache-Control": "no-cache",
            "Pragma": "no-cache",
            "Priority": "u=0, i",
            "Referer": self.url,
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.6 Safari/605.1.15",
        }

        cookies = cookie_str_to_dict(self.cookies)

        async with httpx.AsyncClient(
            headers=headers, timeout=10, cookies=cookies
        ) as client:
            # get the user details page
            user_details_url = build_url(
                host=self.url,
                path="userdetails.php",
                query={"id": cookies["uid"]},
            )
            response = await client.get(user_details_url)
            response.raise_for_status()

            new_cookies = dict_to_cookie_str(dict(client.cookies))
            await session.execute(
                update(Indexer)
                .where(Indexer.id == self.indexer_id)
                .values(cookie=new_cookies)
            )
            await session.commit()

            scrapers = []
            user_details_bs = BeautifulSoup(response.text, "html.parser")
            user = user_details_bs.find("h2")
            my_info = user_details_bs.find("table", {"class": "desc-table"})

            infos = [
                [i.text for i in tr.find_all("td")]
                for tr in my_info.find_all("tr")
            ]
            infos.append(["user", user.text])

            for info in infos:
                attribute, value, *_ = [i.strip() for i in info] + [None] * (
                    2 - len(info)
                )
                attribute = slugify(attribute, separator="_").replace(
                    "class", "class_"
                )

                if attribute in ScenetimeScraperFields.get_keys():
                    scrapers.append(
                        Scraper(
                            **{
                                "indexer_id": self.indexer_id,
                                "attribute": getattr(
                                    ScenetimeScraperFields, attribute
                                ),
                                "value": str(value),
                            }
                        )
                    )
                else:
                    logging.debug(f"Field not tracked: {attribute} = {value}")

            session.add_all(scrapers)
            await session.commit()
