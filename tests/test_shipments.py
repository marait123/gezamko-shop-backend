from decimal import Decimal

import pytest
from django.urls import reverse

from orders.models import Order
from shipments.models import Shipment


@pytest.fixture
def order(db, user):
    """Create and return a test order."""
    return Order.objects.create(
        user=user,
        status=Order.Status.CONFIRMED,
        total_amount=Decimal("99.99"),
        shipping_address="123 Test St",
        shipping_city="Test City",
        shipping_country="Test Country",
        shipping_postal_code="12345",
        phone_number="+1234567890",
    )


@pytest.fixture
def shipment(db, order):
    """Create and return a test shipment."""
    return Shipment.objects.create(
        order=order,
        status=Shipment.Status.PENDING,
        shipping_method=Shipment.Method.STANDARD,
        tracking_number="TEST-123456",
        shipping_address=order.shipping_address,
        shipping_city=order.shipping_city,
        shipping_country=order.shipping_country,
        shipping_postal_code=order.shipping_postal_code,
        recipient_name="Test User",
        recipient_phone=order.phone_number,
    )


@pytest.mark.django_db
class TestShipmentList:
    def test_list_shipments_authenticated(self, authenticated_client, shipment):
        """Test listing shipments for authenticated user."""
        url = reverse("shipments:shipment-list")
        response = authenticated_client.get(url)

        assert response.status_code == 200
        assert len(response.data["results"]) == 1

    def test_list_shipments_unauthenticated(self, api_client):
        """Test that unauthenticated users cannot list shipments."""
        url = reverse("shipments:shipment-list")
        response = api_client.get(url)

        assert response.status_code == 401


@pytest.mark.django_db
class TestShipmentDetail:
    def test_get_shipment_detail(self, authenticated_client, shipment):
        """Test getting shipment details."""
        url = reverse("shipments:shipment-detail", kwargs={"pk": shipment.pk})
        response = authenticated_client.get(url)

        assert response.status_code == 200
        assert response.data["tracking_number"] == shipment.tracking_number


@pytest.mark.django_db
class TestShipmentCreate:
    def test_create_shipment_admin(self, admin_client, order):
        """Test that admin can create a shipment."""
        url = reverse("shipments:shipment-list")
        data = {
            "order_id": order.pk,
            "shipping_method": "standard",
            "recipient_name": "Test User",
            "recipient_phone": "+1234567890",
        }
        response = admin_client.post(url, data)

        assert response.status_code == 201
        assert Shipment.objects.count() == 1

    def test_create_shipment_non_admin(self, authenticated_client, order):
        """Test that non-admin cannot create a shipment."""
        url = reverse("shipments:shipment-list")
        data = {
            "order_id": order.pk,
            "shipping_method": "standard",
            "recipient_name": "Test User",
            "recipient_phone": "+1234567890",
        }
        response = authenticated_client.post(url, data)

        assert response.status_code == 403


@pytest.mark.django_db
class TestShipmentTracking:
    def test_get_tracking_info(self, authenticated_client, shipment):
        """Test getting tracking information."""
        url = reverse("shipments:shipment-tracking", kwargs={"pk": shipment.pk})
        response = authenticated_client.get(url)

        assert response.status_code == 200
        assert response.data["tracking_number"] == shipment.tracking_number


@pytest.mark.django_db
class TestShipmentRates:
    def test_get_shipping_rates(self, authenticated_client):
        """Test getting shipping rates."""
        url = reverse("shipments:shipment-rates")
        data = {
            "destination": {"city": "Test City", "country": "Test Country"},
            "weight": 1.5,
        }
        response = authenticated_client.post(url, data, format="json")

        assert response.status_code == 200
        assert "rates" in response.data
