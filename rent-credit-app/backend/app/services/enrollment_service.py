"""
Auto-enrollment workflow service.

Flow:
1. PMS sync adds resident → status=pending
2. After enrollment_delay_days → activate trial, send welcome email, create Stripe customer
3. After trial ends (30 days) → charge begins ($8.95/month)
4. Monthly: pull PMS ledger → create RentPayment records → batch to credit bureaus
5. PM payout: transfer $3.00/enrolled resident to their Stripe Connect account
"""
from datetime import datetime, timedelta, date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from app.models.resident import Resident, EnrollmentStatus
from app.models.property import Property
from app.models.property_manager import PropertyManager
from app.models.rent_payment import RentPayment, PaymentStatus, ReportingStatus
from app.services.stripe_service import stripe_service
from app.services.email_service import email_service
from app.core.config import settings


class EnrollmentService:

    async def process_new_resident(
        self,
        resident: Resident,
        property_obj: Property,
        db: AsyncSession,
    ) -> Resident:
        """
        Called when a new resident is added (from PMS sync or manual).
        Sets enrollment to pending; a scheduled job will activate the trial.
        """
        if property_obj.auto_enroll:
            resident.enrollment_status = EnrollmentStatus.pending
            db.add(resident)
            await db.commit()
            await db.refresh(resident)

            # Schedule trial activation via background task
            # (In production, use Celery: activate_trial.apply_async(
            #     args=[resident.id], countdown=property_obj.enrollment_delay_days * 86400))
        return resident

    async def activate_trial(self, resident_id: str, db: AsyncSession) -> Resident:
        """
        Activate free trial for a resident.
        Creates Stripe customer, sets trial dates, sends welcome email.
        """
        result = await db.execute(select(Resident).where(Resident.id == resident_id))
        resident = result.scalar_one_or_none()
        if not resident or resident.enrollment_status != EnrollmentStatus.pending:
            return resident

        # Create Stripe customer
        customer = await stripe_service.create_customer(
            email=resident.email,
            name=f"{resident.first_name} {resident.last_name}",
            metadata={"resident_id": resident.id, "property_id": resident.property_id},
        )
        resident.stripe_customer_id = customer.id

        # Create subscription with trial
        subscription = await stripe_service.create_subscription(
            customer_id=customer.id,
            price_id=settings.STRIPE_RESIDENT_PRICE_ID,
            trial_days=settings.FREE_TRIAL_DAYS,
            metadata={"resident_id": resident.id},
        )
        resident.stripe_subscription_id = subscription.id

        now = datetime.utcnow()
        resident.enrollment_status = EnrollmentStatus.trial
        resident.enrollment_date = now
        resident.trial_end_date = now + timedelta(days=settings.FREE_TRIAL_DAYS)

        db.add(resident)
        await db.commit()
        await db.refresh(resident)

        # Send welcome email with opt-out link
        await email_service.send_enrollment_welcome(resident)

        return resident

    async def opt_out_resident(
        self,
        resident_id: str,
        reason: str,
        db: AsyncSession,
    ) -> Resident:
        """Cancel enrollment and Stripe subscription."""
        result = await db.execute(select(Resident).where(Resident.id == resident_id))
        resident = result.scalar_one_or_none()
        if not resident:
            raise ValueError("Resident not found")

        if resident.stripe_subscription_id:
            await stripe_service.cancel_subscription(resident.stripe_subscription_id)

        resident.enrollment_status = EnrollmentStatus.opted_out
        resident.opted_out_at = datetime.utcnow()
        resident.opt_out_reason = reason

        db.add(resident)
        await db.commit()
        await db.refresh(resident)

        await email_service.send_opt_out_confirmation(resident)
        return resident

    async def sync_payments_from_pms(
        self,
        resident: Resident,
        pms_payments: list[dict],
        db: AsyncSession,
    ) -> list[RentPayment]:
        """
        Upsert payment records from PMS ledger data.
        Only creates records for the months when resident was enrolled.
        """
        created = []
        for pms_payment in pms_payments:
            due_date_str = pms_payment.get("due_date", "")
            if not due_date_str:
                continue

            try:
                due_date = date.fromisoformat(due_date_str)
            except (ValueError, TypeError):
                continue

            # Only report months after enrollment
            if resident.enrollment_date and due_date < resident.enrollment_date.date():
                if not pms_payment.get("is_retroactive"):
                    continue

            period_start = date(due_date.year, due_date.month, 1)
            period_end = (period_start.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)

            # Check if record already exists
            existing = await db.execute(
                select(RentPayment).where(
                    and_(
                        RentPayment.resident_id == resident.id,
                        RentPayment.payment_period_start == period_start,
                    )
                )
            )
            if existing.scalar_one_or_none():
                continue

            is_on_time = pms_payment.get("is_on_time", False)
            paid_date_str = pms_payment.get("paid_date", "")
            try:
                paid_date = date.fromisoformat(paid_date_str) if paid_date_str else None
            except ValueError:
                paid_date = None

            amount_due = pms_payment.get("amount_due_cents", 0)
            amount_paid = pms_payment.get("amount_paid_cents", 0)

            payment = RentPayment(
                resident_id=resident.id,
                payment_period_start=period_start,
                payment_period_end=period_end,
                due_date=due_date,
                paid_date=paid_date,
                amount_due_cents=amount_due,
                amount_paid_cents=amount_paid,
                payment_status=PaymentStatus.on_time if is_on_time else PaymentStatus.late,
                # Positive-only: only report on-time payments
                reporting_status=ReportingStatus.pending if is_on_time else ReportingStatus.skipped,
                pms_transaction_id=pms_payment.get("pms_transaction_id", ""),
                is_retroactive=pms_payment.get("is_retroactive", False),
            )
            db.add(payment)
            created.append(payment)

        await db.commit()
        return created

    async def process_monthly_pm_payouts(
        self,
        property_manager: PropertyManager,
        enrolled_resident_count: int,
        reporting_period: str,
        db: AsyncSession,
    ) -> bool:
        """
        Transfer $3.00 per enrolled resident to the property manager's Stripe Connect account.
        Called monthly after credit bureau submissions.
        """
        if not property_manager.stripe_account_id or not property_manager.stripe_account_onboarded:
            return False

        total_payout_cents = settings.PM_MONTHLY_PAYOUT_CENTS * enrolled_resident_count
        if total_payout_cents <= 0:
            return False

        await stripe_service.create_payout_to_pm(
            connected_account_id=property_manager.stripe_account_id,
            amount_cents=total_payout_cents,
            description=f"RentReport revenue share - {reporting_period} - {enrolled_resident_count} residents",
            metadata={
                "pm_id": property_manager.id,
                "period": reporting_period,
                "resident_count": str(enrolled_resident_count),
            },
        )
        return True


enrollment_service = EnrollmentService()
