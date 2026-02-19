import uuid
from datetime import datetime
from sqlalchemy import String, Boolean, DateTime, Integer, ForeignKey, Enum as SAEnum, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base
import enum


class CreditBureau(str, enum.Enum):
    experian = "experian"
    equifax = "equifax"
    transunion = "transunion"


class CreditReportStatus(str, enum.Enum):
    pending = "pending"
    submitted = "submitted"
    accepted = "accepted"
    rejected = "rejected"


class CreditReport(Base):
    """
    Tracks submission of a rent payment to a specific credit bureau.
    One record per (rent_payment, bureau) pair.
    """
    __tablename__ = "credit_reports"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    resident_id: Mapped[str] = mapped_column(String(36), ForeignKey("residents.id"), nullable=False)
    rent_payment_id: Mapped[str] = mapped_column(String(36), ForeignKey("rent_payments.id"), nullable=False)

    bureau: Mapped[CreditBureau] = mapped_column(SAEnum(CreditBureau), nullable=False)
    status: Mapped[CreditReportStatus] = mapped_column(
        SAEnum(CreditReportStatus), default=CreditReportStatus.pending
    )

    batch_id: Mapped[str] = mapped_column(String(36), nullable=True, index=True)
    submitted_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    acknowledged_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    error_message: Mapped[str] = mapped_column(Text, nullable=True)

    # Metro 2 data snapshot
    metro2_data: Mapped[str] = mapped_column(Text, nullable=True)  # JSON

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    resident: Mapped["Resident"] = relationship("Resident", back_populates="credit_reports")
    rent_payment: Mapped["RentPayment"] = relationship("RentPayment", back_populates="credit_reports")


class CreditReportBatch(Base):
    """Monthly batch submitted to bureaus around the 15th-20th."""
    __tablename__ = "credit_report_batches"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    property_manager_id: Mapped[str] = mapped_column(String(36), ForeignKey("property_managers.id"), nullable=False)
    bureau: Mapped[CreditBureau] = mapped_column(SAEnum(CreditBureau), nullable=False)
    reporting_period: Mapped[str] = mapped_column(String(7), nullable=False)  # "2024-01"
    record_count: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[str] = mapped_column(String(50), default="pending")
    file_path: Mapped[str] = mapped_column(String(500), nullable=True)
    submitted_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
