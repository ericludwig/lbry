"""
Metro 2 Credit Reporting Format Service.

Metro 2 is the standard format used for credit bureau reporting (FCRA compliance).
This service generates Metro 2 compliant fixed-width files for submission to
Experian, Equifax, and TransUnion via SFTP.

Reference: CDIA Credit Reporting Resource Guide
"""
import paramiko
import json
from datetime import date, datetime
from typing import Optional
from dataclasses import dataclass
from app.core.config import settings
from app.models.resident import Resident
from app.models.rent_payment import RentPayment, PaymentStatus


HEADER_RECORD_IDENTIFIER = "HEADER"
DATA_RECORD_IDENTIFIER = "1"
TRAILER_RECORD_IDENTIFIER = "TRAILER"

# Metro 2 Account Type: 4C = Rental Agreement
ACCOUNT_TYPE_RENTAL = "4C"
# Metro 2 Account Rating: 01 = current
ACCOUNT_RATING_CURRENT = "01"
# Portfolio Type: I = Installment
PORTFOLIO_TYPE = "I"


@dataclass
class Metro2Record:
    """One Metro 2 data record per resident per reporting period."""
    # Segment identifiers
    record_identifier: str = DATA_RECORD_IDENTIFIER

    # J1 Segment - Primary consumer
    consumer_last_name: str = ""
    consumer_first_name: str = ""
    consumer_middle_name: str = ""
    consumer_ssn: str = ""          # Full SSN required for bureau matching
    consumer_dob: str = ""          # MMDDYYYY

    # Account info
    account_number: str = ""        # Our internal resident_id
    portfolio_type: str = PORTFOLIO_TYPE
    account_type: str = ACCOUNT_TYPE_RENTAL
    date_opened: str = ""           # MMDDYYYY - lease start date
    credit_limit: int = 0           # Monthly rent amount
    highest_credit: int = 0         # Monthly rent amount
    terms_duration: int = 1         # Monthly
    terms_frequency: str = "M"      # M = Monthly

    # Payment info
    scheduled_monthly_payment: int = 0
    actual_payment_amount: int = 0
    account_status: str = ACCOUNT_RATING_CURRENT   # 11=Current
    payment_rating: str = "0"       # 0 = no payment history
    date_of_account_info: str = ""  # MMDDYYYY - reporting period
    amount_past_due: int = 0
    current_balance: int = 0

    # Address
    address_line1: str = ""
    city: str = ""
    state: str = ""
    zip_code: str = ""

    def to_metro2_line(self) -> str:
        """
        Generate fixed-width Metro 2 format line (426 characters).
        Simplified version - production would use full CDIA spec.
        """
        def pad(s: str, length: int, fill: str = " ", align: str = "left") -> str:
            s = str(s)[:length]
            return s.ljust(length, fill) if align == "left" else s.rjust(length, fill)

        def pad_num(n: int, length: int) -> str:
            return str(n)[:length].zfill(length)

        line = (
            pad(self.record_identifier, 1) +
            pad("426", 4, "0", "right") +          # Record descriptor word
            pad(self.portfolio_type, 1) +
            pad(self.account_type, 2) +
            pad(self.account_number, 30) +
            pad_num(self.credit_limit, 9) +
            pad_num(self.highest_credit, 9) +
            pad(self.terms_duration, 3, "0", "right") +
            pad(self.terms_frequency, 1) +
            pad_num(self.scheduled_monthly_payment, 9) +
            pad_num(self.actual_payment_amount, 9) +
            pad(self.account_status, 2) +
            pad(self.payment_rating, 1) +
            pad(self.date_of_account_info, 8) +
            pad_num(self.amount_past_due, 9) +
            pad_num(self.current_balance, 9) +
            pad(self.consumer_last_name, 25) +
            pad(self.consumer_first_name, 20) +
            pad(self.consumer_middle_name, 20) +
            pad(self.consumer_ssn, 9) +
            pad(self.consumer_dob, 8) +
            pad(self.address_line1, 32) +
            pad(self.city, 20) +
            pad(self.state, 2) +
            pad(self.zip_code, 9) +
            pad(self.date_opened, 8) +
            " " * 187  # Remaining fields (simplified)
        )
        return line[:426].ljust(426)


