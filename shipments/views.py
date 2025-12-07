import logging

from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from orders.models import Order

from .models import Shipment, ShipmentTracking
from .serializers import (
    ShipmentCreateSerializer,
    ShipmentSerializer,
    ShipmentStatusUpdateSerializer,
    ShipmentTrackingSerializer,
)
from .services import PostaService

logger = logging.getLogger(__name__)


@extend_schema_view(
    list=extend_schema(
        summary="List shipments",
        description="Get a list of shipments. Users see their own shipments, admins see all.",
    ),
    retrieve=extend_schema(
        summary="Get shipment details",
        description="Get detailed information about a specific shipment.",
    ),
    create=extend_schema(
        summary="Create a shipment",
        description="Create a shipment for an order. Admin access required.",
    ),
)
class ShipmentViewSet(viewsets.ModelViewSet):
    """ViewSet for managing shipments."""

    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["status", "shipping_method"]

    def get_queryset(self):
        if self.request.user.is_staff:
            return Shipment.objects.all()
        return Shipment.objects.filter(order__user=self.request.user)

    def get_serializer_class(self):
        if self.action == "create":
            return ShipmentCreateSerializer
        if self.action == "update_status":
            return ShipmentStatusUpdateSerializer
        return ShipmentSerializer

    def get_permissions(self):
        if self.action in ["create", "destroy", "update", "partial_update"]:
            return [permissions.IsAdminUser()]
        return super().get_permissions()

    def perform_create(self, serializer):
        order_id = serializer.validated_data.pop("order_id")
        order = Order.objects.get(id=order_id)

        shipment = serializer.save(
            order=order,
            shipping_address=order.shipping_address,
            shipping_city=order.shipping_city,
            shipping_country=order.shipping_country,
            shipping_postal_code=order.shipping_postal_code,
        )

        try:
            posta_service = PostaService()
            result = posta_service.create_shipment(shipment)

            shipment.posta_shipment_id = result.get("shipment_id")
            shipment.tracking_number = result.get("tracking_number")
            shipment.estimated_delivery = result.get("estimated_delivery")
            if result.get("shipping_cost"):
                shipment.shipping_cost = result.get("shipping_cost")
            shipment.status = Shipment.Status.PROCESSING
            shipment.save()

            order.status = Order.Status.PROCESSING
            order.save(update_fields=["status"])

        except Exception as e:
            logger.error(f"Failed to create shipment in Posta: {e}")

    @extend_schema(
        summary="Update shipment status",
        description="Update the status of a shipment. Admin access required.",
    )
    @action(
        detail=True, methods=["patch"], permission_classes=[permissions.IsAdminUser]
    )
    def update_status(self, request, pk=None):
        shipment = self.get_object()
        serializer = ShipmentStatusUpdateSerializer(
            shipment, data=request.data, partial=True
        )

        if serializer.is_valid():
            old_status = shipment.status
            serializer.save()

            ShipmentTracking.objects.create(
                shipment=shipment,
                status=shipment.status,
                description=f"Status changed from {old_status} to {shipment.status}",
                timestamp=shipment.updated_at,
            )

            if shipment.status == Shipment.Status.SHIPPED:
                shipment.order.status = Order.Status.SHIPPED
                shipment.order.save(update_fields=["status"])
            elif shipment.status == Shipment.Status.DELIVERED:
                shipment.order.status = Order.Status.DELIVERED
                shipment.order.save(update_fields=["status"])
                from django.utils import timezone

                shipment.actual_delivery = timezone.now()
                shipment.save(update_fields=["actual_delivery"])

            return Response(ShipmentSerializer(shipment).data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        summary="Get tracking info",
        description="Get real-time tracking information for a shipment.",
    )
    @action(detail=True, methods=["get"])
    def tracking(self, request, pk=None):
        shipment = self.get_object()

        if shipment.tracking_number:
            posta_service = PostaService()
            tracking_info = posta_service.get_tracking_info(shipment.tracking_number)

            for update in tracking_info.get("updates", []):
                ShipmentTracking.objects.get_or_create(
                    shipment=shipment,
                    timestamp=update.get("timestamp"),
                    defaults={
                        "status": update.get("status", ""),
                        "location": update.get("location", ""),
                        "description": update.get("description", ""),
                    },
                )

        tracking_updates = shipment.tracking_updates.all()
        serializer = ShipmentTrackingSerializer(tracking_updates, many=True)

        return Response(
            {
                "tracking_number": shipment.tracking_number,
                "status": shipment.status,
                "updates": serializer.data,
            }
        )

    @extend_schema(
        summary="Get shipping rates",
        description="Get available shipping rates based on destination and weight.",
    )
    @action(detail=False, methods=["post"])
    def rates(self, request):
        destination = request.data.get("destination", {})
        weight = request.data.get("weight", 1.0)

        posta_service = PostaService()
        rates = posta_service.get_shipping_rates(
            origin={"country": "EG"},
            destination=destination,
            weight=weight,
        )

        return Response({"rates": rates})
