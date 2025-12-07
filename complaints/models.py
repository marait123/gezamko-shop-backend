from django.conf import settings
from django.db import models

from orders.models import Order


class Complaint(models.Model):
    """Complaint model for customer support tickets."""

    class Status(models.TextChoices):
        OPEN = "open", "Open"
        IN_PROGRESS = "in_progress", "In Progress"
        WAITING_CUSTOMER = "waiting_customer", "Waiting for Customer"
        RESOLVED = "resolved", "Resolved"
        CLOSED = "closed", "Closed"

    class Priority(models.TextChoices):
        LOW = "low", "Low"
        MEDIUM = "medium", "Medium"
        HIGH = "high", "High"
        URGENT = "urgent", "Urgent"

    class Category(models.TextChoices):
        ORDER = "order", "Order Issue"
        PRODUCT = "product", "Product Issue"
        SHIPPING = "shipping", "Shipping Issue"
        PAYMENT = "payment", "Payment Issue"
        REFUND = "refund", "Refund Request"
        OTHER = "other", "Other"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="complaints"
    )
    order = models.ForeignKey(
        Order,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="complaints",
    )
    subject = models.CharField(max_length=255)
    description = models.TextField()
    category = models.CharField(
        max_length=20, choices=Category.choices, default=Category.OTHER
    )
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.OPEN
    )
    priority = models.CharField(
        max_length=20, choices=Priority.choices, default=Priority.MEDIUM
    )
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_complaints",
    )
    resolution = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "complaints"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Complaint #{self.id}: {self.subject}"


class ComplaintResponse(models.Model):
    """Model for responses to complaints."""

    complaint = models.ForeignKey(
        Complaint, on_delete=models.CASCADE, related_name="responses"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="complaint_responses",
    )
    message = models.TextField()
    is_staff_response = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "complaint_responses"
        ordering = ["created_at"]

    def __str__(self):
        return f"Response to Complaint #{self.complaint.id}"
