from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from users.permissions import IsAdminUser, IsStaffUser, OrderPermission

from .models import Order
from .serializers import (
    OrderCreateSerializer,
    OrderSerializer,
    OrderStatusUpdateSerializer,
)


@extend_schema_view(
    list=extend_schema(
        summary="List orders",
        description="Customers see their own orders. Staff/Admin see all orders.",
    ),
    retrieve=extend_schema(
        summary="Get order details",
        description="Get detailed information about a specific order.",
    ),
    create=extend_schema(
        summary="Create an order",
        description="Create a new order with items. Customer access.",
    ),
)
class OrderViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing orders.

    Permissions:
    - Customers: Create orders, view/cancel their own orders
    - Staff: View all orders, update status
    - Admin: Full access
    """

    permission_classes = [OrderPermission]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["status"]

    def get_queryset(self):
        if self.request.user.is_staff_user:
            return Order.objects.all()
        return Order.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action == "create":
            return OrderCreateSerializer
        if self.action == "update_status":
            return OrderStatusUpdateSerializer
        return OrderSerializer

    def get_permissions(self):
        if self.action in ["destroy", "update", "partial_update"]:
            return [IsAdminUser()]
        return super().get_permissions()

    @extend_schema(
        summary="Update order status",
        description="Update the status of an order. Staff/Admin access required.",
    )
    @action(detail=True, methods=["patch"], permission_classes=[IsStaffUser])
    def update_status(self, request, pk=None):
        order = self.get_object()
        serializer = OrderStatusUpdateSerializer(order, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(OrderSerializer(order).data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        summary="Cancel order",
        description=(
            "Cancel an order. Customers can cancel their own pending orders. "
            "Staff/Admin can cancel any pending order."
        ),
    )
    @action(detail=True, methods=["post"])
    def cancel(self, request, pk=None):
        order = self.get_object()

        if order.status != Order.Status.PENDING:
            return Response(
                {"error": "Only pending orders can be cancelled"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if order.user != request.user and not request.user.is_staff_user:
            return Response(
                {"error": "You can only cancel your own orders"},
                status=status.HTTP_403_FORBIDDEN,
            )

        for item in order.items.all():
            if item.product:
                item.product.stock += item.quantity
                item.product.save(update_fields=["stock"])

        order.status = Order.Status.CANCELLED
        order.save(update_fields=["status"])

        return Response(OrderSerializer(order).data)
