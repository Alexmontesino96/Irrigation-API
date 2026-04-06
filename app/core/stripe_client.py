import logging
import os

logger = logging.getLogger(__name__)


class StripeClient:
    def __init__(self):
        self.secret_key = os.getenv("STRIPE_SECRET_KEY")
        self.webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET")
        self._stripe = None

    @property
    def is_configured(self) -> bool:
        return bool(self.secret_key)

    def _get_stripe(self):
        if self._stripe is None:
            if not self.is_configured:
                logger.warning("Stripe not configured.")
                return None
            try:
                import stripe
                stripe.api_key = self.secret_key
                self._stripe = stripe
            except ImportError:
                logger.warning("stripe package not installed.")
                return None
        return self._stripe

    def create_customer(self, email: str, name: str) -> str | None:
        stripe = self._get_stripe()
        if not stripe:
            return None
        customer = stripe.Customer.create(email=email, name=name)
        return customer.id

    def create_checkout_session(self, customer_id: str, price_id: str, success_url: str, cancel_url: str) -> str | None:
        stripe = self._get_stripe()
        if not stripe:
            return None
        session = stripe.checkout.Session.create(
            customer=customer_id,
            payment_method_types=["card"],
            line_items=[{"price": price_id, "quantity": 1}],
            mode="subscription",
            success_url=success_url,
            cancel_url=cancel_url,
        )
        return session.url

    def create_portal_session(self, customer_id: str) -> str | None:
        stripe = self._get_stripe()
        if not stripe:
            return None
        session = stripe.billing_portal.Session.create(customer=customer_id)
        return session.url

    def verify_webhook(self, payload: bytes, sig_header: str):
        stripe = self._get_stripe()
        if not stripe or not self.webhook_secret:
            return None
        return stripe.Webhook.construct_event(payload, sig_header, self.webhook_secret)


stripe_client = StripeClient()
