from decimal import Decimal

import pytest
from django.urls import reverse

from products.models import Product


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
        brand="TestBrand",
        size="42",
        color="black",
        is_active=True,
    )


@pytest.mark.django_db
class TestProductList:
    def test_list_products_unauthenticated(self, api_client, product):
        """Test that products can be listed without authentication."""
        url = reverse("products:product-list")
        response = api_client.get(url)

        assert response.status_code == 200
        assert len(response.data["results"]) == 1
        assert response.data["results"][0]["name"] == product.name

    def test_list_products_authenticated(self, authenticated_client, product):
        """Test that products can be listed when authenticated."""
        url = reverse("products:product-list")
        response = authenticated_client.get(url)

        assert response.status_code == 200
        assert len(response.data["results"]) == 1


@pytest.mark.django_db
class TestProductDetail:
    def test_get_product_detail(self, api_client, product):
        """Test getting a single product's details."""
        url = reverse("products:product-detail", kwargs={"pk": product.pk})
        response = api_client.get(url)

        assert response.status_code == 200
        assert response.data["name"] == product.name
        assert Decimal(response.data["price"]) == product.price
        assert response.data["stock"] == product.stock


@pytest.mark.django_db
class TestProductCreate:
    def test_create_product_admin(self, admin_client):
        """Test that admin can create a product."""
        url = reverse("products:product-list")
        data = {
            "name": "New Shoe",
            "description": "A new shoe",
            "price": "149.99",
            "stock": 5,
            "category": "shoes",
            "brand": "NewBrand",
        }
        response = admin_client.post(url, data)

        assert response.status_code == 201
        assert Product.objects.filter(name="New Shoe").exists()

    def test_create_product_non_admin(self, authenticated_client):
        """Test that non-admin cannot create a product."""
        url = reverse("products:product-list")
        data = {
            "name": "New Shoe",
            "price": "149.99",
            "stock": 5,
        }
        response = authenticated_client.post(url, data)

        assert response.status_code == 403


@pytest.mark.django_db
class TestProductSearch:
    def test_search_products(self, api_client, product):
        """Test searching products."""
        url = reverse("products:product-list")
        response = api_client.get(url, {"search": "Test"})

        assert response.status_code == 200
        assert len(response.data["results"]) == 1

    def test_filter_products_by_category(self, api_client, product):
        """Test filtering products by category."""
        url = reverse("products:product-list")
        response = api_client.get(url, {"category": "shoes"})

        assert response.status_code == 200
        assert len(response.data["results"]) == 1
