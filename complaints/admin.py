from django.contrib import admin

from .models import Complaint, ComplaintResponse


class ComplaintResponseInline(admin.TabularInline):
    model = ComplaintResponse
    extra = 1
    readonly_fields = ["user", "is_staff_response", "created_at"]


@admin.register(Complaint)
class ComplaintAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "subject",
        "user",
        "category",
        "status",
        "priority",
        "assigned_to",
        "created_at",
    ]
    list_filter = ["status", "category", "priority", "created_at"]
    search_fields = ["subject", "description", "user__email", "user__username"]
    list_editable = ["status", "priority", "assigned_to"]
    readonly_fields = ["user", "created_at", "updated_at"]
    ordering = ["-created_at"]
    inlines = [ComplaintResponseInline]

    fieldsets = (
        (None, {"fields": ("user", "order", "subject", "description")}),
        (
            "Classification",
            {"fields": ("category", "status", "priority")},
        ),
        ("Assignment", {"fields": ("assigned_to",)}),
        ("Resolution", {"fields": ("resolution",)}),
        ("Timestamps", {"fields": ("created_at", "updated_at")}),
    )


@admin.register(ComplaintResponse)
class ComplaintResponseAdmin(admin.ModelAdmin):
    list_display = ["complaint", "user", "is_staff_response", "created_at"]
    list_filter = ["is_staff_response", "created_at"]
    search_fields = ["complaint__subject", "message", "user__email"]
    readonly_fields = ["complaint", "user", "is_staff_response", "created_at"]
    ordering = ["-created_at"]
