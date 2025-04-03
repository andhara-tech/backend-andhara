from datetime import datetime

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api import authentication

# Init the entry point of the app
app = FastAPI(
    title="ANDHARA BACKEND FOR MANAGE THE SYSTEM"
)

# Config the cors
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(authentication.router)


@app.get("/")
def entry_point():
    time = datetime.now().strftime("%d-%m-%Y")
    return JSONResponse(
        status_code=200,
        content={
            "status": "working...",
            "time": time,
            "version": settings.project_version,
            "author": settings.project_author,
        },
    )
