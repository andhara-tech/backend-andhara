"""Module to manage the email sender."""

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from app.core.config import settings
from app.utils.email_sender import get_email_body


class EmailSender:
    def __init__(self) -> None:
        self.email_host = "smtp.gmail.com"
        self.email_port = 587
        self.email_username = settings.email_username
        self.email_password = settings.email_password

    def get_email_body(self) -> str:
        clients = [
            ("John Doe", "123456789"),
            ("Jane Doe", "987654321"),
        ]
        return get_email_body(clients)

    def send_email(self, email_to: str, subject: str) -> tuple[bool, str]:
        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = self.email_username
            msg["To"] = email_to

            # Attach the HTML content to the email
            part = MIMEText(self.get_email_body(), "html")
            msg.attach(part)

            with smtplib.SMTP(self.email_host, self.email_port) as server:
                server.starttls()
                server.login(self.email_username, self.email_password)
                server.sendmail(self.email_username, email_to, msg.as_string())
            return True, "Email sent successfully"
        except Exception as e:
            error_msg = f"Error sending email: {e!s}"
            return False, error_msg
