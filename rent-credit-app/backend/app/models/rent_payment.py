import uuid
from datetime import datetime, date
from sqlalchemy import String, Boolean, DateTime, Date, Integer, ForeignKey, Enum as SAEnum, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base
import enum


class PaymentStatus(str, enum.Enum):
    on_time = "on_time"
    late = "late"
    not_paid = "not_paid"
    partial = "partial"


class ReportingStatus(str, enum.Enum):
    pending = "pending"
    reported = "reported"
    skipped = "skipped"     # Late/missed - positive-only policy
    failed = "failed"
    retroactive = "retroactive"


class RentPayment(Base):
    """
    Represents a rent payment event pulled from the PMS ledger.
    One record per monthly rent period per resident.
    """
    __tablename__ = "rent_payments"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    resident_id: Mapped[str] = mapped_column(String(36), ForeignKey("residents.id"), nullable=False)

    # Payment period
    payment_period_start: Mapped[date] = mapped_column(Date, nullable=False)  # e.g. 2024-01-01
    payment_period_end: Mapped[date] = mapped_column(Date, nullable=False)    # e.g. 2024-01-31
    due_date: Mapped[date] = mapped_column(Date, nullable=False)
    paid_date: Mapped[date] = mapped_column(Date, nullable=True)

    amount_due_cents: Mapped[int] = mapped_column(Integer, nullable=False)
    amount_paid_cents: Mapped[int] = mapped_column(Integer, nullable=True)

    payment_status: Mapped[PaymentStatus] = mapped_column(SAEnum(PaymentStatus), nullable=False)
    reporting_status: Mapped[ReportingStatus] = mapped_column(
        SAEnum(ReportingStatus), default=ReportingStatus.pending
    )

    # PMS reference
    pms_transaction_id: Mapped[str] = mapped_column(String(255), nullable=True)

    # Credit bureau submission
    reported_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    report_batch_id: Mapped[str] = mapped_column(String(36), nullable=True)
    metro2_sequence_number: Mapped[int] = mapped_column(Integer, nullable=True)

    is_retroactive: Mapped[bool] = mapped_column(Boolean, default=False)
    notes: Mapped[str] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    resident: Mapped["Resident"] = relationship("Resident", back_populates="rent_payments")
    credit_reports: Mapped[list["CreditReport"]] = relationship("CreditReport", back_populates="rent_payment")
