import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.mark.django_db
class TestUserProfile:
    def test_get_profile_authenticated(self, authenticated_client, user):
        """Test getting user profile when authenticated."""
        url = reverse("users:profile")
        response = authenticated_client.get(url)

        assert response.status_code == 200
        assert response.data["email"] == user.email
        assert response.data["username"] == user.username

    def test_get_profile_unauthenticated(self, api_client):
        """Test getting profile fails when unauthenticated."""
        url = reverse("users:profile")
        response = api_client.get(url)

        assert response.status_code == 401

    def test_update_profile(self, authenticated_client, user):
        """Test updating user profile."""
        url = reverse("users:profile")
        data = {
            "first_name": "Updated",
            "last_name": "Name",
            "phone_number": "+1234567890",
        }
        response = authenticated_client.patch(url, data)

        assert response.status_code == 200
        user.refresh_from_db()
        assert user.first_name == "Updated"
        assert user.last_name == "Name"
        assert user.phone_number == "+1234567890"


@pytest.mark.django_db
class TestUserList:
    def test_list_users_admin(self, admin_client):
        """Test that admin can list all users."""
        url = reverse("users:user-list")
        response = admin_client.get(url)

        assert response.status_code == 200

    def test_list_users_non_admin(self, authenticated_client):
        """Test that non-admin cannot list all users."""
        url = reverse("users:user-list")
        response = authenticated_client.get(url)

        assert response.status_code == 403
