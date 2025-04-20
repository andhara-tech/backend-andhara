import platform
import socket
import time
from datetime import UTC, datetime

import psutil
from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api import (
    authentication,
    customer,
    product,
)
from app.core.config import settings

# Init the entry point of the app
app = FastAPI(
    title=settings.app_name,
    description="Andhara Backend for managing products and customers",
    version="1.0.0",
)

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


# calculate the up time
start_time = time.time()


@app.get("/", status_code=status.HTTP_200_OK, tags=["System"])
def get_system_info() -> JSONResponse:
    """
    Get the system information.

    Returns:
        JSONResponse: The system information.

    """
    up_time = int(time.time() - start_time)

    # format the up time
    days, remainder = divmod(up_time, 86400)
    hour, remainder = divmod(remainder, 3600)
    minutes, seconds = divmod(remainder, 60)

    uptime = f"{days}d {hour}h {minutes}m {seconds}s"

    # system info
    return {
        "api_version": app.version,
        "status": "activate",
        "server_time": datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S"),
        "up_time": uptime,
        "hostname": socket.gethostname(),
        "system": {
            "os": platform.system(),
            "python_version": platform.python_version(),
            "cpu_usage": f"{psutil.cpu_percent()}%",
            "memory_usage": f"{psutil.virtual_memory().percent}%",
        },
        "dependencies": {
            "database": "supabase",
            "database_status": "connected",
            "cache": "connected",
            "external_apis": {},
        },
        "support_contact": {
            "email": "devaul.fs@gmail.com",
            "docs_url": "https://backend-andhara.onrender.com/docs",
        },
    }
