from pydantic import BaseModel
from typing import Optional
from datetime import datetime, date
from app.models.rent_payment import PaymentStatus, ReportingStatus


class RentPaymentOut(BaseModel):
    id: str
    resident_id: str
    payment_period_start: date
    payment_period_end: date
    due_date: date
    paid_date: Optional[date]
    amount_due_cents: int
    amount_paid_cents: Optional[int]
    payment_status: PaymentStatus
    reporting_status: ReportingStatus
    reported_at: Optional[datetime]
    is_retroactive: bool
    created_at: datetime

    class Config:
        from_attributes = True


class PaymentHistoryItem(BaseModel):
    period: str  # "January 2024"
    due_date: date
    paid_date: Optional[date]
    amount_cents: int
    payment_status: PaymentStatus
    reporting_status: ReportingStatus
    bureaus_reported: list[str]
