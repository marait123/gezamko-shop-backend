import pytest
from django.urls import reverse
from decimal import Decimal

from products.models import Product
from orders.models import Order, OrderItem


@pytest.fixture
def product(db):
    """Create and return a test product."""
    return Product.objects.create(
        name="Test Shoe",
        description="A test shoe product",
        price=Decimal("99.99"),
        stock=10,
        sku="TEST-001",
        category="shoes",
        is_active=True,
    )


@pytest.fixture
def order(db, user, product):
    """Create and return a test order."""
    order = Order.objects.create(
        user=user,
        status=Order.Status.PENDING,
        total_amount=Decimal("99.99"),
        shipping_address="123 Test St",
        shipping_city="Test City",
        shipping_country="Test Country",
        shipping_postal_code="12345",
        phone_number="+1234567890",
    )
    OrderItem.objects.create(
        order=order,
        product=product,
        product_name=product.name,
        product_price=product.price,
        quantity=1,
    )
    return order


@pytest.mark.django_db
class TestOrderList:
    def test_list_orders_authenticated(self, authenticated_client, order):
        """Test listing orders for authenticated user."""
        url = reverse("orders:order-list")
        response = authenticated_client.get(url)

        assert response.status_code == 200
        assert len(response.data["results"]) == 1

    def test_list_orders_unauthenticated(self, api_client):
        """Test that unauthenticated users cannot list orders."""
        url = reverse("orders:order-list")
        response = api_client.get(url)

        assert response.status_code == 401


@pytest.mark.django_db
class TestOrderCreate:
    def test_create_order(self, authenticated_client, product):
        """Test creating an order."""
        url = reverse("orders:order-list")
        data = {
            "shipping_address": "456 New St",
            "shipping_city": "New City",
            "shipping_country": "New Country",
            "shipping_postal_code": "67890",
            "phone_number": "+9876543210",
            "items": [{"product_id": product.pk, "quantity": 2}],
        }
        response = authenticated_client.post(url, data, format="json")

        assert response.status_code == 201
        assert Order.objects.count() == 1

        order = Order.objects.first()
        assert order.total_amount == Decimal("199.98")

        product.refresh_from_db()
        assert product.stock == 8

    def test_create_order_insufficient_stock(self, authenticated_client, product):
        """Test creating order with insufficient stock."""
        product.stock = 1
        product.save()

        url = reverse("orders:order-list")
        data = {
            "shipping_address": "456 New St",
            "shipping_city": "New City",
            "shipping_country": "New Country",
            "shipping_postal_code": "67890",
            "phone_number": "+9876543210",
            "items": [{"product_id": product.pk, "quantity": 5}],
        }
        response = authenticated_client.post(url, data, format="json")

        assert response.status_code == 400


@pytest.mark.django_db
class TestOrderCancel:
    def test_cancel_order(self, authenticated_client, order, product):
        """Test cancelling an order."""
        initial_stock = product.stock
        url = reverse("orders:order-cancel", kwargs={"pk": order.pk})
        response = authenticated_client.post(url)

        assert response.status_code == 200
        order.refresh_from_db()
        assert order.status == Order.Status.CANCELLED

        product.refresh_from_db()
        assert product.stock == initial_stock + 1

    def test_cancel_non_pending_order(self, authenticated_client, order):
        """Test that non-pending orders cannot be cancelled."""
        order.status = Order.Status.SHIPPED
        order.save()

        url = reverse("orders:order-cancel", kwargs={"pk": order.pk})
        response = authenticated_client.post(url)

        assert response.status_code == 400
