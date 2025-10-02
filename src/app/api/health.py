from fastapi import APIRouter, Response
from sqlalchemy import literal, select

from app.dependencies import DbSessionDep

router = APIRouter()


@router.get("")
async def get_health(db: DbSessionDep):
    stmt = select(literal(1))
    try:
        result = await db.execute(stmt)
        res = result.scalar()
    except Exception as e:
        print(e)
        res = False

    return Response(
        content=("OK" if res else "DB ERROR"),
        media_type="text/html",
        status_code=(200 if res else 500),
    )
