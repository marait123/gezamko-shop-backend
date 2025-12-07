from django.contrib import admin

from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "order",
        "payment_method",
        "amount",
        "status",
        "transaction_id",
        "created_at",
    ]
    list_filter = ["status", "payment_method", "created_at"]
    search_fields = ["order__id", "transaction_id", "paymob_order_id"]
    readonly_fields = [
        "order",
        "amount",
        "transaction_id",
        "paymob_order_id",
        "payment_key",
        "metadata",
        "created_at",
        "updated_at",
    ]
    ordering = ["-created_at"]

    fieldsets = (
        (None, {"fields": ("order", "payment_method", "amount", "status")}),
        (
            "Transaction Details",
            {"fields": ("transaction_id", "paymob_order_id", "payment_key")},
        ),
        ("Additional Info", {"fields": ("metadata", "error_message")}),
        ("Timestamps", {"fields": ("created_at", "updated_at")}),
    )
