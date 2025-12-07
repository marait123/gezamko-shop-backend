from rest_framework import serializers

from .models import User


class UserSerializer(serializers.ModelSerializer):
    """Serializer for the User model."""

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "role",
            "first_name",
            "last_name",
            "phone_number",
            "address",
            "city",
            "country",
            "postal_code",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "username",
            "email",
            "role",
            "created_at",
            "updated_at",
        ]


class UserProfileUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating user profile."""

    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "phone_number",
            "address",
            "city",
            "country",
            "postal_code",
        ]


class UserCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating users (admin only)."""

    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "password",
            "role",
            "first_name",
            "last_name",
            "phone_number",
        ]

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class UserAdminUpdateSerializer(serializers.ModelSerializer):
    """Serializer for admin to update users."""

    class Meta:
        model = User
        fields = [
            "role",
            "first_name",
            "last_name",
            "phone_number",
            "address",
            "city",
            "country",
            "postal_code",
            "is_active",
        ]