class Metro2Service:

    def build_header(
        self,
        reporter_name: str,
        reporter_address: str,
        reporter_city_state_zip: str,
        reporter_phone: str,
        reporter_id: str,
        cycle_identifier: str,
        program_date: str,
        program_revision_date: str,
    ) -> str:
        """Generate Metro 2 header record."""
        def pad(s: str, length: int, fill: str = " ") -> str:
            return str(s)[:length].ljust(length, fill)

        header = (
            pad(HEADER_RECORD_IDENTIFIER, 6) +
            pad("0426", 4) +
            pad(cycle_identifier, 2) +
            pad(program_date, 8) +
            pad(program_revision_date, 8) +
            pad(reporter_name, 40) +
            pad(reporter_address, 40) +
            pad(reporter_city_state_zip, 40) +
            pad(reporter_phone, 15) +
            pad(reporter_id, 10) +
            " " * 253
        )
        return header[:426].ljust(426)

    def build_trailer(self, base_record_count: int, total_balance: int = 0) -> str:
        def pad(s, length, fill=" ", align="left"):
            s = str(s)[:length]
            return s.ljust(length, fill) if align == "left" else s.rjust(length, fill)

        trailer = (
            pad(TRAILER_RECORD_IDENTIFIER, 7) +
            pad("0426", 4) +
            pad(str(base_record_count).zfill(9), 9) +
            pad(str(total_balance).zfill(18), 18) +
            " " * 388
        )
        return trailer[:426].ljust(426)

    def build_record_from_payment(
        self,
        resident: Resident,
        payment: RentPayment,
        ssn: Optional[str] = None,
    ) -> Metro2Record:
        """Convert a RentPayment to a Metro 2 record."""
        dob_str = ""
        if resident.date_of_birth:
            dob_str = resident.date_of_birth.strftime("%m%d%Y")

        lease_start = resident.lease_start_date.strftime("%m%d%Y")
        period_date = payment.payment_period_start.strftime("%m%d%Y")

        # Determine account status based on payment
        if payment.payment_status == PaymentStatus.on_time:
            account_status = "11"  # Current account
            payment_rating = "0"   # Current
        else:
            # Positive-only policy: skip late payments, don't submit
            account_status = "11"
            payment_rating = "0"

        return Metro2Record(
            consumer_last_name=resident.last_name.upper()[:25],
            consumer_first_name=resident.first_name.upper()[:20],
            consumer_ssn=ssn or "",
            consumer_dob=dob_str,
            account_number=resident.id[:30],
            account_type=ACCOUNT_TYPE_RENTAL,
            date_opened=lease_start,
            credit_limit=resident.monthly_rent_cents // 100,
            highest_credit=resident.monthly_rent_cents // 100,
            scheduled_monthly_payment=resident.monthly_rent_cents // 100,
            actual_payment_amount=(payment.amount_paid_cents or 0) // 100,
            account_status=account_status,
            payment_rating=payment_rating,
            date_of_account_info=period_date,
            amount_past_due=0,
            current_balance=0,
        )

    def generate_metro2_file(
        self,
        residents_and_payments: list[tuple[Resident, RentPayment]],
        reporter_name: str = "RentReport LLC",
        reporter_id: str = "RNTCRD",
        cycle_identifier: str = "01",
    ) -> str:
        """Generate a complete Metro 2 formatted file as a string."""
        today = date.today().strftime("%m%d%Y")
        lines = [
            self.build_header(
                reporter_name=reporter_name,
                reporter_address="123 Main St",
                reporter_city_state_zip="Salt Lake City, UT 84101",
                reporter_phone="8005551234",
                reporter_id=reporter_id,
                cycle_identifier=cycle_identifier,
                program_date=today,
                program_revision_date=today,
            )
        ]

        for resident, payment in residents_and_payments:
            if payment.payment_status != PaymentStatus.on_time:
                continue  # Positive-only reporting policy
            record = self.build_record_from_payment(resident, payment)
            lines.append(record.to_metro2_line())

        lines.append(self.build_trailer(
            base_record_count=len(lines) - 1,  # Exclude header
        ))
        return "\n".join(lines)

    async def submit_to_bureau(
        self,
        bureau: str,
        file_content: str,
        filename: str,
    ) -> bool:
        """Submit Metro 2 file to credit bureau via SFTP."""
        bureau_config = {
            "experian": {
                "host": settings.EXPERIAN_FTP_HOST,
                "user": settings.EXPERIAN_FTP_USER,
                "password": settings.EXPERIAN_FTP_PASSWORD,
                "remote_path": f"/upload/{filename}",
            },
            "equifax": {
                "host": settings.EQUIFAX_FTP_HOST,
                "user": settings.EQUIFAX_FTP_USER,
                "password": settings.EQUIFAX_FTP_PASSWORD,
                "remote_path": f"/upload/{filename}",
            },
            "transunion": {
                "host": settings.TRANSUNION_FTP_HOST,
                "user": settings.TRANSUNION_FTP_USER,
                "password": settings.TRANSUNION_FTP_PASSWORD,
                "remote_path": f"/upload/{filename}",
            },
        }

        config = bureau_config.get(bureau)
        if not config or not config["host"]:
            raise ValueError(f"Bureau {bureau} not configured")

        transport = paramiko.Transport((config["host"], 22))
        transport.connect(username=config["user"], password=config["password"])
        sftp = paramiko.SFTPClient.from_transport(transport)
        try:
            with sftp.open(config["remote_path"], "w") as f:
                f.write(file_content)
            return True
        finally:
            sftp.close()
            transport.close()


metro2_service = Metro2Service()
