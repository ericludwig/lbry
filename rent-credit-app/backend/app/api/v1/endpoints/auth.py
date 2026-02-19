from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.base import get_db
from app.models.property_manager import PropertyManager
from app.models.resident import Resident
from app.schemas.property_manager import PropertyManagerCreate, LoginRequest, TokenResponse, PropertyManagerOut
from app.core.security import get_password_hash, verify_password, create_access_token
from app.services.email_service import email_service

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register/property-manager", response_model=PropertyManagerOut)
async def register_property_manager(
    data: PropertyManagerCreate,
    db: AsyncSession = Depends(get_db),
):
    existing = await db.execute(
        select(PropertyManager).where(PropertyManager.email == data.email)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email already registered")

    pm = PropertyManager(
        email=data.email,
        hashed_password=get_password_hash(data.password),
        company_name=data.company_name,
        contact_name=data.contact_name,
        phone=data.phone,
    )
    db.add(pm)
    await db.commit()
    await db.refresh(pm)
    await email_service.send_pm_welcome(pm)
    return pm


@router.post("/login", response_model=TokenResponse)
async def login(data: LoginRequest, db: AsyncSession = Depends(get_db)):
    # Try PM login first
    pm_result = await db.execute(
        select(PropertyManager).where(PropertyManager.email == data.email)
    )
    pm = pm_result.scalar_one_or_none()
    if pm and verify_password(data.password, pm.hashed_password):
        token = create_access_token({"sub": pm.id, "type": "property_manager"})
        return TokenResponse(access_token=token, user_type="property_manager", user_id=pm.id)

    # Try resident login
    res_result = await db.execute(
        select(Resident).where(Resident.email == data.email)
    )
    resident = res_result.scalar_one_or_none()
    if resident and resident.hashed_password and verify_password(data.password, resident.hashed_password):
        token = create_access_token({"sub": resident.id, "type": "resident"})
        return TokenResponse(access_token=token, user_type="resident", user_id=resident.id)

    raise HTTPException(status_code=401, detail="Invalid credentials")


@router.post("/resident/signup")
async def resident_signup(
    token: str,
    password: str,
    db: AsyncSession = Depends(get_db),
):
    """Resident sets password after being auto-enrolled."""
    result = await db.execute(select(Resident).where(Resident.id == token))
    resident = result.scalar_one_or_none()
    if not resident:
        raise HTTPException(status_code=404, detail="Invalid enrollment token")

    resident.hashed_password = get_password_hash(password)
    db.add(resident)
    await db.commit()
    access_token = create_access_token({"sub": resident.id, "type": "resident"})
    return TokenResponse(access_token=access_token, user_type="resident", user_id=resident.id)
