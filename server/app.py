from fastapi import FastAPI, Depends, Request
import uvicorn
from controller import status, user_controller
from logger import logger

app = FastAPI()

#  register routers here and add dependency on authenticate_token if token based authentication is required
app.include_router(status.router)
app.include_router(user_controller.user_router)


# register event handlers here
@app.on_event("startup")
async def startup_event():
    logger.info("Startup Event Triggered")


@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutdown Event Triggered")


if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=9999, reload=True)
