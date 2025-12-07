from django.db import models

from orders.models import Order


class Payment(models.Model):
    """Payment model for tracking order payments."""

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        PROCESSING = "processing", "Processing"
        COMPLETED = "completed", "Completed"
        FAILED = "failed", "Failed"
        REFUNDED = "refunded", "Refunded"
        CANCELLED = "cancelled", "Cancelled"

    class Method(models.TextChoices):
        CARD = "card", "Credit/Debit Card"
        WALLET = "wallet", "Mobile Wallet"
        CASH = "cash", "Cash on Delivery"

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="payments")
    payment_method = models.CharField(max_length=20, choices=Method.choices)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.PENDING
    )
    transaction_id = models.CharField(
        max_length=255, unique=True, null=True, blank=True
    )
    paymob_order_id = models.CharField(max_length=255, null=True, blank=True)
    payment_key = models.TextField(null=True, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    error_message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "payments"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Payment #{self.id} for Order #{self.order.id}"
