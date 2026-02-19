from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from app.models.property_manager import PMSType


class PMSConfig(BaseModel):
    pms_type: PMSType
    pms_api_key: Optional[str] = None
    pms_client_id: Optional[str] = None
    pms_client_secret: Optional[str] = None
    pms_instance_url: Optional[str] = None


class PropertyManagerCreate(BaseModel):
    email: EmailStr
    password: str
    company_name: str
    contact_name: str
    phone: Optional[str] = None


class PropertyManagerUpdate(BaseModel):
    company_name: Optional[str] = None
    contact_name: Optional[str] = None
    phone: Optional[str] = None
    report_to_experian: Optional[bool] = None
    report_to_equifax: Optional[bool] = None
    report_to_transunion: Optional[bool] = None


class PropertyManagerOut(BaseModel):
    id: str
    email: str
    company_name: str
    contact_name: str
    phone: Optional[str]
    pms_type: Optional[PMSType]
    stripe_account_id: Optional[str]
    stripe_account_onboarded: bool
    report_to_experian: bool
    report_to_equifax: bool
    report_to_transunion: bool
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_type: str
    user_id: str
