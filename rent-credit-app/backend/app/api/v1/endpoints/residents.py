from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from app.db.base import get_db
from app.models.resident import Resident, EnrollmentStatus
from app.models.property import Property
from app.models.rent_payment import RentPayment
from app.models.credit_report import CreditReport
from app.schemas.resident import ResidentCreate, ResidentOut, OptOutRequest, EnrollmentSummary
from app.schemas.rent_payment import RentPaymentOut, PaymentHistoryItem
from app.core.security import get_current_pm, get_current_resident, get_current_user
from app.services.enrollment_service import enrollment_service
from app.core.config import settings
from datetime import date

router = APIRouter(prefix="/residents", tags=["residents"])


@router.post("/", response_model=ResidentOut)
async def add_resident(
    data: ResidentCreate,
    background_tasks: BackgroundTasks,
    current_user=Depends(get_current_pm),
    db: AsyncSession = Depends(get_db),
):
    """Manually add a resident (or called from PMS sync)."""
    # Verify PM owns this property
    prop_result = await db.execute(
        select(Property).where(
            and_(
                Property.id == data.property_id,
                Property.property_manager_id == current_user["user_id"],
            )
        )
    )
    prop = prop_result.scalar_one_or_none()
    if not prop:
        raise HTTPException(status_code=404, detail="Property not found")

    existing = await db.execute(select(Resident).where(Resident.email == data.email))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Resident email already exists")

    resident = Resident(**data.model_dump())
    db.add(resident)
    await db.commit()
    await db.refresh(resident)

    if prop.auto_enroll:
        background_tasks.add_task(enrollment_service.process_new_resident, resident, prop, db)

    return resident


@router.get("/", response_model=list[ResidentOut])
async def list_residents(
    property_id: str = None,
    status: EnrollmentStatus = None,
    current_user=Depends(get_current_pm),
    db: AsyncSession = Depends(get_db),
):
    """List all residents for PM's properties."""
    query = select(Resident).join(Property).where(
        Property.property_manager_id == current_user["user_id"]
    )
    if property_id:
        query = query.where(Resident.property_id == property_id)
    if status:
        query = query.where(Resident.enrollment_status == status)
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/summary", response_model=EnrollmentSummary)
async def get_enrollment_summary(
    current_user=Depends(get_current_pm),
    db: AsyncSession = Depends(get_db),
):
    """Dashboard stats for the property manager."""
    query = select(Resident).join(Property).where(
        Property.property_manager_id == current_user["user_id"]
    )
    result = await db.execute(query)
    residents = result.scalars().all()

    total_active = sum(1 for r in residents if r.enrollment_status == EnrollmentStatus.active)
    return EnrollmentSummary(
        total_enrolled=sum(1 for r in residents if r.enrollment_status in [
            EnrollmentStatus.active, EnrollmentStatus.trial
        ]),
        total_active=total_active,
        total_opted_out=sum(1 for r in residents if r.enrollment_status == EnrollmentStatus.opted_out),
        total_trial=sum(1 for r in residents if r.enrollment_status == EnrollmentStatus.trial),
        monthly_revenue_cents=total_active * settings.RESIDENT_MONTHLY_FEE_CENTS,
        monthly_pm_payout_cents=total_active * settings.PM_MONTHLY_PAYOUT_CENTS,
    )


@router.get("/me", response_model=ResidentOut)
async def get_my_profile(
    current_user=Depends(get_current_resident),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Resident).where(Resident.id == current_user["user_id"]))
    return result.scalar_one_or_404()


@router.get("/me/payments", response_model=list[RentPaymentOut])
async def get_my_payment_history(
    current_user=Depends(get_current_resident),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(RentPayment)
        .where(RentPayment.resident_id == current_user["user_id"])
        .order_by(RentPayment.payment_period_start.desc())
    )
    return result.scalars().all()


@router.post("/me/opt-out")
async def opt_out(
    data: OptOutRequest,
    current_user=Depends(get_current_resident),
    db: AsyncSession = Depends(get_db),
):
    """Resident opts out of rent reporting."""
    await enrollment_service.opt_out_resident(
        current_user["user_id"], data.reason or "", db
    )
    return {"status": "opted_out"}


@router.post("/opt-out/{token}")
async def opt_out_via_token(
    token: str,  # token = resident_id from email link
    db: AsyncSession = Depends(get_db),
):
    """Opt-out via email link (no auth required)."""
    await enrollment_service.opt_out_resident(token, "opted_out_via_email_link", db)
    return {"status": "opted_out", "message": "You have been successfully unenrolled from RentReport."}


@router.get("/{resident_id}", response_model=ResidentOut)
async def get_resident(
    resident_id: str,
    current_user=Depends(get_current_pm),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Resident).join(Property).where(
            and_(
                Resident.id == resident_id,
                Property.property_manager_id == current_user["user_id"],
            )
        )
    )
    resident = result.scalar_one_or_none()
    if not resident:
        raise HTTPException(status_code=404, detail="Resident not found")
    return resident
