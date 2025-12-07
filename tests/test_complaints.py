from decimal import Decimal

import pytest
from django.urls import reverse

from complaints.models import Complaint
from orders.models import Order, OrderItem
from products.models import Product


@pytest.fixture
def order(db, user):
    """Create and return a test order."""
    return Order.objects.create(
        user=user,
        status=Order.Status.DELIVERED,
        total_amount=Decimal("99.99"),
        shipping_address="123 Test St",
        shipping_city="Test City",
        shipping_country="Test Country",
        shipping_postal_code="12345",
        phone_number="+1234567890",
    )


@pytest.fixture
def complaint(db, user, order):
    """Create and return a test complaint."""
    return Complaint.objects.create(
        user=user,
        order=order,
        subject="Test Complaint",
        description="This is a test complaint description.",
        category=Complaint.Category.ORDER,
        status=Complaint.Status.OPEN,
        priority=Complaint.Priority.MEDIUM,
    )


@pytest.mark.django_db
class TestComplaintList:
    def test_list_complaints_authenticated(self, authenticated_client, complaint):
        """Test listing complaints for authenticated user."""
        url = reverse("complaints:complaint-list")
        response = authenticated_client.get(url)

        assert response.status_code == 200
        assert len(response.data["results"]) == 1

    def test_list_complaints_unauthenticated(self, api_client):
        """Test that unauthenticated users cannot list complaints."""
        url = reverse("complaints:complaint-list")
        response = api_client.get(url)

        assert response.status_code == 401


@pytest.mark.django_db
class TestComplaintCreate:
    def test_create_complaint(self, authenticated_client, order):
        """Test creating a complaint."""
        url = reverse("complaints:complaint-list")
        data = {
            "order": order.pk,
            "subject": "New Complaint",
            "description": "Description of the new complaint.",
            "category": "order",
        }
        response = authenticated_client.post(url, data)

        assert response.status_code == 201
        assert Complaint.objects.count() == 1
        assert Complaint.objects.first().subject == "New Complaint"

    def test_create_complaint_without_order(self, authenticated_client):
        """Test creating a complaint without an associated order."""
        url = reverse("complaints:complaint-list")
        data = {
            "subject": "General Complaint",
            "description": "A general complaint without an order.",
            "category": "other",
        }
        response = authenticated_client.post(url, data)

        assert response.status_code == 201


@pytest.mark.django_db
class TestComplaintRespond:
    def test_respond_to_complaint(self, authenticated_client, complaint):
        """Test responding to a complaint."""
        url = reverse("complaints:complaint-respond", kwargs={"pk": complaint.pk})
        data = {"message": "This is my response to the complaint."}
        response = authenticated_client.post(url, data)

        assert response.status_code == 200
        assert complaint.responses.count() == 1

    def test_staff_respond_to_complaint(self, admin_client, complaint):
        """Test staff responding to a complaint."""
        url = reverse("complaints:complaint-respond", kwargs={"pk": complaint.pk})
        data = {"message": "Staff response to the complaint."}
        response = admin_client.post(url, data)

        assert response.status_code == 200
        assert complaint.responses.first().is_staff_response is True


@pytest.mark.django_db
class TestComplaintClose:
    def test_close_own_complaint(self, authenticated_client, complaint):
        """Test closing own complaint."""
        url = reverse("complaints:complaint-close", kwargs={"pk": complaint.pk})
        response = authenticated_client.post(url)

        assert response.status_code == 200
        complaint.refresh_from_db()
        assert complaint.status == Complaint.Status.CLOSED


@pytest.mark.django_db
class TestComplaintResolve:
    def test_resolve_complaint_admin(self, admin_client, complaint):
        """Test admin resolving a complaint."""
        url = reverse("complaints:complaint-resolve", kwargs={"pk": complaint.pk})
        data = {"resolution": "Issue has been resolved."}
        response = admin_client.post(url, data)

        assert response.status_code == 200
        complaint.refresh_from_db()
        assert complaint.status == Complaint.Status.RESOLVED
        assert complaint.resolution == "Issue has been resolved."

    def test_resolve_complaint_non_admin(self, authenticated_client, complaint):
        """Test that non-admin cannot resolve complaints."""
        url = reverse("complaints:complaint-resolve", kwargs={"pk": complaint.pk})
        data = {"resolution": "Issue has been resolved."}
        response = authenticated_client.post(url, data)

        assert response.status_code == 403
