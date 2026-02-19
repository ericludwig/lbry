"""Stripe webhook handler and Stripe Connect onboarding endpoints."""
from fastapi import APIRouter, Depends, HTTPException, Request, Header
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from app.db.base import get_db
from app.models.property_manager import PropertyManager
from app.models.resident import Resident, EnrollmentStatus
from app.services.stripe_service import stripe_service
from app.core.security import get_current_pm, get_current_resident
from app.core.config import settings

router = APIRouter(prefix="/payments", tags=["payments"])


# ---- Property Manager Stripe Connect ----

@router.post("/pm/connect/onboard")
async def start_stripe_onboarding(
    current_user=Depends(get_current_pm),
    db: AsyncSession = Depends(get_db),
):
    """Initiate Stripe Connect Express onboarding for property manager."""
    result = await db.execute(
        select(PropertyManager).where(PropertyManager.id == current_user["user_id"])
    )
    pm = result.scalar_one_or_none()
    if not pm:
        raise HTTPException(status_code=404, detail="Property manager not found")

    if not pm.stripe_account_id:
        account = await stripe_service.create_connect_account(
            email=pm.email,
            company_name=pm.company_name,
        )
        pm.stripe_account_id = account.id
        db.add(pm)
        await db.commit()

    link = await stripe_service.create_account_link(
        account_id=pm.stripe_account_id,
        refresh_url=f"{settings.ALLOWED_ORIGINS}/dashboard/settings?stripe=refresh",
        return_url=f"{settings.ALLOWED_ORIGINS}/dashboard/settings?stripe=success",
    )
    return {"url": link.url}


@router.get("/pm/connect/status")
async def get_stripe_status(
    current_user=Depends(get_current_pm),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(PropertyManager).where(PropertyManager.id == current_user["user_id"])
    )
    pm = result.scalar_one_or_none()
    if not pm or not pm.stripe_account_id:
        return {"connected": False, "onboarded": False}

    account = await stripe_service.get_account(pm.stripe_account_id)
    onboarded = account.get("details_submitted", False)
    if onboarded and not pm.stripe_account_onboarded:
        pm.stripe_account_onboarded = True
        db.add(pm)
        await db.commit()

    return {"connected": True, "onboarded": onboarded, "account_id": pm.stripe_account_id}


# ---- Resident Payment Method ----

@router.post("/resident/setup-intent")
async def create_setup_intent(
    current_user=Depends(get_current_resident),
    db: AsyncSession = Depends(get_db),
):
    """Get Stripe SetupIntent client_secret for resident to add payment method."""
    result = await db.execute(
        select(Resident).where(Resident.id == current_user["user_id"])
    )
    resident = result.scalar_one_or_none()
    if not resident or not resident.stripe_customer_id:
        raise HTTPException(status_code=400, detail="Resident not enrolled in Stripe yet")

    intent = await stripe_service.create_setup_intent(resident.stripe_customer_id)
    return {"client_secret": intent.client_secret}


# ---- Stripe Webhook ----

@router.post("/webhook")
async def stripe_webhook(
    request: Request,
    stripe_signature: str = Header(None, alias="stripe-signature"),
    db: AsyncSession = Depends(get_db),
):
    payload = await request.body()
    try:
        event = stripe_service.construct_event(payload, stripe_signature)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Webhook error: {str(e)}")

    result = await stripe_service.handle_subscription_event(event)
    action = result.get("action")
    subscription_id = result.get("subscription_id")

    if not subscription_id:
        return {"status": "ok"}

    resident_result = await db.execute(
        select(Resident).where(Resident.stripe_subscription_id == subscription_id)
    )
    resident = resident_result.scalar_one_or_none()
    if not resident:
        return {"status": "ok"}

    if action == "deactivate_subscription":
        resident.enrollment_status = EnrollmentStatus.opted_out
        db.add(resident)
        await db.commit()

    elif action == "payment_failed":
        resident.enrollment_status = EnrollmentStatus.payment_failed
        db.add(resident)
        await db.commit()

    elif action == "payment_succeeded":
        if resident.enrollment_status == EnrollmentStatus.trial:
            resident.enrollment_status = EnrollmentStatus.active
            db.add(resident)
            await db.commit()

    return {"status": "ok"}
