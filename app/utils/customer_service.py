
from datetime import date, datetime, timezone


def calculate_days_remaining(
    next_contact_date_str: str
) -> date:
    days_remaining = None
    today = datetime.now(timezone.utc).date()

    if isinstance(next_contact_date_str, str):
        # Try to parse with or without the time/timezone part
        try:
            next_contact_dt_obj = datetime.fromisoformat(next_contact_date_str.replace('Z', '+00:00')).date()
        except ValueError:
            next_contact_dt_obj = date.fromisoformat(next_contact_date_str)
    elif isinstance(next_contact_date_str, date):
        next_contact_dt_obj = next_contact_date_str
    elif isinstance(next_contact_date_str, datetime):
        next_contact_dt_obj = next_contact_date_str.date()
    else:
        print(f"Advertencia: next_contact_date tiene un tipo inesperado: {type(next_contact_date_str)}")
        next_contact_dt_obj = None

    # Calculate the days remaining
    if next_contact_dt_obj:
        days_remaining = (next_contact_dt_obj - today).days
    return days_remaining
