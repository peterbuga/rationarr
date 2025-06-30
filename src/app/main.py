from fastapi import FastAPI, Response
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.api import api_router
from app.config import settings
from app.dependencies import SchedulerSessionDep
from app.scheduler import start_scheduler

app = FastAPI(
    title="Rationarr",
    description="API-only FastAPI app for scheduled data crawling from configured websites.",
    version="0.1.0",
    redirect_slashes=False,
)

app.include_router(api_router)


@app.on_event("startup")
async def startup_event():
    await start_scheduler()


def _debug_proxy():
    import httpx
    from starlette.background import BackgroundTask
    from starlette.requests import Request
    from starlette.responses import StreamingResponse

    client = httpx.AsyncClient(base_url="http://rationarr-web:5173/")

    async def _reverse_proxy(request: Request):
        url = httpx.URL(path=request.url.path, query=request.url.query.encode("utf-8"))
        rp_req = client.build_request(
            request.method,
            url,
            headers=request.headers.raw,
            content=request.stream(),
        )
        rp_resp = await client.send(rp_req, stream=True)
        return StreamingResponse(
            rp_resp.aiter_raw(),
            status_code=rp_resp.status_code,
            headers=rp_resp.headers,
            background=BackgroundTask(rp_resp.aclose),
        )

    app.add_route("/{path:path}", _reverse_proxy, ["GET", "POST"])

if settings.DEBUG:
    _debug_proxy()
else:
    # serve static files
    # app.mount("/", StaticFiles(directory="dist", html=True), name="dist")
    app.mount("/assets", StaticFiles(directory="dist/assets"), name="assets")

    @app.get("/")
    async def index():
        return FileResponse("dist/index.html")
        # return {"message": "Rationarr API is running."}


@app.get("/health")
async def root():
    return Response(content="OK", media_type="text/html")


# for testing
@app.get("/api/jobs")
async def get_jobs(scheduler: SchedulerSessionDep):
    jobs = scheduler.get_jobs()

    return {"scheduled_jobs": [job.id for job in jobs]}
