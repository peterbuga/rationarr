import logging
import time
import uuid

import httpx
from bs4 import BeautifulSoup
from slugify import slugify
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from app.indexers.base_indexer import BaseIndexer
from app.models import Scraper
from app.models.indexer import Indexer
from app.schemas.myanonamouse import MyanonamouseScraperFields


class Myanonamouse(BaseIndexer):
    alias = "MAM"

    def __init__(self, id: uuid.UUID, **kwargs):
        super().__init__(id, **kwargs)
        self.cookie = kwargs["cookie"]

    async def extract_info(self, session: AsyncSession):
        headers = {
            "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.5 Safari/605.1.15"
        }

        # TODO: check if cookie entry contains user id cookie
        cookie = {"mam_id": self.cookie}

        async with httpx.AsyncClient(
            headers=headers, cookies=cookie, timeout=10
        ) as client:
            response = await client.get(f"{self.url}/index.php")
            response.raise_for_status()
            mam_id = response.cookies.get("mam_id")
            if not mam_id:
                raise Exception("No MAM cookie.")

            await session.execute(
                update(Indexer)
                .where(Indexer.id == self.indexer_id)
                .values(cookie=mam_id)
            )
            await session.commit()

            scrapers = []
            homepage_bs = BeautifulSoup(response.text, "html.parser")
            my_info = homepage_bs.find(
                "a", {"role": "menuitem", "class": "myInfo"}
            )

            points = homepage_bs.find("a", {"href": "/store.php"})
            scrapers.append(
                Scraper(
                    **{
                        "indexer_id": self.indexer_id,
                        "attribute": getattr(MyanonamouseScraperFields, "points"),
                        "value": points.text.lower()
                        .replace("bonus:", "")
                        .strip(),
                    }
                )
            )

            time.sleep(10)
            response = await client.get(f"{self.url}{my_info['href']}")
            my_info_bs = BeautifulSoup(response.text, "html.parser")
            my_info = my_info_bs.find(
                "table", {"style": "width:100%;min-width:100%;max-width:100%;"}
            )
            infos = [
                [i.text for i in tr.find_all("td")]
                for tr in my_info.find_all("tr")
            ]
            # logging.warning(f"tds {results}")

            for info in infos:
                attribute, value = [i.strip() for i in info] + [None] * (
                    2 - len(info)
                )
                attribute = slugify(attribute, separator="_").replace(
                    "class", "class_"
                )

                if attribute in MyanonamouseScraperFields.get_keys():
                    scrapers.append(
                        Scraper(
                            **{
                                "indexer_id": self.indexer_id,
                                "attribute": getattr(
                                    MyanonamouseScraperFields, attribute
                                ),
                                "value": str(value),
                            }
                        )
                    )
                else:
                    logging.debug(f"Field not tracked: {attribute} = {value}")

            session.add_all(scrapers)
            await session.commit()
