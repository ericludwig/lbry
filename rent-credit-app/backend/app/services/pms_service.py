"""
Property Management Software (PMS) Integration Service.

Adapters for RealPage, Yardi, AppFolio, Entrata.
Each adapter implements a common interface:
  - get_residents(property_id) -> list of resident dicts
  - get_payment_ledger(resident_id, months) -> list of payment records
  - sync_residents(property_id) -> upsert residents into our DB
"""
import httpx
from abc import ABC, abstractmethod
from datetime import date, timedelta
from typing import Optional
from app.core.config import settings


class PMSResident(dict):
    """Normalized resident record from any PMS."""
    pass


class PMSPayment(dict):
    """Normalized payment record from any PMS."""
    pass


class BasePMSAdapter(ABC):

    @abstractmethod
    async def get_residents(self, property_id: str) -> list[PMSResident]:
        pass

    @abstractmethod
    async def get_payment_ledger(
        self,
        resident_id: str,
        months: int = 24,
    ) -> list[PMSPayment]:
        pass

    async def normalize_resident(self, raw: dict) -> PMSResident:
        raise NotImplementedError

    async def normalize_payment(self, raw: dict) -> PMSPayment:
        raise NotImplementedError


class RealPageAdapter(BasePMSAdapter):
    """
    RealPage API adapter.
    Docs: https://developer.realpage.com
    Uses OAuth2 client credentials flow.
    """

    BASE_URL = settings.REALPAGE_API_URL

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.client = httpx.AsyncClient(
            base_url=self.BASE_URL,
            headers={"Authorization": f"Bearer {api_key}", "Accept": "application/json"},
            timeout=30,
        )

    async def get_residents(self, property_id: str) -> list[PMSResident]:
        response = await self.client.get(f"/v2/properties/{property_id}/residents")
        response.raise_for_status()
        raw_list = response.json().get("residents", [])
        return [await self.normalize_resident(r) for r in raw_list]

    async def get_payment_ledger(self, resident_id: str, months: int = 24) -> list[PMSPayment]:
        response = await self.client.get(
            f"/v2/residents/{resident_id}/ledger",
            params={"months": months, "type": "rent"},
        )
        response.raise_for_status()
        raw_list = response.json().get("transactions", [])
        return [await self.normalize_payment(p) for p in raw_list]

    async def normalize_resident(self, raw: dict) -> PMSResident:
        return PMSResident(
            pms_resident_id=str(raw.get("residentId", "")),
            email=raw.get("email", ""),
            first_name=raw.get("firstName", ""),
            last_name=raw.get("lastName", ""),
            phone=raw.get("phone", ""),
            unit_number=raw.get("unitNumber", ""),
            lease_start_date=raw.get("leaseStartDate", ""),
            lease_end_date=raw.get("leaseEndDate", ""),
            monthly_rent_cents=int(float(raw.get("monthlyRent", 0)) * 100),
        )

    async def normalize_payment(self, raw: dict) -> PMSPayment:
        amount = float(raw.get("amount", 0))
        return PMSPayment(
            pms_transaction_id=str(raw.get("transactionId", "")),
            due_date=raw.get("dueDate", ""),
            paid_date=raw.get("paidDate", ""),
            amount_due_cents=int(amount * 100),
            amount_paid_cents=int(float(raw.get("paidAmount", 0)) * 100),
            is_on_time=raw.get("isOnTime", False),
        )


