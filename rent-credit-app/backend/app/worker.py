"""
Celery background task worker.
Handles scheduled jobs: monthly PMS syncs, credit bureau submissions, PM payouts.
"""
from celery import Celery
from celery.schedules import crontab
from app.core.config import settings

celery_app = Celery(
    "rentreport",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=["app.tasks.enrollment_tasks", "app.tasks.reporting_tasks"],
)

celery_app.conf.beat_schedule = {
    # Sync residents and payments from PMS every night at 2 AM
    "sync-pms-data": {
        "task": "app.tasks.reporting_tasks.sync_all_pms_data",
        "schedule": crontab(hour=2, minute=0),
    },
    # Submit Metro 2 files to bureaus on the 18th of each month
    "monthly-credit-reporting": {
        "task": "app.tasks.reporting_tasks.run_monthly_credit_reporting",
        "schedule": crontab(day_of_month=18, hour=6, minute=0),
    },
    # Process PM revenue share payouts on the 20th of each month
    "monthly-pm-payouts": {
        "task": "app.tasks.reporting_tasks.process_pm_payouts",
        "schedule": crontab(day_of_month=20, hour=10, minute=0),
    },
    # Check for pending enrollments (trial activations) every hour
    "activate-pending-enrollments": {
        "task": "app.tasks.enrollment_tasks.activate_pending_enrollments",
        "schedule": crontab(minute=0),  # Every hour
    },
    # Send trial-ending notices 3 days before trial ends
    "trial-ending-notices": {
        "task": "app.tasks.enrollment_tasks.send_trial_ending_notices",
        "schedule": crontab(hour=9, minute=0),  # Every day at 9 AM
    },
}

celery_app.conf.timezone = "UTC"
