import logging

from django.conf import settings
from rest_framework import authentication, exceptions
from keycloak import KeycloakOpenID

from .models import User

logger = logging.getLogger(__name__)


class KeycloakAuthentication(authentication.BaseAuthentication):
    """Keycloak token authentication for Django REST Framework."""

    def authenticate(self, request):
        auth_header = request.META.get("HTTP_AUTHORIZATION", "")

        if not auth_header.startswith("Bearer "):
            return None

        token = auth_header.split(" ")[1]

        try:
            keycloak_openid = KeycloakOpenID(
                server_url=settings.KEYCLOAK_SERVER_URL,
                client_id=settings.KEYCLOAK_CLIENT_ID,
                realm_name=settings.KEYCLOAK_REALM,
                client_secret_key=settings.KEYCLOAK_CLIENT_SECRET,
            )

            token_info = keycloak_openid.introspect(token)

            if not token_info.get("active"):
                raise exceptions.AuthenticationFailed("Token is invalid or expired")

            user_info = keycloak_openid.userinfo(token)
            user = self._get_or_create_user(user_info)

            return (user, token_info)

        except Exception as e:
            logger.error(f"Keycloak authentication error: {e}")
            raise exceptions.AuthenticationFailed(f"Authentication failed: {str(e)}")

    def _get_or_create_user(self, user_info):
        """Get or create a user based on Keycloak user info."""
        keycloak_id = user_info.get("sub")
        email = user_info.get("email", "")
        username = user_info.get("preferred_username", email)
        first_name = user_info.get("given_name", "")
        last_name = user_info.get("family_name", "")

        user, created = User.objects.update_or_create(
            keycloak_id=keycloak_id,
            defaults={
                "email": email,
                "username": username,
                "first_name": first_name,
                "last_name": last_name,
            },
        )

        if created:
            logger.info(f"Created new user from Keycloak: {username}")

        return user

    def authenticate_header(self, request):
        return "Bearer"
