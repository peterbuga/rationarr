import logging

import httpx

from app.config import settings


async def flarsolverr_destroy_session(session_name: str):
    if not settings.FLARESOLVERR_URL:
        logging.debug("FlareSolverr not setup.")
        return

    async with httpx.AsyncClient(timeout=60) as client:
        try:
            res = await client.post(
                url=str(settings.FLARESOLVERR_URL),
                headers={"Content-Type": "application/json"},
                json={
                    "cmd": "sessions.list",
                },
            )

            res_data = res.json()
            if (
                res_data["status"] == "ok"
                and session_name in res_data["sessions"]
            ):
                res = await client.post(
                    url=str(settings.FLARESOLVERR_URL),
                    headers={"Content-Type": "application/json"},
                    json={"cmd": "sessions.destroy", "session": session_name},
                )
        except Exception as e:
            logging.error(f"Failed to destroy FlareSolverr session: {e}")
