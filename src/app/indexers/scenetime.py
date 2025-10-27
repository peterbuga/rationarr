import logging

from bs4 import BeautifulSoup
from slugify import slugify

from app.indexers.base_indexer import BaseIndexer
from app.models import Activity, Scraper
from app.schemas.scenetime import ScenetimeScraperFields
from app.utils.url import build_url


class Scenetime(BaseIndexer):
    alias = "ST"
    points_map = {
        100: {"value": "1", "desc": "1 GB upload"},
        200: {"value": "2", "desc": "2.5 GB upload"},
        350: {"value": "3", "desc": "5 GB upload"},  # not confirmed
        500: {"value": "4", "desc": "custom title"},  # not confirmed
        # 2000: "1 invite",
        # 3000: "50 GB upload",
        # 5800: "100 GB upload",
        # 14000: "250 GB upload",
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Cache-Control": "no-cache",
            "Pragma": "no-cache",
            "Priority": "u=0, i",
            "Referer": self.url,
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.6 Safari/605.1.15",
        }

    async def exchange_points(self, total_points, target_points):
        exchange_points_url = build_url(
            host=self.url,
            path="global_API.php",
        )

        self.headers.update(
            {
                "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                "X-Requested-With": "XMLHttpRequest",
                "Origin": self.url,
                "Referer": build_url(host=self.url, path="mybonus.php"),
            }
        )

        post_data = {
            "opt": self.points_map[target_points]["value"],
            "type": "bpxch",
        }
        response = await self.client.post(exchange_points_url, data=post_data)
        response.raise_for_status()

        # TODO check for valid response
        await self.save_cookies(dict(self.client.cookies))

        activity_data = Activity(
            **{
                "indexer_id": self.indexer_id,
                "activity": f"{target_points} bonus points exchanged for {self.points_map[target_points]['desc']}.",
            }
        )
        self.db_session.add(activity_data)
        await self.db_session.commit()

    async def extract_info(self):
        # get the user details page
        user_details_url = build_url(
            host=self.url,
            path="userdetails.php",
            query={"id": self.cookie["uid"]},
        )
        response = await self.client.get(user_details_url)
        response.raise_for_status()

        await self.save_cookies(dict(self.client.cookies))

        scrapers = []
        user_details_bs = BeautifulSoup(response.text, "html.parser")
        user = user_details_bs.find("h2")
        my_info = user_details_bs.find("table", {"class": "desc-table"})

        infos = [
            [i.text for i in tr.find_all("td")] for tr in my_info.find_all("tr")
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

        self.db_session.add_all(scrapers)
        await self.db_session.commit()
