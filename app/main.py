from datetime import datetime

from fastapi import FastAPI
from fastapi.responses import JSONResponse

from app.core.config import settings

# Init the entry point of the app
app = FastAPI()


@app.get("/")
def entry_point():
    time = datetime.now().strftime("%d-%m-%Y")
    return JSONResponse(
        status_code=200,
        content={
            "status": "working...",
            "time": time,
            "version": settings.VERSION,
            "author": settings.AUTHOR,
        },
    )
