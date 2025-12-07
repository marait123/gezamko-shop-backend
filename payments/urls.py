from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import PaymentViewSet, PaymobCallbackView

app_name = "payments"

router = DefaultRouter()
router.register("", PaymentViewSet, basename="payment")

urlpatterns = [
    path("callback/", PaymobCallbackView.as_view(), name="paymob-callback"),
    path("", include(router.urls)),
]
