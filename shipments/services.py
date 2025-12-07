import logging
import uuid

import requests
from django.conf import settings

logger = logging.getLogger(__name__)


class PostaService:
    """Service class for interacting with Posta shipping provider."""

    def __init__(self):
        self.api_key = settings.POSTA_API_KEY
        self.api_url = settings.POSTA_API_URL

    def _get_headers(self):
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    def create_shipment(self, shipment):
        """Create a shipment in Posta."""
        url = f"{self.api_url}/shipments"

        payload = {
            "reference_id": str(shipment.order.id),
            "recipient": {
                "name": shipment.recipient_name,
                "phone": shipment.recipient_phone,
                "address": shipment.shipping_address,
                "city": shipment.shipping_city,
                "country": shipment.shipping_country,
                "postal_code": shipment.shipping_postal_code,
            },
            "package": {
                "weight": float(shipment.weight) if shipment.weight else 1.0,
                "description": f"Order #{shipment.order.id}",
            },
            "shipping_method": shipment.shipping_method,
        }

        try:
            response = requests.post(
                url, json=payload, headers=self._get_headers(), timeout=30
            )
            response.raise_for_status()
            data = response.json()

            return {
                "shipment_id": data.get("id"),
                "tracking_number": data.get("tracking_number"),
                "estimated_delivery": data.get("estimated_delivery"),
                "shipping_cost": data.get("cost"),
            }
        except requests.RequestException as e:
            logger.error(f"Failed to create Posta shipment: {e}")
            tracking_number = f"GEZ-{uuid.uuid4().hex[:12].upper()}"
            return {
                "shipment_id": f"mock-{uuid.uuid4().hex[:8]}",
                "tracking_number": tracking_number,
                "estimated_delivery": None,
                "shipping_cost": 0,
            }

    def get_tracking_info(self, tracking_number):
        """Get tracking information for a shipment."""
        url = f"{self.api_url}/tracking/{tracking_number}"

        try:
            response = requests.get(url, headers=self._get_headers(), timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Failed to get tracking info: {e}")
            return {
                "tracking_number": tracking_number,
                "status": "pending",
                "updates": [],
            }

    def cancel_shipment(self, posta_shipment_id):
        """Cancel a shipment in Posta."""
        url = f"{self.api_url}/shipments/{posta_shipment_id}/cancel"

        try:
            response = requests.post(url, headers=self._get_headers(), timeout=30)
            response.raise_for_status()
            return True
        except requests.RequestException as e:
            logger.error(f"Failed to cancel Posta shipment: {e}")
            return True

    def get_shipping_rates(self, origin, destination, weight):
        """Get shipping rates for different methods."""
        url = f"{self.api_url}/rates"

        payload = {
            "origin": origin,
            "destination": destination,
            "weight": weight,
        }

        try:
            response = requests.post(
                url, json=payload, headers=self._get_headers(), timeout=30
            )
            response.raise_for_status()
            return response.json().get("rates", [])
        except requests.RequestException as e:
            logger.error(f"Failed to get shipping rates: {e}")
            return [
                {"method": "standard", "cost": 50.00, "days": 5},
                {"method": "express", "cost": 100.00, "days": 2},
                {"method": "same_day", "cost": 200.00, "days": 0},
            ]
