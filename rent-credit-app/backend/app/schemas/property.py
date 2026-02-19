from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class PropertyCreate(BaseModel):
    name: str
    address_line1: str
    address_line2: Optional[str] = None
    city: str
    state: str
    zip_code: str
    unit_count: Optional[int] = 0
    pms_property_id: Optional[str] = None
    auto_enroll: bool = True
    enrollment_delay_days: int = 3


class PropertyUpdate(BaseModel):
    name: Optional[str] = None
    auto_enroll: Optional[bool] = None
    enrollment_delay_days: Optional[int] = None
    unit_count: Optional[int] = None


class PropertyOut(BaseModel):
    id: str
    property_manager_id: str
    name: str
    address_line1: str
    address_line2: Optional[str]
    city: str
    state: str
    zip_code: str
    unit_count: int
    pms_property_id: Optional[str]
    auto_enroll: bool
    enrollment_delay_days: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True
