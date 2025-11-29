# ===================================
# delivery/urls.py
# ===================================

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DeliveryAssignmentViewSet, DeliveryLocationViewSet

router = DefaultRouter()
router.register(r'assignments', DeliveryAssignmentViewSet, basename='delivery-assignment')
router.register(r'locations', DeliveryLocationViewSet, basename='delivery-location')

urlpatterns = [
    path('', include(router.urls)),
]