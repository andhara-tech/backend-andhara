from datetime import datetime, timezone

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api import (
    authentication,
    customer,
    product,
)
from app.core.config import settings

# Init the entry point of the app
app = FastAPI(title="ANDHARA BACKEND FOR MANAGEMENT")

# Config the cors
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.allowed_cors],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(authentication.router, prefix="/v1")
app.include_router(product.router, prefix="/v1")
app.include_router(customer.router, prefix="/v1")


@app.get("/")
def entry_point() -> JSONResponse:
    time = datetime.now(timezone.UTC).strftime("%d-%m-%Y")
    return JSONResponse(
        status_code=200,
        content={
            "status": "working...",
            "time": time,
            "version": settings.project_version,
            "author": settings.project_author,
        },
    )
