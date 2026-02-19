"""
Email service using Resend.
Handles: enrollment welcome, opt-out links, trial ending notices, payment confirmations.
"""
import resend
from app.core.config import settings

resend.api_key = settings.RESEND_API_KEY


class EmailService:

    async def send_enrollment_welcome(self, resident) -> bool:
        """
        Send welcome email to newly enrolled resident with opt-out link.
        """
        opt_out_link = f"https://app.rentreport.com/opt-out?token={resident.id}"
        portal_link = f"https://app.rentreport.com/resident/dashboard"

        try:
            resend.Emails.send({
                "from": settings.EMAIL_FROM,
                "to": resident.email,
                "subject": "Welcome to RentReport - Your Rent is Now Building Credit!",
                "html": f"""
                <h2>Welcome, {resident.first_name}!</h2>
                <p>Great news — your property has enrolled you in <strong>RentReport</strong>,
                a service that reports your on-time rent payments to Experian, Equifax, and TransUnion
                to help you build credit.</p>

                <h3>How it works:</h3>
                <ul>
                    <li>Your first month is <strong>FREE</strong>. After your trial period, the service
                    is just <strong>$8.95/month</strong>, billed as a line item with your rent.</li>
                    <li>On-time rent payments are automatically reported to the credit bureaus every month.</li>
                    <li>You can request up to <strong>24 months</strong> of back-reporting at no extra charge.</li>
                    <li>Average credit score improvement: <strong>20–40 points</strong> after 12 months.</li>
                </ul>

                <p><a href="{portal_link}" style="background:#2563EB;color:white;padding:12px 24px;
                border-radius:6px;text-decoration:none;display:inline-block;margin:16px 0;">
                View Your Credit Dashboard</a></p>

                <p style="color:#6B7280;font-size:14px;">
                Enrollment is optional. If you do not wish to participate, you may opt out at any time
                by clicking <a href="{opt_out_link}">this link</a> or emailing support@rentreport.com.
                No charges will be applied during your free trial period.
                </p>
                """,
            })
            return True
        except Exception:
            return False

    async def send_opt_out_confirmation(self, resident) -> bool:
        try:
            resend.Emails.send({
                "from": settings.EMAIL_FROM,
                "to": resident.email,
                "subject": "You've been unenrolled from RentReport",
                "html": f"""
                <h2>Enrollment Cancelled</h2>
                <p>Hi {resident.first_name}, you have been successfully unenrolled from RentReport.
                No further charges will be applied.</p>
                <p>Your rent payment reporting has stopped. If you change your mind,
                you can re-enroll any time through your resident portal.</p>
                <p><a href="https://app.rentreport.com/resident/enroll">Re-enroll</a></p>
                """,
            })
            return True
        except Exception:
            return False

    async def send_trial_ending_notice(self, resident, days_remaining: int) -> bool:
        try:
            resend.Emails.send({
                "from": settings.EMAIL_FROM,
                "to": resident.email,
                "subject": f"Your free RentReport trial ends in {days_remaining} days",
                "html": f"""
                <h2>Your trial ends soon</h2>
                <p>Hi {resident.first_name}, your free RentReport trial ends in <strong>{days_remaining} days</strong>.
                After that, the service continues at $8.95/month, added to your rent ledger.</p>
                <p>To opt out before being charged, click below:</p>
                <p><a href="https://app.rentreport.com/opt-out?token={resident.id}">Cancel Enrollment</a></p>
                """,
            })
            return True
        except Exception:
            return False

    async def send_monthly_report_confirmation(self, resident, period: str, bureaus: list[str]) -> bool:
        bureau_list = ", ".join(bureaus)
        try:
            resend.Emails.send({
                "from": settings.EMAIL_FROM,
                "to": resident.email,
                "subject": f"Your rent payment for {period} has been reported",
                "html": f"""
                <h2>Rent Reported!</h2>
                <p>Hi {resident.first_name}, your on-time rent payment for <strong>{period}</strong>
                has been submitted to <strong>{bureau_list}</strong>.</p>
                <p>It typically takes 30–40 days to appear on your credit report.</p>
                <p><a href="https://app.rentreport.com/resident/history">View Reporting History</a></p>
                """,
            })
            return True
        except Exception:
            return False

    async def send_pm_welcome(self, pm) -> bool:
        try:
            resend.Emails.send({
                "from": settings.EMAIL_FROM,
                "to": pm.email,
                "subject": "Welcome to RentReport - Property Manager Portal",
                "html": f"""
                <h2>Welcome, {pm.contact_name}!</h2>
                <p>Your RentReport account for <strong>{pm.company_name}</strong> is ready.</p>
                <p>Next steps:</p>
                <ol>
                    <li>Connect your property management software in the <strong>Integrations</strong> tab</li>
                    <li>Add your properties</li>
                    <li>Set up your Stripe Connect account to receive your <strong>$3.00/month/resident</strong> revenue share</li>
                </ol>
                <p><a href="https://app.rentreport.com/dashboard">Go to Dashboard</a></p>
                """,
            })
            return True
        except Exception:
            return False


email_service = EmailService()
