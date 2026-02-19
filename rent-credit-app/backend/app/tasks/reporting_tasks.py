"""Celery tasks for monthly PMS sync and credit bureau reporting."""
import asyncio
from datetime import date, datetime
import uuid
from sqlalchemy import select, and_
from app.worker import celery_app
from app.db.base import AsyncSessionLocal
from app.models.resident import Resident, EnrollmentStatus
from app.models.property import Property
from app.models.property_manager import PropertyManager
from app.models.rent_payment import RentPayment, PaymentStatus, ReportingStatus
from app.models.credit_report import CreditReport, CreditReportBatch, CreditBureau, CreditReportStatus
from app.services.pms_service import get_pms_adapter
from app.services.enrollment_service import enrollment_service
from app.services.metro2_service import metro2_service
from app.services.email_service import email_service


@celery_app.task(name="app.tasks.reporting_tasks.sync_all_pms_data")
def sync_all_pms_data():
    asyncio.run(_sync_all_pms_data())


async def _sync_all_pms_data():
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(PropertyManager).where(PropertyManager.is_active == True)
        )
        managers = result.scalars().all()

        for pm in managers:
            if not pm.pms_type or pm.pms_type.value == "manual":
                continue

            adapter = get_pms_adapter(
                pm.pms_type.value,
                api_key=pm.pms_api_key,
                client_id=pm.pms_client_id,
                client_secret=pm.pms_client_secret,
                instance_url=pm.pms_instance_url,
            )

            props_result = await db.execute(
                select(Property).where(
                    and_(Property.property_manager_id == pm.id, Property.is_active == True)
                )
            )
            properties = props_result.scalars().all()

            for prop in properties:
                if not prop.pms_property_id:
                    continue
                try:
                    pms_residents = await adapter.get_residents(prop.pms_property_id)
                    for pms_res in pms_residents:
                        # Find or create resident
                        res_result = await db.execute(
                            select(Resident).where(
                                Resident.pms_resident_id == pms_res["pms_resident_id"]
                            )
                        )
                        resident = res_result.scalar_one_or_none()

                        if not resident:
                            from app.schemas.resident import ResidentCreate
                            from datetime import date as d
                            resident = Resident(
                                property_id=prop.id,
                                email=pms_res["email"],
                                first_name=pms_res["first_name"],
                                last_name=pms_res["last_name"],
                                phone=pms_res.get("phone"),
                                unit_number=pms_res.get("unit_number"),
                                lease_start_date=date.fromisoformat(pms_res["lease_start_date"]),
                                monthly_rent_cents=pms_res["monthly_rent_cents"],
                                pms_resident_id=pms_res["pms_resident_id"],
                            )
                            db.add(resident)
                            await db.commit()
                            await db.refresh(resident)
                            await enrollment_service.process_new_resident(resident, prop, db)

                        # Sync payment ledger
                        pms_payments = await adapter.get_payment_ledger(
                            pms_res["pms_resident_id"], months=24
                        )
                        await enrollment_service.sync_payments_from_pms(resident, pms_payments, db)

                except Exception as e:
                    print(f"PMS sync error for property {prop.id}: {e}")


@celery_app.task(name="app.tasks.reporting_tasks.run_monthly_credit_reporting")
def run_monthly_credit_reporting():
    asyncio.run(_run_monthly_credit_reporting())


async def _run_monthly_credit_reporting():
    """Generate and submit Metro 2 files for all eligible residents."""
    async with AsyncSessionLocal() as db:
        today = date.today()
        reporting_period = f"{today.year}-{today.month:02d}"
        period_start = date(today.year, today.month, 1)

        result = await db.execute(
            select(PropertyManager).where(PropertyManager.is_active == True)
        )
        managers = result.scalars().all()

        for pm in managers:
            bureaus = []
            if pm.report_to_experian:
                bureaus.append("experian")
            if pm.report_to_equifax:
                bureaus.append("equifax")
            if pm.report_to_transunion:
                bureaus.append("transunion")

            if not bureaus:
                continue

            # Get all active enrolled residents for this PM
            res_result = await db.execute(
                select(Resident)
                .join(Property)
                .where(
                    and_(
                        Property.property_manager_id == pm.id,
                        Resident.enrollment_status == EnrollmentStatus.active,
                    )
                )
            )
            residents = res_result.scalars().all()

            payments_to_report: list[tuple[Resident, RentPayment]] = []
            for resident in residents:
                pay_result = await db.execute(
                    select(RentPayment).where(
                        and_(
                            RentPayment.resident_id == resident.id,
                            RentPayment.payment_period_start == period_start,
                            RentPayment.payment_status == PaymentStatus.on_time,
                            RentPayment.reporting_status == ReportingStatus.pending,
                        )
                    )
                )
                payment = pay_result.scalar_one_or_none()
                if payment:
                    payments_to_report.append((resident, payment))

            if not payments_to_report:
                continue

            batch_id = str(uuid.uuid4())

            for bureau in bureaus:
                try:
                    file_content = metro2_service.generate_metro2_file(
                        payments_to_report,
                        reporter_name=pm.company_name,
                        reporter_id=pm.id[:6].upper(),
                    )
                    filename = f"{pm.id}_{bureau}_{reporting_period}.metro2"

                    batch = CreditReportBatch(
                        id=batch_id,
                        property_manager_id=pm.id,
                        bureau=CreditBureau(bureau),
                        reporting_period=reporting_period,
                        record_count=len(payments_to_report),
                        status="submitted",
                        submitted_at=datetime.utcnow(),
                    )
                    db.add(batch)

                    for resident, payment in payments_to_report:
                        report = CreditReport(
                            resident_id=resident.id,
                            rent_payment_id=payment.id,
                            bureau=CreditBureau(bureau),
                            status=CreditReportStatus.submitted,
                            batch_id=batch_id,
                            submitted_at=datetime.utcnow(),
                        )
                        db.add(report)
                        payment.reporting_status = ReportingStatus.reported
                        payment.reported_at = datetime.utcnow()
                        payment.report_batch_id = batch_id

                    await metro2_service.submit_to_bureau(bureau, file_content, filename)
                    await db.commit()

                    # Send confirmation emails
                    for resident, _ in payments_to_report:
                        await email_service.send_monthly_report_confirmation(
                            resident, reporting_period, bureaus
                        )

                except Exception as e:
                    print(f"Credit reporting error for PM {pm.id}, bureau {bureau}: {e}")


@celery_app.task(name="app.tasks.reporting_tasks.process_pm_payouts")
def process_pm_payouts():
    asyncio.run(_process_pm_payouts())


async def _process_pm_payouts():
    today = date.today()
    reporting_period = f"{today.year}-{today.month:02d}"

    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(PropertyManager).where(
                and_(
                    PropertyManager.is_active == True,
                    PropertyManager.stripe_account_onboarded == True,
                )
            )
        )
        managers = result.scalars().all()

        for pm in managers:
            count_result = await db.execute(
                select(Resident)
                .join(Property)
                .where(
                    and_(
                        Property.property_manager_id == pm.id,
                        Resident.enrollment_status == EnrollmentStatus.active,
                    )
                )
            )
            enrolled = count_result.scalars().all()
            await enrollment_service.process_monthly_pm_payouts(
                pm, len(enrolled), reporting_period, db
            )
