from django.contrib import admin

from .models import Shipment, ShipmentTracking


class ShipmentTrackingInline(admin.TabularInline):
    model = ShipmentTracking
    extra = 0
    readonly_fields = ["status", "location", "description", "timestamp"]


@admin.register(Shipment)
class ShipmentAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "order",
        "status",
        "shipping_method",
        "tracking_number",
        "shipping_city",
        "estimated_delivery",
        "created_at",
    ]
    list_filter = ["status", "shipping_method", "created_at"]
    search_fields = [
        "order__id",
        "tracking_number",
        "recipient_name",
        "recipient_phone",
    ]
    readonly_fields = [
        "tracking_number",
        "posta_shipment_id",
        "estimated_delivery",
        "actual_delivery",
        "created_at",
        "updated_at",
    ]
    list_editable = ["status"]
    ordering = ["-created_at"]
    inlines = [ShipmentTrackingInline]

    fieldsets = (
        (None, {"fields": ("order", "status", "shipping_method")}),
        (
            "Tracking",
            {"fields": ("tracking_number", "posta_shipment_id")},
        ),
        (
            "Recipient Information",
            {"fields": ("recipient_name", "recipient_phone")},
        ),
        (
            "Shipping Address",
            {
                "fields": (
                    "shipping_address",
                    "shipping_city",
                    "shipping_country",
                    "shipping_postal_code",
                )
            },
        ),
        (
            "Delivery Info",
            {
                "fields": (
                    "estimated_delivery",
                    "actual_delivery",
                    "shipping_cost",
                    "weight",
                )
            },
        ),
        ("Notes", {"fields": ("notes",)}),
        ("Timestamps", {"fields": ("created_at", "updated_at")}),
    )


@admin.register(ShipmentTracking)
class ShipmentTrackingAdmin(admin.ModelAdmin):
    list_display = ["shipment", "status", "location", "timestamp"]
    list_filter = ["status", "timestamp"]
    search_fields = ["shipment__tracking_number", "status", "location"]
    ordering = ["-timestamp"]
