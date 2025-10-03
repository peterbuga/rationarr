import logging
import os

from fastapi import FastAPI, Request
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.api import api_router
from app.config import settings
from app.scheduler import start_scheduler

app = FastAPI(
    title="Rationarr",
    description="API-only FastAPI app for scheduled data crawling from configured websites.",
    version="0.1.0",
    redirect_slashes=False,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

app.include_router(api_router)


# disable successful health checks
block_endpoints = ["/api/health"]


class LogFilter(logging.Filter):
    def filter(self, record):
        if record.args and len(record.args) >= 4:
            if record.args[2] in block_endpoints and record.args[4] == "200":
                return False
        return True


uvicorn_logger = logging.getLogger("uvicorn.access")
uvicorn_logger.addFilter(LogFilter())


# @TODO move scheduler externally
# quirk to run in only 1 uvicorn worker and not execute multiple same-jobs
def is_primary_worker() -> bool:
    pid = os.getpid()
    parent_pid = os.getppid()
    children = []

    for entry in os.listdir("/proc"):
        if entry.isdigit():
            try:
                with open(f"/proc/{entry}/stat") as f:
                    data = f.read().split()
                    ppid = int(data[3])
                    if ppid == parent_pid:
                        children.append(int(entry))
            except Exception:
                continue

    return pid == max(children)


@app.on_event("startup")
async def startup_event():
    if is_primary_worker():
        await start_scheduler()


if settings.DEBUG:

    @app.get("/")
    async def index_debug():
        return {"message": "Rationarr API is running in debug mode."}

else:
    # serve static files
    # app.mount("/", StaticFiles(directory="dist", html=True), name="dist")

    @app.get("/")
    async def index():
        return FileResponse("dist/index.html")

    file_routes = ["_next", "static"]
    for file_route in file_routes:
        app.mount(
            f"/{file_route}",
            StaticFiles(directory=f"dist/{file_route}"),
            name=file_route,
        )

    def create_endpoint(route_name: str):
        async def endpoint(request: Request):
            return FileResponse(
                f"dist/{route_name}{".html" if not os.path.splitext(route_name)[1] else "" }"
            )

        return endpoint

    path_routes = ["index", "indexers", "activities"]
    for path_route in path_routes:
        app.add_api_route(
            f"/{path_route}",
            create_endpoint(path_route),
            methods=["GET", "POST"],
        )
        app.add_api_route(
            f"/{path_route}.txt",
            create_endpoint(f"{path_route}.txt"),
            methods=["GET"],
        )


# import os
# from typing import Tuple

# from fastapi import FastAPI
# from fastapi.staticfiles import StaticFiles

# app = FastAPI()


# class SinglePageApplication(StaticFiles):
#     """Acts similar to the bripkens/connect-history-api-fallback
#     NPM package."""

#     def __init__(self, directory: os.PathLike, index='index.html') -> None:
#         self.index = index

#         # set html=True to resolve the index even when no
#         # the base path is passed in
#         super().__init__(directory=directory, packages=None, html=True, check_dir=True)

#     async def lookup_path(self, path: str) -> Tuple[str, os.stat_result]:
#         """Returns the index file when no match is found.

#         Args:
#             path (str): Resource path.

#         Returns:
#             [tuple[str, os.stat_result]]: Always retuens a full path and stat result.
#         """
#         full_path, stat_result = await super().lookup_path(path)

#         # if a file cannot be found
#         if stat_result is None:
#             return await super().lookup_path(self.index)

#         return (full_path, stat_result)


# app.mount(
#     path='/',
#     app=SinglePageApplication(directory='path/to/dist'),
#     name='SPA'
# )
