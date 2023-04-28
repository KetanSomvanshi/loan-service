import http

from fastapi import APIRouter
from fastapi.responses import JSONResponse

router = APIRouter(tags=["health_checks", "status"])


#  health check endpoints
@router.get("/status", status_code=http.HTTPStatus.OK)
async def status_check():
    return JSONResponse(status_code=http.HTTPStatus.OK, content={"status": "OK"})
