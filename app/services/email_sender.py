"""Module for scheduler the email sender."""

from datetime import datetime

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from pytz import timezone

from app.core.config import settings
from app.persistence.repositories.email_sender import EmailSender


class ServiceEmailSender:
    def __init__(self, callback=None) -> None:
        self.scheduler = BackgroundScheduler()
        self.email_sender = EmailSender()
        self.timezone = timezone("America/Bogota")
        self.job_added = False
        self.callback = callback

    def send_email(self) -> tuple[bool, str]:
        """Envía un email y retorna estado y mensaje."""
        try:
            # Get the current date
            current_date = datetime.now(self.timezone).strftime("%Y-%m-%d")
            email_to = settings.email_to
            subject = f"Gestión diaria de clientes - {current_date}"

            success, message = self.email_sender.send_email(
                email_to=email_to, subject=subject
            )
            msg_status = f"message: {message} date: {current_date}"

            # Notify the result if there is callback
            if self.callback:
                self.callback(success, msg_status)

            return success, msg_status

        except Exception as e:
            msg = f"Error sending email: {e!s}"
            if self.callback:
                self.callback(False, msg)  # noqa: FBT003

            raise ValueError(msg) from e

    def __call__(self, immediate: bool = False) -> tuple[bool, str]:
        """Configura y ejecuta el scheduler de emails."""
        try:
            if not self.job_added:
                self.scheduler.add_job(
                    self.send_email,
                    trigger=CronTrigger(
                        hour=8,
                        minute=0,
                        timezone=self.timezone,
                    ),
                    id="send_email",
                )
                self.job_added = True

            # Run the scheduler
            if not self.scheduler.running:
                self.scheduler.start()

            # Start the scheduler
            if immediate:
                return self.send_email()

            return True, "Email sent successfully"
        except Exception as e:
            error_msg = f"Error in email scheduler: {e!s}"
            if self.callback:
                self.callback(False, error_msg)  # noqa: FBT003
            return False, error_msg
