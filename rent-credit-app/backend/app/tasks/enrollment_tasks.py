"""Celery tasks for enrollment workflow."""
import asyncio
from datetime import datetime, timedelta
from sqlalchemy import select, and_
from app.worker import celery_app
from app.db.base import AsyncSessionLocal
from app.models.resident import Resident, EnrollmentStatus
from app.services.enrollment_service import enrollment_service
from app.services.email_service import email_service


@celery_app.task(name="app.tasks.enrollment_tasks.activate_pending_enrollments")
def activate_pending_enrollments():
    asyncio.run(_activate_pending_enrollments())


async def _activate_pending_enrollments():
    async with AsyncSessionLocal() as db:
        # Find residents pending enrollment whose delay has passed
        result = await db.execute(
            select(Resident).join(Resident.property).where(
                and_(
                    Resident.enrollment_status == EnrollmentStatus.pending,
                    Resident.is_active == True,
                )
            )
        )
        residents = result.scalars().all()

        for resident in residents:
            delay_days = resident.property.enrollment_delay_days
            enroll_after = resident.lease_start_date + timedelta(days=delay_days)
            if datetime.utcnow().date() >= enroll_after:
                await enrollment_service.activate_trial(resident.id, db)


@celery_app.task(name="app.tasks.enrollment_tasks.send_trial_ending_notices")
def send_trial_ending_notices():
    asyncio.run(_send_trial_ending_notices())


async def _send_trial_ending_notices():
    async with AsyncSessionLocal() as db:
        now = datetime.utcnow()
        three_days_out = now + timedelta(days=3)

        result = await db.execute(
            select(Resident).where(
                and_(
                    Resident.enrollment_status == EnrollmentStatus.trial,
                    Resident.trial_end_date >= now,
                    Resident.trial_end_date <= three_days_out,
                )
            )
        )
        residents = result.scalars().all()

        for resident in residents:
            days_remaining = (resident.trial_end_date - now).days
            await email_service.send_trial_ending_notice(resident, max(days_remaining, 1))
