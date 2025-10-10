import datetime
import logging
import random
import time
import urllib.parse

import httpx
from bs4 import BeautifulSoup
from sqlalchemy import update

from app.config import settings
from app.indexers.base_indexer import BaseIndexer
from app.models import Activity, Indexer, Scraper
from app.schemas.common import ScraperFields
from app.utils.cookie import cookie_str_to_dict, dict_to_cookie_str
from app.utils.url import build_url


class Hdspace(BaseIndexer):
    alias = "HDS"

    points_map = {
        600: {"value": "3", "desc": "1 GB upload"},
        1100: {"value": "4", "desc": "2 GB upload"},
        2700: {"value": "5", "desc": "5 GB upload"},
        5200: {"value": "6", "desc": "10 GB upload"},
        10000: {"value": "invite", "desc": "1 invite"},
        15000: {"value": "invite2", "desc": "2 invites"},
        20000: {"value": "invite3", "desc": "3 invites"},
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    async def exchange_points(self, total_points, target_points):
        exchange_points_url = build_url(
            host=self.url,
            path="seedbonus_exchange.php",
            query={"id": self.points_map[target_points]["value"]},
        )

        async with httpx.AsyncClient(timeout=60) as client:
            cookies_dict = cookie_str_to_dict(self.cookie)

            params = {"submit": "Exchange!"}
            response = await client.post(
                url=str(settings.FLARESOLVERR_URL),
                headers={"Content-Type": "application/json"},
                json={
                    "cmd": "request.post",
                    "url": exchange_points_url,
                    "session": self.type,
                    "postData": urllib.parse.urlencode(params),
                    "cookies": [
                        {"name": c[0], "value": c[1]}
                        for c in cookies_dict.items()
                    ],
                },
            )
            response.raise_for_status()
            solverr_data = response.json()

            # save latest cookies
            cookies = {
                cookie["name"]: cookie["value"]
                for cookie in solverr_data["solution"]["cookies"]
            }

            cookies_str = dict_to_cookie_str(cookies)
            await self.db_session.execute(
                update(Indexer)
                .where(Indexer.id == self.indexer_id)
                .values(cookie=cookies_str)
            )
            await self.db_session.commit()

        activity_data = Activity(
            **{
                "indexer_id": self.indexer_id,
                "activity": f"{target_points} bonus points exchanged for {self.points_map[target_points]['desc']}.",
            }
        )
        self.db_session.add(activity_data)
        await self.db_session.commit()

    async def extract_info(self):
        async with httpx.AsyncClient(timeout=60) as client:
            cookies_dict = cookie_str_to_dict(self.cookie)
            homepage_url = build_url(
                host=self.url,
                path="index.php",
                # go for control panel page if cookies present
                **(
                    {"query": {"page": "usercp", "uid": cookies_dict["uid"]}}
                    if self.cookie
                    else {}
                ),
            )
            login_url = build_url(
                host=self.url, path="index.php", query={"page": "login"}
            )

            response = await client.post(
                url=str(settings.FLARESOLVERR_URL),
                headers={"Content-Type": "application/json"},
                json={
                    "cmd": "request.get",
                    "url": homepage_url,
                    "session": self.type,
                }
                |
                # use cookies if present
                (
                    {
                        "cookies": [
                            {"name": c[0], "value": c[1]}
                            for c in cookies_dict.items()
                        ]
                    }
                    if self.cookie is not None
                    else {}
                ),
            )

            response.raise_for_status()
            flaresolverr_data = response.json()

            logged_page_bs = BeautifulSoup(
                flaresolverr_data["solution"]["response"], "html.parser"
            )
            logged_in = logged_page_bs.find("div", {"id": "menu"})

            if flaresolverr_data["status"] != "ok" or not logged_in:
                time.sleep(random.randint(2, 10))

                params = {"uid": self.username, "pwd": self.password}
                response = await client.post(
                    url=str(settings.FLARESOLVERR_URL),
                    headers={"Content-Type": "application/json"},
                    json={
                        "cmd": "request.post",
                        "url": login_url,
                        "session": self.type,
                        "postData": urllib.parse.urlencode(params),
                    },
                )
                response.raise_for_status()

                flaresolverr_data = response.json()
                if flaresolverr_data["status"] != "ok":
                    logging.error(
                        f"Failed to login/bypass cloudflare {self.name}"
                    )
                    return

                logged_page_bs = BeautifulSoup(
                    response.json()["solution"]["response"], "html.parser"
                )

            # save latest cookies
            cookies = {
                cookie["name"]: cookie["value"]
                for cookie in flaresolverr_data["solution"]["cookies"]
            }
            cookies_str = dict_to_cookie_str(cookies)

            await self.db_session.execute(
                update(Indexer)
                .where(Indexer.id == self.indexer_id)
                .values(cookie=cookies_str)
            )
            await self.db_session.commit()

            # collect data
            upload = (
                logged_page_bs.find("td", {"class": "green", "align": "center"})
                .text.split(":")[-1]
                .strip()
            )
            download = (
                logged_page_bs.find("td", {"class": "red", "align": "center"})
                .text.split(":")[-1]
                .strip()
            )
            ratio = (
                logged_page_bs.find(
                    "td", {"class": "yellow", "align": "center"}
                )
                .text.split(":")[-1]
                .strip()
            )
            ratio = ratio if "-" not in ratio else 0
            points = (
                logged_page_bs.find(
                    "a", {"href": "index.php?page=modules&module=seedbonus"}
                )
                .text.split(":")[-1]
                .strip()
            )
            seed_leech = logged_page_bs.find(
                "img", {"src": "images/actseed.png"}
            )
            seed = seed_leech.parent.find("font", {"color": "green"}).text
            leech = seed_leech.parent.find("font", {"color": "red"}).text

            freeleech = logged_page_bs.find(
                "font",
                {"color": "orange"},
            )
            if freeleech:
                freeleech = (
                    "false"
                    if freeleech.text.strip().lower() == "not active"
                    else "true"
                )

            join = logged_page_bs.find(
                "td",
                {"class": "header", "align": "left"},
                string=lambda text: text and "Joined on:" in text,
            )
            join_date = join.parent.find("td", {"class": "lista"})
            if join_date:
                join_date = join_date.text.strip().replace(",", "")
                join_date = str(
                    datetime.datetime.strptime(join_date, "%B %d %Y %H:%M:%S")
                )

            user_class = logged_page_bs.find(
                "td",
                {"style": "text-align:center;", "align": "center"},
                string=lambda text: text and "Rank:" in text,
            )
            if user_class:
                user_class = user_class.text.split(":")[-1].strip()

            user = logged_page_bs.find(
                "td",
                {"class": "header", "align": "left"},
                string=lambda text: text and "User:" in text,
            )
            user = user.parent.find("td", {"class": "lista"})
            if user:
                user = user.text.strip()

            posts = logged_page_bs.find(
                "td",
                {"class": "header", "align": "left"},
                string=lambda text: text and "Forum Posts:" in text,
            )
            posts = posts.parent.find("td", {"class": "lista"})
            if posts:
                posts = posts.text.split("[")[0].strip()

            last_access = logged_page_bs.find("font", {"color": "steelblue"})
            if last_access:
                last_access = str(
                    datetime.datetime.strptime(
                        last_access.text.strip(), "%d/%m/%Y %H:%M:%S"
                    )
                )

            scraped_data = {
                "user": user,
                "user_class": user_class,
                "upload": upload,
                "download": download,
                "ratio": ratio,
                "seed": seed,
                "leech": leech,
                "points": points,
                "join_date": join_date,
                "posts": posts,
                "freeleech": freeleech,
                "last_access": last_access,
            }

            # save data
            scrapers = []
            for attribute, value in scraped_data.items():
                scrapers.append(
                    Scraper(
                        **{
                            "indexer_id": self.indexer_id,
                            "attribute": getattr(ScraperFields, attribute),
                            "value": str(value),
                        }
                    )
                )

            self.db_session.add_all(scrapers)
            await self.db_session.commit()
