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
    customer_service,
    product,
    purchase,
)
from app.core.config import settings
from app.core.scheduler_status import SchedulerState
from app.services.email_sender import ServiceEmailSender

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
app.include_router(purchase.purchase_router, prefix="/v1")
app.include_router(customer_service.router, prefix="/v1")


# Instance the scheduler state
scheduler_status = SchedulerState()


# Function to update the global variable
def update_shcheduler_status(success: bool, message: str) -> None:
    scheduler_status.success = success
    scheduler_status.message = message


@app.on_event("startup")
async def startup_event() -> None:
    try:
        # Instance the scheduler for sending the email
        email_service = ServiceEmailSender(callback=update_shcheduler_status)
        shcheduler_success, msg = email_service(immediate=False)
        # Show the message when the scheduler fails
        if not shcheduler_success:
            raise ValueError(msg)

    except Exception as e:
        update_shcheduler_status(False, str(e))  # noqa: FBT003
        raise ValueError(e) from e


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
            "scheduler": scheduler_status.success,
            "scheduler_message": scheduler_status.message,
            "external_apis": {},
        },
        "support_contact": {
            "email": "devaul.fs@gmail.com",
            "docs_url": "https://backend-andhara.onrender.com/docs",
        },
    }
