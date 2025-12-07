from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = [
        "username",
        "email",
        "role",
        "first_name",
        "last_name",
        "is_staff",
        "created_at",
    ]
    list_filter = ["role", "is_staff", "is_superuser", "is_active", "created_at"]
    search_fields = ["username", "email", "first_name", "last_name"]
    list_editable = ["role"]
    ordering = ["-created_at"]

    fieldsets = BaseUserAdmin.fieldsets + (
        (
            "Role & Permissions",
            {"fields": ("role",)},
        ),
        (
            "Additional Info",
            {
                "fields": (
                    "keycloak_id",
                    "phone_number",
                    "address",
                    "city",
                    "country",
                    "postal_code",
                )
            },
        ),
    )

    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        (
            "Role",
            {"fields": ("role",)},
        ),
        (
            "Additional Info",
            {
                "fields": (
                    "email",
                    "phone_number",
                    "address",
                    "city",
                    "country",
                    "postal_code",
                )
            },
        ),
    )
