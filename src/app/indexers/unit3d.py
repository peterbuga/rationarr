import logging
import random
import time

import httpx
import pyotp
from bs4 import BeautifulSoup
from sqlalchemy import update

from app.indexers.base_indexer import BaseIndexer
from app.models import Activity, Indexer, Scraper
from app.schemas.unit3d import Unit3dScraperFields
from app.utils.cookie import dict_to_cookie_str
from app.utils.url import build_url


class Unit3d(BaseIndexer):
    name = "Unit3d [generic]"
    api_key = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.api_key = self.api_key or kwargs["api_key"]
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
        if not self.points_map.get(target_points):
            logging.warning(
                f"Indexer {self.name} has no points exchange mapping."
            )
            return

        homepage_url = build_url(host=self.url)
        login_url = build_url(
            host=self.url,
            path="/login",
        )

        login_challenge_url = build_url(
            host=self.url, path="/two-factor-challenge"
        )

        transactions_create_url = build_url(
            host=self.url, path=f"/users/{self.username}/transactions/create"
        )

        transactions_url = build_url(
            host=self.url, path=f"/users/{self.username}/transactions"
        )

        async with httpx.AsyncClient(
            headers=self.headers,
            timeout=10,
            cookies=(self.cookie or {}),
            follow_redirects=True,
        ) as client:
            response = await client.get(homepage_url)
            response.raise_for_status()

            login_page_bs = BeautifulSoup(response.text, "html.parser")
            avatar = login_page_bs.find("img", {"alt": "My Profile"})

            if not avatar:
                # login flow
                inputs = login_page_bs.find_all("input")

                post_data = {}
                for input in inputs:
                    if input.get("name"):
                        post_data[input["name"]] = input.get("value")

                post_data["username"] = self.username
                post_data["password"] = self.password
                post_data["remember"] = "on"

                time.sleep(random.randint(2, 10))
                response = await client.post(login_url, data=post_data)
                login_challenge_page_bs = BeautifulSoup(
                    response.text, "html.parser"
                )
                inputs = login_challenge_page_bs.find_all("input")

                post_data = {}
                for input in inputs:
                    if input.get("name"):
                        post_data[input["name"]] = input.get("value")

                totp = pyotp.TOTP(self.mfa_key)
                post_data["code"] = totp.now()
                post_data["recovery_code"] = ""

                time.sleep(random.randint(2, 10))
                response = await client.post(
                    login_challenge_url, data=post_data
                )

                homepage_bs = BeautifulSoup(response.text, "html.parser")
                avatar = homepage_bs.find("img", {"alt": "My Profile"})
                if not avatar:
                    raise Exception("Cannot login!")

            time.sleep(random.randint(2, 10))
            response = await client.get(transactions_create_url)
            transactions_create_bs = BeautifulSoup(response.text, "html.parser")
            transaction_token = transactions_create_bs.find(
                "input", {"type": "hidden", "name": "_token"}
            )

            time.sleep(random.randint(2, 10))
            post_data = {
                "_token": transaction_token["value"],
                "exchange": self.points_map[target_points]["value"],
            }
            response = await client.post(transactions_url, data=post_data)

            if "Bonus Exchange Successful" in response.text:
                activity_data = Activity(
                    **{
                        "indexer_id": self.indexer_id,
                        "activity": f"{target_points} bonus points exchanged for {self.points_map[target_points]['desc']}.",
                    }
                )
                self.db_session.add(activity_data)
                await self.db_session.commit()

            remember_me = None
            for c in client.cookies:
                if "remember_web" in str(c):
                    remember_me = str(c)

            new_cookies = dict(response.cookies)
            if remember_me:
                new_cookies[remember_me] = client.cookies.get(remember_me)

            new_cookies = dict_to_cookie_str(new_cookies)

        await self.db_session.execute(
            update(Indexer)
            .where(Indexer.id == self.indexer_id)
            .values(cookie=new_cookies)
        )
        await self.db_session.commit()

    async def extract_info(self):
        async with httpx.AsyncClient() as client:
            endpoint_url = build_url(
                host=self.url,
                path="/api/user",
                query={"api_token": self.api_key},
            )
            response = await client.get(endpoint_url, timeout=10)
            response.raise_for_status()

            scrapers = []
            for attribute, value in response.json().items():
                if attribute in Unit3dScraperFields.get_keys():
                    scrapers.append(
                        Scraper(
                            **{
                                "indexer_id": self.indexer_id,
                                "attribute": getattr(
                                    Unit3dScraperFields, attribute
                                ),
                                "value": str(value),
                            }
                        )
                    )
                else:
                    logging.debug(f"Field not tracked: {attribute} = {value}")

            self.db_session.add_all(scrapers)
            await self.db_session.commit()
