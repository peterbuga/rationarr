import copy
import logging
import random
import time

import pyotp
from bs4 import BeautifulSoup

from app.indexers.base_indexer import BaseIndexer
from app.models import Activity, Scraper
from app.schemas.unit3d import Unit3dScraperFields
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

    async def _login(self):
        if not self.username or not self.password:
            raise Exception("Missing login information")

        homepage_url = build_url(host=self.url)
        login_url = build_url(
            host=self.url,
            path="/login",
        )

        login_challenge_url = build_url(
            host=self.url, path="/two-factor-challenge"
        )

        response = await self.client.get(homepage_url)
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
            response = await self.client.post(login_url, data=post_data)
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
            response = await self.client.post(
                login_challenge_url, data=post_data
            )

            homepage_bs = BeautifulSoup(response.text, "html.parser")
            avatar = homepage_bs.find("img", {"alt": "My Profile"})
            if not avatar:
                raise Exception("Cannot login!")

    async def redeem_claim(self):
        await self._login()

        events_list_url = build_url(host=self.url, path="/events/")

        time.sleep(random.randint(2, 10))
        response = await self.client.get(events_list_url)
        events_list_bs = BeautifulSoup(response.text, "html.parser")
        events_list = events_list_bs.find("table", {"class": "data-table"})

        event_urls = [
            e.get("href")
            for e in events_list.find_all(
                "a", href=lambda href: href and "/events/" in href
            )
        ]

        remember_me = None
        for c in self.client.cookies:
            if "remember_web" in str(c):
                remember_me = str(c)

        new_cookies = dict(response.cookies)
        if remember_me:
            new_cookies[remember_me] = self.client.cookies.get(remember_me)

        await self.save_cookies(new_cookies)

        for event_url in event_urls:
            time.sleep(random.randint(2, 10))
            response = await self.client.get(event_url)
            event_page_bs = BeautifulSoup(response.text, "html.parser")
            claim_form = event_page_bs.select_one("ol.events__list form")

            if claim_form:
                claim_url = claim_form.get("action")
                token = claim_form.find("input", {"name": "_token"})
                headers = copy.deepcopy(self.headers)
                headers.update(
                    {
                        "Content-Type": "application/x-www-form-urlencoded",
                        "Referer": event_url,
                    }
                )

                logging.warning(f"claim POST info: {claim_url} - {token}")

                response = await self.client.post(
                    url=claim_url,
                    headers=headers,
                    data={"_token": token.get("value")},
                )
                response.raise_for_status()

                event_page_bs = BeautifulSoup(response.text, "html.parser")
                prizes = event_page_bs.select("li > i.events__prize-message")

                if prizes:
                    prize = prizes[-1].getText().strip()

                    activity_data = Activity(
                        **{
                            "indexer_id": self.indexer_id,
                            "activity": f"Claim redeemed for {prize}.",
                        }
                    )
                    logging.info(f"Claimed {prize}")
                    self.db_session.add(activity_data)
                    await self.db_session.commit()

    async def exchange_points(self, total_points, target_points):
        if not self.points_map.get(target_points):
            logging.warning(
                f"Indexer {self.name} has no points exchange mapping."
            )
            return

        await self._login()

        transactions_create_url = build_url(
            host=self.url, path=f"/users/{self.username}/transactions/create"
        )

        transactions_url = build_url(
            host=self.url, path=f"/users/{self.username}/transactions"
        )

        time.sleep(random.randint(2, 10))
        response = await self.client.get(transactions_create_url)
        transactions_create_bs = BeautifulSoup(response.text, "html.parser")
        transaction_token = transactions_create_bs.find(
            "input", {"type": "hidden", "name": "_token"}
        )

        time.sleep(random.randint(2, 10))
        post_data = {
            "_token": transaction_token["value"],
            "exchange": self.points_map[target_points]["value"],
        }
        response = await self.client.post(transactions_url, data=post_data)

        if "bonus exchange successful" in response.text.lower():
            activity_data = Activity(
                **{
                    "indexer_id": self.indexer_id,
                    "activity": f"{target_points} bonus points exchanged for {self.points_map[target_points]['desc']}.",
                }
            )
            self.db_session.add(activity_data)
            await self.db_session.commit()

        remember_me = None
        for c in self.client.cookies:
            if "remember_web" in str(c):
                remember_me = str(c)

        new_cookies = dict(response.cookies)
        if remember_me:
            new_cookies[remember_me] = self.client.cookies.get(remember_me)

        await self.save_cookies(new_cookies)

    async def extract_info(self):
        endpoint_url = build_url(
            host=self.url,
            path="/api/user",
            query={"api_token": self.api_key},
        )
        response = await self.client.get(endpoint_url, timeout=10)
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
