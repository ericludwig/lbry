"""
Stripe service for:
- Resident subscriptions ($8.95/month)
- Stripe Connect onboarding for property managers
- Revenue share payouts ($3.00/month per enrolled resident) via Stripe Connect
"""
import stripe
from typing import Optional
from app.core.config import settings

stripe.api_key = settings.STRIPE_SECRET_KEY


class StripeService:

    # -------------------------
    # Resident Subscription
    # -------------------------

    async def create_customer(self, email: str, name: str, metadata: dict = None) -> stripe.Customer:
        return stripe.Customer.create(
            email=email,
            name=name,
            metadata=metadata or {},
        )

    async def create_subscription(
        self,
        customer_id: str,
        price_id: str,
        trial_days: int = 30,
        metadata: dict = None,
    ) -> stripe.Subscription:
        return stripe.Subscription.create(
            customer=customer_id,
            items=[{"price": price_id}],
            trial_period_days=trial_days,
            payment_behavior="default_incomplete",
            payment_settings={"save_default_payment_method": "on_subscription"},
            expand=["latest_invoice.payment_intent"],
            metadata=metadata or {},
        )

    async def create_setup_intent(self, customer_id: str) -> stripe.SetupIntent:
        """Returns client_secret for collecting payment method before trial ends."""
        return stripe.SetupIntent.create(
            customer=customer_id,
            payment_method_types=["card"],
            usage="off_session",
        )

    async def cancel_subscription(self, subscription_id: str) -> stripe.Subscription:
        return stripe.Subscription.cancel(subscription_id)

    async def get_subscription(self, subscription_id: str) -> stripe.Subscription:
        return stripe.Subscription.retrieve(subscription_id)

    # -------------------------
    # Stripe Connect (PM Payouts)
    # -------------------------

    async def create_connect_account(self, email: str, company_name: str) -> stripe.Account:
        """Create a Stripe Express account for a property manager."""
        return stripe.Account.create(
            type="express",
            email=email,
            business_profile={"name": company_name},
            capabilities={
                "transfers": {"requested": True},
            },
        )

    async def create_account_link(
        self,
        account_id: str,
        refresh_url: str,
        return_url: str,
    ) -> stripe.AccountLink:
        """Get onboarding link for property manager to complete Stripe Express setup."""
        return stripe.AccountLink.create(
            account=account_id,
            refresh_url=refresh_url,
            return_url=return_url,
            type="account_onboarding",
        )

    async def get_account(self, account_id: str) -> stripe.Account:
        return stripe.Account.retrieve(account_id)

    async def create_payout_to_pm(
        self,
        connected_account_id: str,
        amount_cents: int,
        description: str,
        metadata: dict = None,
    ) -> stripe.Transfer:
        """Transfer revenue share to property manager's connected account."""
        return stripe.Transfer.create(
            amount=amount_cents,
            currency="usd",
            destination=connected_account_id,
            description=description,
            metadata=metadata or {},
        )

    # -------------------------
    # Webhook Handling
    # -------------------------

    def construct_event(self, payload: bytes, sig_header: str) -> stripe.Event:
        return stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )

    async def handle_subscription_event(self, event: stripe.Event) -> dict:
        """Route Stripe webhook events to appropriate handlers."""
        event_type = event["type"]
        subscription = event["data"]["object"]

        if event_type == "customer.subscription.trial_will_end":
            return {"action": "notify_trial_ending", "subscription_id": subscription["id"]}

        elif event_type == "customer.subscription.deleted":
            return {"action": "deactivate_subscription", "subscription_id": subscription["id"]}

        elif event_type == "invoice.payment_succeeded":
            return {"action": "payment_succeeded", "subscription_id": subscription.get("subscription")}

        elif event_type == "invoice.payment_failed":
            return {"action": "payment_failed", "subscription_id": subscription.get("subscription")}

        return {"action": "unknown"}


stripe_service = StripeService()