class YardiAdapter(BasePMSAdapter):
    """
    Yardi Voyager / RENTCafe API adapter.
    Uses SOAP/REST hybrid; we use their REST endpoints.
    """

    BASE_URL = settings.YARDI_API_URL

    def __init__(self, api_key: str, instance_url: Optional[str] = None):
        self.api_key = api_key
        base = instance_url or self.BASE_URL
        self.client = httpx.AsyncClient(
            base_url=base,
            headers={"X-Api-Key": api_key, "Accept": "application/json"},
            timeout=30,
        )

    async def get_residents(self, property_id: str) -> list[PMSResident]:
        response = await self.client.get(
            "/api/residents",
            params={"propertyCode": property_id, "status": "current"},
        )
        response.raise_for_status()
        return [await self.normalize_resident(r) for r in response.json().get("Residents", [])]

    async def get_payment_ledger(self, resident_id: str, months: int = 24) -> list[PMSPayment]:
        response = await self.client.get(
            "/api/ledger",
            params={"tenantCode": resident_id, "chargeCode": "RNT", "months": months},
        )
        response.raise_for_status()
        return [await self.normalize_payment(p) for p in response.json().get("Transactions", [])]

    async def normalize_resident(self, raw: dict) -> PMSResident:
        return PMSResident(
            pms_resident_id=raw.get("TenantCode", ""),
            email=raw.get("Email", ""),
            first_name=raw.get("FirstName", ""),
            last_name=raw.get("LastName", ""),
            phone=raw.get("Phone", ""),
            unit_number=raw.get("UnitID", ""),
            lease_start_date=raw.get("LeaseFromDate", ""),
            lease_end_date=raw.get("LeaseToDate", ""),
            monthly_rent_cents=int(float(raw.get("Rent", 0)) * 100),
        )

    async def normalize_payment(self, raw: dict) -> PMSPayment:
        due = raw.get("TransDate", "")
        paid = raw.get("PostDate", "") if raw.get("Paid") else None
        return PMSPayment(
            pms_transaction_id=raw.get("TransactionID", ""),
            due_date=due,
            paid_date=paid,
            amount_due_cents=int(float(raw.get("Amount", 0)) * 100),
            amount_paid_cents=int(float(raw.get("PaidAmount", 0)) * 100),
            is_on_time=raw.get("PaidOnTime", False),
        )


