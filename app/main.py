from datetime import datetime

from fastapi import FastAPI
from fastapi.responses import JSONResponse


# Init the entry point of the app
app = FastAPI()


@app.get("/")
def entry_point():
    time = datetime.now()
    return JSONResponse(
        status_code=200,
        content={
            "status": "working...",
            "time": time.strftime("%d-%m-%Y"),
            "andhara_version": "0.0.3",
        },
    )
