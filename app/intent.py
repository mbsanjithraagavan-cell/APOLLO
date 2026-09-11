"""Booking extraction from sanitized user text; no direct side effects."""
from datetime import date, timedelta
from app.schemas import BookingIntent


def extract_booking_intent(text: str) -> BookingIntent:
    lowered = text.lower()
    specialty = None
    for terms, normalized in (("cardiology", "cardiologist"), ("dermatology", "dermatologist"),
                              ("orthopedics", "orthopedist"), ("pediatrics", "pediatrician")):
        if terms in lowered or normalized in lowered:
            specialty = terms
            break
    if not specialty:
        raise ValueError("Booking request lacks a supported specialty")
    target = date.today() + timedelta(days=1) if "tomorrow" in lowered else None
    return BookingIntent(specialty=specialty, date_from=target, date_to=target)
