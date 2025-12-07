from django.contrib import admin

from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ["product_name", "product_price", "subtotal"]

    def subtotal(self, obj):
        return obj.subtotal


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "user",
        "status",
        "total_amount",
        "shipping_city",
        "created_at",
    ]
    list_filter = ["status", "created_at", "shipping_country"]
    search_fields = ["user__email", "user__username", "shipping_address"]
    readonly_fields = ["total_amount", "created_at", "updated_at"]
    list_editable = ["status"]
    ordering = ["-created_at"]
    inlines = [OrderItemInline]

    fieldsets = (
        (None, {"fields": ("user", "status", "total_amount")}),
        (
            "Shipping Information",
            {
                "fields": (
                    "shipping_address",
                    "shipping_city",
                    "shipping_country",
                    "shipping_postal_code",
                    "phone_number",
                )
            },
        ),
        ("Notes", {"fields": ("notes",)}),
        ("Timestamps", {"fields": ("created_at", "updated_at")}),
    )


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ["order", "product_name", "product_price", "quantity", "subtotal"]
    list_filter = ["order__status", "created_at"]
    search_fields = ["product_name", "order__id"]

    def subtotal(self, obj):
        return obj.subtotal

    subtotal.short_description = "Subtotal"
