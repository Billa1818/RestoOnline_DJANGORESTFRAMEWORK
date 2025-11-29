
# ===================================
# payments/urls.py
# ===================================

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PaymentViewSet, PaymentWebhookViewSet, paydunya_webhook

router = DefaultRouter()
router.register(r'payments', PaymentViewSet, basename='payment')
router.register(r'webhooks', PaymentWebhookViewSet, basename='payment-webhook')

urlpatterns = [
    path('', include(router.urls)),
    path('paydunya/webhook/', paydunya_webhook, name='paydunya-webhook'),
]