import pytest
from django.urls import reverse
from decimal import Decimal
from unittest.mock import patch, MagicMock

from orders.models import Order
from payments.models import Payment


@pytest.fixture
def order(db, user):
    """Create and return a test order."""
    return Order.objects.create(
        user=user,
        status=Order.Status.PENDING,
        total_amount=Decimal("99.99"),
        shipping_address="123 Test St",
        shipping_city="Test City",
        shipping_country="Test Country",
        shipping_postal_code="12345",
        phone_number="+1234567890",
    )


@pytest.fixture
def payment(db, order):
    """Create and return a test payment."""
    return Payment.objects.create(
        order=order,
        payment_method=Payment.Method.CARD,
        amount=order.total_amount,
        status=Payment.Status.PENDING,
    )


@pytest.mark.django_db
class TestPaymentList:
    def test_list_payments_authenticated(self, authenticated_client, payment):
        """Test listing payments for authenticated user."""
        url = reverse("payments:payment-list")
        response = authenticated_client.get(url)

        assert response.status_code == 200
        assert len(response.data["results"]) == 1

    def test_list_payments_unauthenticated(self, api_client):
        """Test that unauthenticated users cannot list payments."""
        url = reverse("payments:payment-list")
        response = api_client.get(url)

        assert response.status_code == 401


@pytest.mark.django_db
class TestPaymentInitiate:
    def test_initiate_cash_payment(self, authenticated_client, order):
        """Test initiating a cash on delivery payment."""
        url = reverse("payments:payment-initiate")
        data = {
            "order_id": order.pk,
            "payment_method": "cash",
        }
        response = authenticated_client.post(url, data)

        assert response.status_code == 200
        assert "payment_id" in response.data
        assert Payment.objects.count() == 1
        assert Payment.objects.first().status == Payment.Status.PROCESSING

    def test_initiate_payment_wrong_order(self, authenticated_client, admin_user):
        """Test initiating payment for another user's order fails."""
        other_order = Order.objects.create(
            user=admin_user,
            status=Order.Status.PENDING,
            total_amount=Decimal("99.99"),
            shipping_address="123 Test St",
            shipping_city="Test City",
            shipping_country="Test Country",
            shipping_postal_code="12345",
            phone_number="+1234567890",
        )
        url = reverse("payments:payment-initiate")
        data = {
            "order_id": other_order.pk,
            "payment_method": "card",
        }
        response = authenticated_client.post(url, data)

        assert response.status_code == 404

    def test_initiate_payment_non_pending_order(self, authenticated_client, order):
        """Test initiating payment for non-pending order fails."""
        order.status = Order.Status.SHIPPED
        order.save()

        url = reverse("payments:payment-initiate")
        data = {
            "order_id": order.pk,
            "payment_method": "card",
        }
        response = authenticated_client.post(url, data)

        assert response.status_code == 400

    def test_initiate_payment_already_in_progress(self, authenticated_client, order, payment):
        """Test initiating payment when one already in progress fails."""
        url = reverse("payments:payment-initiate")
        data = {
            "order_id": order.pk,
            "payment_method": "card",
        }
        response = authenticated_client.post(url, data)

        assert response.status_code == 400
