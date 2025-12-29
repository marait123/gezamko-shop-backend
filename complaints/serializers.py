from rest_framework import serializers

from .models import Complaint, ComplaintResponse


class ComplaintResponseSerializer(serializers.ModelSerializer):
    """Serializer for complaint responses."""

    user_email = serializers.CharField(source="user.email", read_only=True)

    class Meta:
        model = ComplaintResponse
        fields = [
            "id",
            "user",
            "user_email",
            "message",
            "is_staff_response",
            "created_at",
        ]
        read_only_fields = ["id", "user", "is_staff_response", "created_at"]


class ComplaintSerializer(serializers.ModelSerializer):
    """Serializer for complaints."""

    responses = ComplaintResponseSerializer(many=True, read_only=True)
    user_email = serializers.CharField(source="user.email", read_only=True)
    assigned_to_email = serializers.CharField(source="assigned_to.email", read_only=True, allow_null=True)

    class Meta:
        model = Complaint
        fields = [
            "id",
            "user",
            "user_email",
            "order",
            "subject",
            "description",
            "category",
            "status",
            "priority",
            "assigned_to",
            "assigned_to_email",
            "resolution",
            "responses",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "user",
            "status",
            "assigned_to",
            "resolution",
            "created_at",
            "updated_at",
        ]


class ComplaintCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating complaints."""

    class Meta:
        model = Complaint
        fields = ["order", "subject", "description", "category"]

    def validate_order(self, value):
        if value:
            user = self.context["request"].user
            if value.user != user and not user.is_staff:
                raise serializers.ValidationError("You can only create complaints for your own orders")
        return value


class ComplaintUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating complaints (admin only)."""

    class Meta:
        model = Complaint
        fields = ["status", "priority", "assigned_to", "resolution"]


class ComplaintResponseCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating complaint responses."""

    class Meta:
        model = ComplaintResponse
        fields = ["message"]
