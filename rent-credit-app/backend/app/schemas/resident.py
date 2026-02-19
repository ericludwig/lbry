from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime, date
from app.models.resident import EnrollmentStatus


class ResidentCreate(BaseModel):
    email: EmailStr
    first_name: str
    last_name: str
    phone: Optional[str] = None
    property_id: str
    unit_number: Optional[str] = None
    lease_start_date: date
    lease_end_date: Optional[date] = None
    monthly_rent_cents: int
    pms_resident_id: Optional[str] = None


class ResidentUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    ssn_last4: Optional[str] = None
    date_of_birth: Optional[date] = None
    lease_end_date: Optional[date] = None


class ResidentOut(BaseModel):
    id: str
    property_id: str
    email: str
    first_name: str
    last_name: str
    phone: Optional[str]
    unit_number: Optional[str]
    lease_start_date: date
    lease_end_date: Optional[date]
    monthly_rent_cents: int
    enrollment_status: EnrollmentStatus
    enrollment_date: Optional[datetime]
    trial_end_date: Optional[datetime]
    retroactive_reporting_consent: bool
    retroactive_months_requested: int
    created_at: datetime

    class Config:
        from_attributes = True


class ResidentSignup(BaseModel):
    """Resident self-signup to set password and confirm enrollment."""
    email: EmailStr
    password: str
    date_of_birth: Optional[date] = None
    ssn_last4: Optional[str] = None
    retroactive_reporting_consent: bool = False
    retroactive_months: int = 0


class OptOutRequest(BaseModel):
    reason: Optional[str] = None


class EnrollmentSummary(BaseModel):
    total_enrolled: int
    total_active: int
    total_opted_out: int
    total_trial: int
    monthly_revenue_cents: int
    monthly_pm_payout_cents: int
