# ===================================
# ratings/urls.py
# ===================================

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DeliveryRatingViewSet, MenuItemRatingViewSet

router = DefaultRouter()
router.register(r'delivery-ratings', DeliveryRatingViewSet, basename='delivery-rating')
router.register(r'menu-item-ratings', MenuItemRatingViewSet, basename='menu-item-rating')

urlpatterns = [
    path('', include(router.urls)),
]