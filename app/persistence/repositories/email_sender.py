"""Module to manage the email sender."""

import smtplib
from datetime import datetime, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from pytz import timezone

from app.core.config import settings
from app.models.email_sender import Normalized
from app.persistence.db.connection import get_supabase
from app.utils.email_sender import customer_service_query, get_email_body


class EmailSender:
    def __init__(self) -> None:
        # Initialize Supabase
        self.supabase = get_supabase()
        # Email configuration
        self.email_host = "smtp.gmail.com"
        self.email_port = 587
        self.email_username = settings.email_username
        self.email_password = settings.email_password
        # Date configuration
        self.timezone = timezone("America/Bogota")

    def get_daily_customers(self) -> list[Normalized]:
        try:
            # Get the current date
            current_date = datetime.now(self.timezone).date()
            customer_service_response = (
                self.supabase.table("customer_service")
                .select(customer_service_query)
                .gte("next_contact_date", current_date)
                .lte("next_contact_date", current_date + timedelta(days=1))
                .execute()
            )
            data: list[dict] = customer_service_response.data
            if not data:
                return []  # Return the empty list if there is not data
            customers_normalized = []
            for item in data:
                purchase = item.get("purchase", {})
                customer = purchase.get("customer", {})

                current_customer = {
                    "customer_service_status": item.get(
                        "customer_service_status"
                    ),
                    "customer_document": customer.get("customer_document"),
                    "customer_name": " ".join(
                        filter(
                            None,
                            [
                                customer.get("customer_first_name"),
                                customer.get("customer_last_name"),
                            ],
                        )
                    ),
                    "phone_number": customer.get("phone_number"),
                    "service_date": item.get("service_date"),
                    "purchase_duration": purchase.get("purchase_duration"),
                    "purchase_date": purchase.get("purchase_date"),
                }
                customers_normalized.append(current_customer)
            # Return the normalized data
            return customers_normalized
        except Exception as e:
            return f"Error getting daily customers: {e!s}"

    def get_email_body(self) -> str:
        """Get the email body."""
        customers: Normalized = self.get_daily_customers()
        # Pass the customer data to the function
        return get_email_body(customers)

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
