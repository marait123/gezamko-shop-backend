from rest_framework import serializers

from .models import Shipment, ShipmentTracking


class ShipmentTrackingSerializer(serializers.ModelSerializer):
    """Serializer for shipment tracking updates."""

    class Meta:
        model = ShipmentTracking
        fields = ["id", "status", "location", "description", "timestamp"]
        read_only_fields = ["id"]


class ShipmentSerializer(serializers.ModelSerializer):
    """Serializer for shipments."""

    tracking_updates = ShipmentTrackingSerializer(many=True, read_only=True)
    order_id = serializers.IntegerField(source="order.id", read_only=True)

    class Meta:
        model = Shipment
        fields = [
            "id",
            "order_id",
            "status",
            "shipping_method",
            "tracking_number",
            "shipping_address",
            "shipping_city",
            "shipping_country",
            "shipping_postal_code",
            "recipient_name",
            "recipient_phone",
            "estimated_delivery",
            "actual_delivery",
            "shipping_cost",
            "weight",
            "notes",
            "tracking_updates",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "tracking_number",
            "estimated_delivery",
            "actual_delivery",
            "shipping_cost",
            "created_at",
            "updated_at",
        ]


class ShipmentCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating shipments."""

    order_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Shipment
        fields = [
            "order_id",
            "shipping_method",
            "recipient_name",
            "recipient_phone",
            "weight",
            "notes",
        ]

    def validate_order_id(self, value):
        from orders.models import Order

        try:
            order = Order.objects.get(id=value)
            if hasattr(order, "shipment"):
                raise serializers.ValidationError("A shipment already exists for this order")
            return value
        except Order.DoesNotExist:
            raise serializers.ValidationError("Order does not exist")


class ShipmentStatusUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating shipment status."""

    class Meta:
        model = Shipment
        fields = ["status"]
