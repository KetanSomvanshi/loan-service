import json

from fastapi import FastAPI, Depends, Request
import uvicorn
from controller import status, user_controller, loan_controller
from controller.context_manager import context_set_db_session_rollback, context_log_meta
from logger import logger
from models.base import GenericResponseModel
from server.auth import authenticate_token
from utils.exceptions import AppException
from utils.helper import build_api_response

app = FastAPI()

#  register routers here and add dependency on authenticate_token if token based authentication is required
app.include_router(status.router)
app.include_router(user_controller.user_router)
app.include_router(loan_controller.loan_router, dependencies=[Depends(authenticate_token)])


@app.exception_handler(AppException)
async def application_exception_handler(request, exc):
    context_set_db_session_rollback.set(True)
    logger.error(extra=context_log_meta.get(),
                 msg=f"application exception occurred error: {json.loads(str(exc))}")
    return build_api_response(GenericResponseModel(status_code=exc.status_code,
                                                   error=exc.message))


# register event handlers here
@app.on_event("startup")
async def startup_event():
    logger.info("Startup Event Triggered")


@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutdown Event Triggered")


if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=9999, reload=True)
