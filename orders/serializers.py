from django.db import transaction
from rest_framework import serializers

from products.models import Product

from .models import Order, OrderItem


class OrderItemSerializer(serializers.ModelSerializer):
    """Serializer for order items."""

    subtotal = serializers.ReadOnlyField()

    class Meta:
        model = OrderItem
        fields = [
            "id",
            "product",
            "product_name",
            "product_price",
            "quantity",
            "subtotal",
        ]
        read_only_fields = ["id", "product_name", "product_price"]


class OrderItemCreateSerializer(serializers.Serializer):
    """Serializer for creating order items."""

    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1)

    def validate_product_id(self, value):
        try:
            product = Product.objects.get(id=value, is_active=True)
            if product.stock < 1:
                raise serializers.ValidationError("Product is out of stock")
            return value
        except Product.DoesNotExist:
            raise serializers.ValidationError("Product does not exist")


class OrderSerializer(serializers.ModelSerializer):
    """Serializer for orders."""

    items = OrderItemSerializer(many=True, read_only=True)
    user_email = serializers.CharField(source="user.email", read_only=True)

    class Meta:
        model = Order
        fields = [
            "id",
            "user",
            "user_email",
            "status",
            "total_amount",
            "shipping_address",
            "shipping_city",
            "shipping_country",
            "shipping_postal_code",
            "phone_number",
            "notes",
            "items",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "user", "total_amount", "created_at", "updated_at"]


class OrderCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating orders."""

    items = OrderItemCreateSerializer(many=True, write_only=True)

    class Meta:
        model = Order
        fields = [
            "shipping_address",
            "shipping_city",
            "shipping_country",
            "shipping_postal_code",
            "phone_number",
            "notes",
            "items",
        ]

    def validate_items(self, value):
        if not value:
            raise serializers.ValidationError("At least one item is required")
        return value

    @transaction.atomic
    def create(self, validated_data):
        items_data = validated_data.pop("items")
        user = self.context["request"].user

        order = Order.objects.create(user=user, **validated_data)

        for item_data in items_data:
            product = Product.objects.select_for_update().get(id=item_data["product_id"])
            quantity = item_data["quantity"]

            if product.stock < quantity:
                raise serializers.ValidationError(f"Insufficient stock for {product.name}")

            OrderItem.objects.create(
                order=order,
                product=product,
                product_name=product.name,
                product_price=product.price,
                quantity=quantity,
            )

            product.stock -= quantity
            product.save(update_fields=["stock"])

        order.calculate_total()
        return order


class OrderStatusUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating order status."""

    class Meta:
        model = Order
        fields = ["status"]
