import logging

from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from drf_spectacular.utils import extend_schema
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from orders.models import Order

from .models import Payment
from .serializers import PaymentInitiateSerializer, PaymentSerializer
from .services import PaymobService

logger = logging.getLogger(__name__)


class PaymentViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for viewing payments."""

    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff:
            return Payment.objects.all()
        return Payment.objects.filter(order__user=self.request.user)

    @extend_schema(
        summary="Initiate payment",
        description="Initiate a payment for an order using Paymob.",
        request=PaymentInitiateSerializer,
    )
    @action(detail=False, methods=["post"])
    def initiate(self, request):
        serializer = PaymentInitiateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        order_id = serializer.validated_data["order_id"]
        payment_method = serializer.validated_data["payment_method"]

        try:
            order = Order.objects.get(id=order_id, user=request.user)
        except Order.DoesNotExist:
            return Response(
                {"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND
            )

        if order.status != Order.Status.PENDING:
            return Response(
                {"error": "Order is not in pending status"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        existing_payment = Payment.objects.filter(
            order=order, status__in=[Payment.Status.PENDING, Payment.Status.PROCESSING]
        ).first()

        if existing_payment:
            return Response(
                {"error": "A payment is already in progress for this order"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        payment = Payment.objects.create(
            order=order,
            payment_method=payment_method,
            amount=order.total_amount,
            status=Payment.Status.PENDING,
        )

        if payment_method == Payment.Method.CASH:
            payment.status = Payment.Status.PROCESSING
            payment.save()
            return Response(
                {
                    "payment_id": payment.id,
                    "message": "Cash on delivery payment created",
                }
            )

        try:
            paymob_service = PaymobService()
            result = paymob_service.initiate_payment(order, request.user)

            payment.paymob_order_id = result["paymob_order_id"]
            payment.payment_key = result["payment_key"]
            payment.status = Payment.Status.PROCESSING
            payment.save()

            return Response(
                {
                    "payment_id": payment.id,
                    "iframe_url": result["iframe_url"],
                }
            )

        except Exception as e:
            logger.error(f"Payment initiation failed: {e}")
            payment.status = Payment.Status.FAILED
            payment.error_message = str(e)
            payment.save()

            return Response(
                {"error": "Failed to initiate payment"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


@method_decorator(csrf_exempt, name="dispatch")
class PaymobCallbackView(APIView):
    """View for handling Paymob payment callbacks."""

    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    @extend_schema(
        summary="Paymob callback",
        description="Webhook endpoint for Paymob payment notifications.",
    )
    def post(self, request):
        data = request.data.get("obj", {})
        hmac_value = request.query_params.get("hmac", "")

        paymob_service = PaymobService()

        if not paymob_service.verify_hmac(data, hmac_value):
            logger.warning("Invalid HMAC signature in Paymob callback")
            return Response(
                {"error": "Invalid signature"}, status=status.HTTP_400_BAD_REQUEST
            )

        paymob_order_id = str(data.get("order", ""))
        transaction_id = str(data.get("id", ""))
        success = data.get("success", False)

        try:
            payment = Payment.objects.get(paymob_order_id=paymob_order_id)
        except Payment.DoesNotExist:
            logger.error(f"Payment not found for Paymob order: {paymob_order_id}")
            return Response(
                {"error": "Payment not found"}, status=status.HTTP_404_NOT_FOUND
            )

        payment.transaction_id = transaction_id
        payment.metadata = data

        if success:
            payment.status = Payment.Status.COMPLETED
            payment.order.status = Order.Status.CONFIRMED
            payment.order.save(update_fields=["status"])
        else:
            payment.status = Payment.Status.FAILED
            payment.error_message = data.get("data", {}).get(
                "message", "Payment failed"
            )

        payment.save()

        logger.info(
            f"Payment {payment.id} {'completed' if success else 'failed'} "
            f"for order {payment.order.id}"
        )

        return Response({"status": "received"})
