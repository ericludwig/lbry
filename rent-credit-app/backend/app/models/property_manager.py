import uuid
from datetime import datetime
from sqlalchemy import String, Boolean, DateTime, Integer, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base
import enum


class PMSType(str, enum.Enum):
    realpage = "realpage"
    yardi = "yardi"
    appfolio = "appfolio"
    entrata = "entrata"
    manual = "manual"


class PropertyManager(Base):
    __tablename__ = "property_managers"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    company_name: Mapped[str] = mapped_column(String(255), nullable=False)
    contact_name: Mapped[str] = mapped_column(String(255), nullable=False)
    phone: Mapped[str] = mapped_column(String(20), nullable=True)

    # Stripe Connect for revenue share payouts
    stripe_account_id: Mapped[str] = mapped_column(String(100), nullable=True)
    stripe_account_onboarded: Mapped[bool] = mapped_column(Boolean, default=False)

    # PMS Integration
    pms_type: Mapped[PMSType] = mapped_column(SAEnum(PMSType), nullable=True)
    pms_api_key: Mapped[str] = mapped_column(String(500), nullable=True)  # encrypted in production
    pms_client_id: Mapped[str] = mapped_column(String(255), nullable=True)
    pms_client_secret: Mapped[str] = mapped_column(String(500), nullable=True)
    pms_instance_url: Mapped[str] = mapped_column(String(500), nullable=True)

    # Credit bureau reporting selection
    report_to_experian: Mapped[bool] = mapped_column(Boolean, default=True)
    report_to_equifax: Mapped[bool] = mapped_column(Boolean, default=True)
    report_to_transunion: Mapped[bool] = mapped_column(Boolean, default=True)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    properties: Mapped[list["Property"]] = relationship("Property", back_populates="property_manager")
