import hashlib
import hmac
import logging

import requests
from django.conf import settings

logger = logging.getLogger(__name__)


class PaymobService:
    """Service class for interacting with Paymob payment gateway."""

    BASE_URL = "https://accept.paymob.com/api"

    def __init__(self):
        self.api_key = settings.PAYMOB_API_KEY
        self.integration_id = settings.PAYMOB_INTEGRATION_ID
        self.iframe_id = settings.PAYMOB_IFRAME_ID
        self.hmac_secret = settings.PAYMOB_HMAC_SECRET

    def get_auth_token(self):
        """Get authentication token from Paymob."""
        url = f"{self.BASE_URL}/auth/tokens"
        payload = {"api_key": self.api_key}

        try:
            response = requests.post(url, json=payload, timeout=30)
            response.raise_for_status()
            return response.json().get("token")
        except requests.RequestException as e:
            logger.error(f"Failed to get Paymob auth token: {e}")
            raise

    def create_order(self, auth_token, amount_cents, order_id):
        """Create an order in Paymob."""
        url = f"{self.BASE_URL}/ecommerce/orders"
        payload = {
            "auth_token": auth_token,
            "delivery_needed": "false",
            "amount_cents": amount_cents,
            "currency": "EGP",
            "merchant_order_id": str(order_id),
            "items": [],
        }

        try:
            response = requests.post(url, json=payload, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Failed to create Paymob order: {e}")
            raise

    def get_payment_key(self, auth_token, order_id, amount_cents, billing_data):
        """Get payment key for the transaction."""
        url = f"{self.BASE_URL}/acceptance/payment_keys"
        payload = {
            "auth_token": auth_token,
            "amount_cents": amount_cents,
            "expiration": 3600,
            "order_id": order_id,
            "billing_data": billing_data,
            "currency": "EGP",
            "integration_id": self.integration_id,
        }

        try:
            response = requests.post(url, json=payload, timeout=30)
            response.raise_for_status()
            return response.json().get("token")
        except requests.RequestException as e:
            logger.error(f"Failed to get Paymob payment key: {e}")
            raise

    def initiate_payment(self, order, user):
        """Initiate a payment for an order."""
        amount_cents = int(order.total_amount * 100)

        auth_token = self.get_auth_token()

        paymob_order = self.create_order(auth_token, amount_cents, order.id)
        paymob_order_id = paymob_order.get("id")

        billing_data = {
            "apartment": "NA",
            "email": user.email,
            "floor": "NA",
            "first_name": user.first_name or "Customer",
            "street": order.shipping_address,
            "building": "NA",
            "phone_number": order.phone_number,
            "shipping_method": "NA",
            "postal_code": order.shipping_postal_code,
            "city": order.shipping_city,
            "country": order.shipping_country,
            "last_name": user.last_name or "Customer",
            "state": "NA",
        }

        payment_key = self.get_payment_key(
            auth_token, paymob_order_id, amount_cents, billing_data
        )

        iframe_url = f"https://accept.paymob.com/api/acceptance/iframes/{self.iframe_id}?payment_token={payment_key}"

        return {
            "paymob_order_id": paymob_order_id,
            "payment_key": payment_key,
            "iframe_url": iframe_url,
        }

    def verify_hmac(self, data, received_hmac):
        """Verify the HMAC signature from Paymob callback."""
        hmac_keys = [
            "amount_cents",
            "created_at",
            "currency",
            "error_occured",
            "has_parent_transaction",
            "id",
            "integration_id",
            "is_3d_secure",
            "is_auth",
            "is_capture",
            "is_refunded",
            "is_standalone_payment",
            "is_voided",
            "order",
            "owner",
            "pending",
            "source_data_pan",
            "source_data_sub_type",
            "source_data_type",
            "success",
        ]

        concatenated = "".join(str(data.get(key, "")) for key in hmac_keys)
        calculated_hmac = hmac.new(
            self.hmac_secret.encode(), concatenated.encode(), hashlib.sha512
        ).hexdigest()

        return hmac.compare_digest(calculated_hmac, received_hmac)
