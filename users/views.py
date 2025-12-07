from drf_spectacular.utils import extend_schema
from rest_framework import generics, permissions

from .models import User
from .serializers import UserProfileUpdateSerializer, UserSerializer


class UserProfileView(generics.RetrieveUpdateAPIView):
    """View for retrieving and updating the current user's profile."""

    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

    def get_serializer_class(self):
        if self.request.method in ["PUT", "PATCH"]:
            return UserProfileUpdateSerializer
        return UserSerializer

    @extend_schema(
        summary="Get current user profile",
        description="Retrieve the profile of the currently authenticated user.",
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @extend_schema(
        summary="Update current user profile",
        description="Update the profile of the currently authenticated user.",
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    @extend_schema(
        summary="Partially update current user profile",
        description="Partially update the profile of the currently authenticated user.",
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)


class UserListView(generics.ListAPIView):
    """View for listing all users (admin only)."""

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]

    @extend_schema(
        summary="List all users",
        description="List all users in the system. Admin access required.",
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class UserDetailView(generics.RetrieveAPIView):
    """View for retrieving a specific user (admin only)."""

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]

    @extend_schema(
        summary="Get user details",
        description="Retrieve details of a specific user. Admin access required.",
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
