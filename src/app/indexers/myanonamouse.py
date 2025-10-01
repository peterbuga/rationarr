import logging
import random
import time
import uuid

import httpx
from bs4 import BeautifulSoup
from slugify import slugify
from sqlalchemy import update

from app.indexers.base_indexer import BaseIndexer
from app.models import Scraper
from app.models.indexer import Indexer
from app.schemas.myanonamouse import MyanonamouseScraperFields
from app.utils.cookie import dict_to_cookie_str
from app.utils.url import build_url


class Myanonamouse(BaseIndexer):
    alias = "MAM"

    def __init__(self, id: uuid.UUID, **kwargs):
        super().__init__(id, **kwargs)

    async def extract_info(self):
        headers = {
            "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.5 Safari/605.1.15"
        }

        # TODO: check if cookie entry contains user id cookie
        cookie = {"mam_id": self.cookie}

        async with httpx.AsyncClient(
            headers=headers, cookies=self.cookie, timeout=15
        ) as client:
            homepage_url = build_url(host=self.url, path="index.php")
            response = await client.get(homepage_url)
            response.raise_for_status()

            mam_id = response.cookies.get("mam_id")
            if not mam_id:
                raise Exception("No MAM cookie.")

            # save latest cookies
            await self.db_session.execute(
                update(Indexer)
                .where(Indexer.id == self.indexer_id)
                .values(
                    cookie=dict_to_cookie_str(
                        response.cookies or client.cookies
                    )
                )
            )
            await self.db_session.commit()

            scrapers = []
            homepage_bs = BeautifulSoup(response.text, "html.parser")
            my_info = homepage_bs.find(
                "a", {"role": "menuitem", "class": "myInfo"}
            )

            points = homepage_bs.find("a", {"href": "/store.php"})
            user = homepage_bs.find("a", {"id": "userMenu"})

            connectable = homepage_bs.find("a", {"id": "tmCo"})
            if connectable:
                connectable = connectable.find("img")
                connectable = "true" if "yes" in connectable["src"] else "false"

            scrape_data = {
                "points": points.text.lower().replace("bonus:", "").strip(),
                "connectable": connectable,
                "user": user.text.split(" ")[0].strip(),
            }
            for key, value in scrape_data.items():
                scrapers.append(
                    Scraper(
                        **{
                            "indexer_id": self.indexer_id,
                            "attribute": getattr(
                                MyanonamouseScraperFields, key
                            ),
                            "value": value,
                        }
                    )
                )

            time.sleep(random.randint(2, 10))
            my_info_url = build_url(host=self.url, path=my_info["href"])
            response = await client.get(my_info_url)
            my_info_bs = BeautifulSoup(response.text, "html.parser")
            my_info = my_info_bs.find(
                "table", {"style": "width:100%;min-width:100%;max-width:100%;"}
            )
            infos = [
                [i.text for i in tr.find_all("td")]
                for tr in my_info.find_all("tr")
            ]

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

            self.db_session.add_all(scrapers)
            await self.db_session.commit()
