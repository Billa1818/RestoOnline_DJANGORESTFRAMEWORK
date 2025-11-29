# ===================================
# menu/urls.py
# ===================================

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CategoryViewSet, MenuItemViewSet, MenuItemSizeViewSet

router = DefaultRouter()
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'items', MenuItemViewSet, basename='menu-item')
router.register(r'sizes', MenuItemSizeViewSet, basename='menu-item-size')

urlpatterns = [
    path('', include(router.urls)),
]