class AppFolioAdapter(BasePMSAdapter):
    """
    AppFolio Property Manager API adapter.
    Uses OAuth2. Documented at https://developer.appfolio.com
    """

    BASE_URL = settings.APPFOLIO_API_URL

    def __init__(self, client_id: str, client_secret: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self._access_token: Optional[str] = None
        self.client = httpx.AsyncClient(base_url=self.BASE_URL, timeout=30)

    async def _get_token(self) -> str:
        if self._access_token:
            return self._access_token
        response = await self.client.post(
            "/oauth2/token",
            data={
                "grant_type": "client_credentials",
                "client_id": self.client_id,
                "client_secret": self.client_secret,
            },
        )
        response.raise_for_status()
        self._access_token = response.json()["access_token"]
        return self._access_token

    async def get_residents(self, property_id: str) -> list[PMSResident]:
        token = await self._get_token()
        response = await self.client.get(
            "/api/v1/listings/residential_listings.json",
            headers={"Authorization": f"Bearer {token}"},
            params={"property_id": property_id, "status": "current_resident"},
        )
        response.raise_for_status()
        return [await self.normalize_resident(r) for r in response.json().get("results", [])]

    async def get_payment_ledger(self, resident_id: str, months: int = 24) -> list[PMSPayment]:
        token = await self._get_token()
        response = await self.client.get(
            "/api/v1/accounting/general_ledger_entries.json",
            headers={"Authorization": f"Bearer {token}"},
            params={"tenant_id": resident_id, "account_type": "Rent", "months": months},
        )
        response.raise_for_status()
        return [await self.normalize_payment(p) for p in response.json().get("results", [])]

    async def normalize_resident(self, raw: dict) -> PMSResident:
        tenant = raw.get("tenant", {})
        return PMSResident(
            pms_resident_id=str(raw.get("id", "")),
            email=tenant.get("email", ""),
            first_name=tenant.get("first_name", ""),
            last_name=tenant.get("last_name", ""),
            phone=tenant.get("phone_number", ""),
            unit_number=raw.get("unit", {}).get("name", ""),
            lease_start_date=raw.get("lease_start_date", ""),
            lease_end_date=raw.get("lease_end_date", ""),
            monthly_rent_cents=int(float(raw.get("rent", 0)) * 100),
        )

    async def normalize_payment(self, raw: dict) -> PMSPayment:
        return PMSPayment(
            pms_transaction_id=str(raw.get("id", "")),
            due_date=raw.get("due_date", ""),
            paid_date=raw.get("cleared_date", ""),
            amount_due_cents=int(float(raw.get("amount", 0)) * 100),
            amount_paid_cents=int(float(raw.get("paid_amount", 0)) * 100),
            is_on_time=raw.get("paid_on_time", False),
        )


class EntrataAdapter(BasePMSAdapter):
    """
    Entrata platform API adapter.
    """

    BASE_URL = settings.ENTRATA_API_URL

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.client = httpx.AsyncClient(
            base_url=self.BASE_URL,
            headers={"Authorization": f"Bearer {api_key}", "Accept": "application/json"},
            timeout=30,
        )

    async def get_residents(self, property_id: str) -> list[PMSResident]:
        response = await self.client.post(
            "/api/v1",
            json={
                "auth": {"type": "apikey", "apikey": self.api_key},
                "requestId": "1",
                "method": {"name": "getResidents", "params": {"propertyId": property_id}},
            },
        )
        response.raise_for_status()
        raw_list = response.json().get("response", {}).get("result", {}).get("Customers", [])
        return [await self.normalize_resident(r) for r in raw_list]

    async def get_payment_ledger(self, resident_id: str, months: int = 24) -> list[PMSPayment]:
        response = await self.client.post(
            "/api/v1",
            json={
                "auth": {"type": "apikey", "apikey": self.api_key},
                "requestId": "1",
                "method": {
                    "name": "getCustomerLedger",
                    "params": {"customerId": resident_id, "months": months},
                },
            },
        )
        response.raise_for_status()
        raw_list = response.json().get("response", {}).get("result", {}).get("Transactions", [])
        return [await self.normalize_payment(p) for p in raw_list]

    async def normalize_resident(self, raw: dict) -> PMSResident:
        return PMSResident(
            pms_resident_id=str(raw.get("customerId", "")),
            email=raw.get("email", ""),
            first_name=raw.get("firstName", ""),
            last_name=raw.get("lastName", ""),
            phone=raw.get("phone", ""),
            unit_number=raw.get("spaceId", ""),
            lease_start_date=raw.get("leaseStartDate", ""),
            lease_end_date=raw.get("leaseEndDate", ""),
            monthly_rent_cents=int(float(raw.get("monthlyRent", 0)) * 100),
        )

    async def normalize_payment(self, raw: dict) -> PMSPayment:
        return PMSPayment(
            pms_transaction_id=str(raw.get("transactionId", "")),
            due_date=raw.get("dueDate", ""),
            paid_date=raw.get("paidDate", ""),
            amount_due_cents=int(float(raw.get("chargeAmount", 0)) * 100),
            amount_paid_cents=int(float(raw.get("paidAmount", 0)) * 100),
            is_on_time=raw.get("paidOnTime", False),
        )


class MockPMSAdapter(BasePMSAdapter):
    """Stub adapter for development/testing."""

    async def get_residents(self, property_id: str) -> list[PMSResident]:
        return [
            PMSResident(
                pms_resident_id="mock-res-001",
                email="resident@example.com",
                first_name="Jane",
                last_name="Smith",
                phone="555-1234",
                unit_number="101",
                lease_start_date="2024-01-01",
                lease_end_date="2024-12-31",
                monthly_rent_cents=150000,
            )
        ]

    async def get_payment_ledger(self, resident_id: str, months: int = 24) -> list[PMSPayment]:
        from datetime import datetime
        records = []
        today = date.today()
        for i in range(min(months, 12)):
            period_start = date(today.year, today.month, 1) - timedelta(days=30 * i)
            records.append(PMSPayment(
                pms_transaction_id=f"mock-txn-{i}",
                due_date=str(period_start),
                paid_date=str(period_start + timedelta(days=1)),
                amount_due_cents=150000,
                amount_paid_cents=150000,
                is_on_time=True,
            ))
        return records


def get_pms_adapter(pms_type: str, **kwargs) -> BasePMSAdapter:
    adapters = {
        "realpage": lambda: RealPageAdapter(kwargs.get("api_key", "")),
        "yardi": lambda: YardiAdapter(kwargs.get("api_key", ""), kwargs.get("instance_url")),
        "appfolio": lambda: AppFolioAdapter(kwargs.get("client_id", ""), kwargs.get("client_secret", "")),
        "entrata": lambda: EntrataAdapter(kwargs.get("api_key", "")),
        "manual": lambda: MockPMSAdapter(),
    }
    factory = adapters.get(pms_type, adapters["manual"])
    return factory()
