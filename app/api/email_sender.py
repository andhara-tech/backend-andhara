"""Module to manage the email sender."""

from fastapi import APIRouter, status
from fastapi.exceptions import HTTPException
from fastapi.responses import JSONResponse

from app.services.email_sender import ServiceEmailSender

# Instance the email sender router
email_sender_router = APIRouter(
    prefix="/email-sender",
    tags=["Email Sender"],
    responses={
        404: {"description": "Not found, please contact the admin"},
    },
)

# Instance the service class using the singleton pattern
service = ServiceEmailSender()


# Create the endpoint
@email_sender_router.post("/send-email", status_code=status.HTTP_200_OK)
async def send_daily_email() -> JSONResponse:
    try:
        for _ in range(3):
            success, status_response = service.send_email()
            if success:
                return JSONResponse(
                    content={"success": success, "message": status_response},
                    status_code=status.HTTP_200_OK,
                )

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=status_response,
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        ) from e
