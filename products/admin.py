from django.contrib import admin

from .models import Product, ProductImage


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "price",
        "stock",
        "category",
        "brand",
        "is_active",
        "created_at",
    ]
    list_filter = ["category", "brand", "is_active", "created_at"]
    search_fields = ["name", "description", "sku"]
    list_editable = ["price", "stock", "is_active"]
    ordering = ["-created_at"]
    inlines = [ProductImageInline]

    fieldsets = (
        (None, {"fields": ("name", "description", "sku")}),
        ("Pricing & Stock", {"fields": ("price", "stock")}),
        ("Attributes", {"fields": ("category", "brand", "size", "color")}),
        ("Status", {"fields": ("is_active",)}),
    )


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ["product", "alt_text", "is_primary", "created_at"]
    list_filter = ["is_primary", "created_at"]
    search_fields = ["product__name", "alt_text"]
