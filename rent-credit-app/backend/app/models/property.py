import uuid
from datetime import datetime
from sqlalchemy import String, Boolean, DateTime, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


class Property(Base):
    __tablename__ = "properties"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    property_manager_id: Mapped[str] = mapped_column(String(36), ForeignKey("property_managers.id"), nullable=False)

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    address_line1: Mapped[str] = mapped_column(String(255), nullable=False)
    address_line2: Mapped[str] = mapped_column(String(255), nullable=True)
    city: Mapped[str] = mapped_column(String(100), nullable=False)
    state: Mapped[str] = mapped_column(String(2), nullable=False)
    zip_code: Mapped[str] = mapped_column(String(10), nullable=False)
    unit_count: Mapped[int] = mapped_column(Integer, default=0)

    # External PMS identifier for this property
    pms_property_id: Mapped[str] = mapped_column(String(255), nullable=True)

    # Auto-enrollment: enroll all new residents automatically
    auto_enroll: Mapped[bool] = mapped_column(Boolean, default=True)
    # Enrollment starts N days after lease start
    enrollment_delay_days: Mapped[int] = mapped_column(Integer, default=3)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    property_manager: Mapped["PropertyManager"] = relationship("PropertyManager", back_populates="properties")
    residents: Mapped[list["Resident"]] = relationship("Resident", back_populates="property")
