import uuid
from datetime import datetime, date
from sqlalchemy import String, Boolean, DateTime, Date, Integer, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base
import enum


class EnrollmentStatus(str, enum.Enum):
    pending = "pending"           # Lease added, awaiting enrollment delay
    trial = "trial"               # In free trial period
    active = "active"             # Subscribed and reporting
    opted_out = "opted_out"       # Resident cancelled
    payment_failed = "payment_failed"


class Resident(Base):
    __tablename__ = "residents"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    property_id: Mapped[str] = mapped_column(String(36), ForeignKey("properties.id"), nullable=False)

    # Personal info
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=True)  # nullable if auto-enrolled via PMS
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    phone: Mapped[str] = mapped_column(String(20), nullable=True)
    ssn_last4: Mapped[str] = mapped_column(String(4), nullable=True)  # for credit bureau matching
    date_of_birth: Mapped[date] = mapped_column(Date, nullable=True)

    # Lease info
    unit_number: Mapped[str] = mapped_column(String(50), nullable=True)
    lease_start_date: Mapped[date] = mapped_column(Date, nullable=False)
    lease_end_date: Mapped[date] = mapped_column(Date, nullable=True)
    monthly_rent_cents: Mapped[int] = mapped_column(Integer, nullable=False)
    pms_resident_id: Mapped[str] = mapped_column(String(255), nullable=True)

    # Enrollment
    enrollment_status: Mapped[EnrollmentStatus] = mapped_column(
        SAEnum(EnrollmentStatus), default=EnrollmentStatus.pending
    )
    enrollment_date: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    trial_end_date: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    opted_out_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    opt_out_reason: Mapped[str] = mapped_column(String(500), nullable=True)

    # Stripe
    stripe_customer_id: Mapped[str] = mapped_column(String(100), nullable=True)
    stripe_subscription_id: Mapped[str] = mapped_column(String(100), nullable=True)

    # Retroactive reporting consent
    retroactive_reporting_consent: Mapped[bool] = mapped_column(Boolean, default=False)
    retroactive_months_requested: Mapped[int] = mapped_column(Integer, default=0)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    property: Mapped["Property"] = relationship("Property", back_populates="residents")
    rent_payments: Mapped[list["RentPayment"]] = relationship("RentPayment", back_populates="resident")
    credit_reports: Mapped[list["CreditReport"]] = relationship("CreditReport", back_populates="resident")
