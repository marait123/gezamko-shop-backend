from django.db import models

from orders.models import Order


class Shipment(models.Model):
    """Shipment model for tracking order deliveries."""

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        PROCESSING = "processing", "Processing"
        SHIPPED = "shipped", "Shipped"
        IN_TRANSIT = "in_transit", "In Transit"
        OUT_FOR_DELIVERY = "out_for_delivery", "Out for Delivery"
        DELIVERED = "delivered", "Delivered"
        RETURNED = "returned", "Returned"
        FAILED = "failed", "Failed"

    class Method(models.TextChoices):
        STANDARD = "standard", "Standard Shipping"
        EXPRESS = "express", "Express Shipping"
        SAME_DAY = "same_day", "Same Day Delivery"

    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name="shipment")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    shipping_method = models.CharField(max_length=20, choices=Method.choices, default=Method.STANDARD)
    tracking_number = models.CharField(max_length=255, unique=True, null=True, blank=True)
    posta_shipment_id = models.CharField(max_length=255, null=True, blank=True)
    shipping_address = models.TextField()
    shipping_city = models.CharField(max_length=100)
    shipping_country = models.CharField(max_length=100)
    shipping_postal_code = models.CharField(max_length=20)
    recipient_name = models.CharField(max_length=255)
    recipient_phone = models.CharField(max_length=20)
    estimated_delivery = models.DateField(null=True, blank=True)
    actual_delivery = models.DateTimeField(null=True, blank=True)
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    weight = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "shipments"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Shipment #{self.id} for Order #{self.order.id}"


class ShipmentTracking(models.Model):
    """Model for tracking shipment status updates."""

    shipment = models.ForeignKey(Shipment, on_delete=models.CASCADE, related_name="tracking_updates")
    status = models.CharField(max_length=100)
    location = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    timestamp = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "shipment_tracking"
        ordering = ["-timestamp"]

    def __str__(self):
        return f"Tracking update for Shipment #{self.shipment.id}"
