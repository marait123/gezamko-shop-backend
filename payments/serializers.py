from rest_framework import serializers

from .models import Payment


class PaymentSerializer(serializers.ModelSerializer):
    """Serializer for payments."""

    order_id = serializers.IntegerField(source="order.id", read_only=True)

    class Meta:
        model = Payment
        fields = [
            "id",
            "order_id",
            "payment_method",
            "amount",
            "status",
            "transaction_id",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "amount", "status", "transaction_id", "created_at", "updated_at"]


class PaymentInitiateSerializer(serializers.Serializer):
    """Serializer for initiating a payment."""

    order_id = serializers.IntegerField()
    payment_method = serializers.ChoiceField(choices=Payment.Method.choices)


class PaymentCallbackSerializer(serializers.Serializer):
    """Serializer for Paymob callback data."""

    id = serializers.IntegerField()
    pending = serializers.BooleanField()
    amount_cents = serializers.IntegerField()
    success = serializers.BooleanField()
    is_auth = serializers.BooleanField()
    is_capture = serializers.BooleanField()
    is_standalone_payment = serializers.BooleanField()
    is_voided = serializers.BooleanField()
    is_refunded = serializers.BooleanField()
    is_3d_secure = serializers.BooleanField()
    integration_id = serializers.IntegerField()
    has_parent_transaction = serializers.BooleanField()
    order = serializers.IntegerField()
    created_at = serializers.CharField()
    currency = serializers.CharField()
    error_occured = serializers.BooleanField()
    owner = serializers.IntegerField()
    source_data_pan = serializers.CharField(required=False, allow_blank=True)
    source_data_sub_type = serializers.CharField(required=False, allow_blank=True)
    source_data_type = serializers.CharField(required=False, allow_blank=True)
