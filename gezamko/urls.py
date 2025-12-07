"""
URL configuration for gezamko project.
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

urlpatterns = [
    path("admin/", admin.site.urls),
    # API endpoints
    path("api/v1/users/", include("users.urls", namespace="users")),
    path("api/v1/products/", include("products.urls", namespace="products")),
    path("api/v1/orders/", include("orders.urls", namespace="orders")),
    path("api/v1/payments/", include("payments.urls", namespace="payments")),
    path("api/v1/shipments/", include("shipments.urls", namespace="shipments")),
    path("api/v1/complaints/", include("complaints.urls", namespace="complaints")),
    # API Documentation
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/docs/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path(
        "api/redoc/",
        SpectacularRedocView.as_view(url_name="schema"),
        name="redoc",
    ),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
