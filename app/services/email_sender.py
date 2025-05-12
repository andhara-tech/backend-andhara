"""Module for scheduler the email sender."""

from datetime import datetime

from pytz import timezone

from app.core.config import settings
from app.persistence.repositories.email_sender import EmailSender


class ServiceEmailSender:
    def __init__(self) -> None:
        self.email_sender = EmailSender()
        self.timezone = timezone("America/Bogota")

    def send_email(self) -> tuple[bool, str]:
        try:
            # Get the current date
            current_date = datetime.now(self.timezone).strftime("%Y-%m-%d")
            email_to = settings.email_to
            subject = f"Gestión diaria de clientes - {current_date}"

            success, message = self.email_sender.send_email(
                email_to=email_to, subject=subject
            )
            return success, message or "Email sent successfully"
        except Exception as e:
            return False, f"Error sending email: {e!s}"
