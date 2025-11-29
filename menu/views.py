# ===================================
# menu/views.py
# ===================================

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.db.models import Q, Avg
from .models import Category, MenuItem, MenuItemSize
from .serializers import (
    CategorySerializer, MenuItemSerializer, MenuItemListSerializer,
    MenuItemCreateSerializer, MenuItemSizeSerializer
)


class CategoryViewSet(viewsets.ModelViewSet):
    """ViewSet pour les catégories"""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    lookup_field = 'slug'
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAuthenticated()]
    
    def get_queryset(self):
        queryset = Category.objects.all()
        if self.action in ['list', 'retrieve']:
            queryset = queryset.filter(is_active=True)
        return queryset.order_by('order', 'name')
    
    @action(detail=True, methods=['get'])
    def items(self, request, slug=None):
        """Liste des plats d'une catégorie"""
        category = self.get_object()
        items = category.items.filter(is_available=True)
        serializer = MenuItemListSerializer(items, many=True)
        return Response(serializer.data)


class MenuItemViewSet(viewsets.ModelViewSet):
    """ViewSet pour les plats du menu"""
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    lookup_field = 'slug'
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'search', 'popular']:
            return [AllowAny()]
        return [IsAuthenticated()]
    
    def get_serializer_class(self):
        if self.action == 'list':
            return MenuItemListSerializer
        if self.action == 'create':
            return MenuItemCreateSerializer
        return MenuItemSerializer
    
    def get_queryset(self):
        queryset = MenuItem.objects.select_related('category').prefetch_related('sizes')
        
        # Filtres
        category_slug = self.request.query_params.get('category', None)
        is_available = self.request.query_params.get('is_available', None)
        search = self.request.query_params.get('search', None)
        
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)
        
        if is_available:
            queryset = queryset.filter(is_available=is_available.lower() == 'true')
        
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) | 
                Q(description__icontains=search) |
                Q(ingredients__icontains=search)
            )
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def popular(self, request):
        """Plats les plus commandés"""
        popular_items = self.get_queryset().filter(
            is_available=True
        ).order_by('-total_orders')[:10]
        serializer = MenuItemListSerializer(popular_items, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def top_rated(self, request):
        """Plats les mieux notés"""
        top_rated = self.get_queryset().filter(
            is_available=True,
            total_ratings__gte=5  # Au moins 5 notes
        ).order_by('-average_rating')[:10]
        serializer = MenuItemListSerializer(top_rated, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def ratings(self, request, slug=None):
        """Notes et avis d'un plat"""
        item = self.get_object()
        from ratings.models import MenuItemRating
        from ratings.serializers import MenuItemRatingSerializer
        
        ratings = MenuItemRating.objects.filter(menu_item=item).order_by('-created_at')
        serializer = MenuItemRatingSerializer(ratings, many=True)
        
        return Response({
            'average_rating': float(item.average_rating),
            'total_ratings': item.total_ratings,
            'ratings': serializer.data
        })
    
    @action(detail=True, methods=['post'])
    def toggle_availability(self, request, slug=None):
        """Basculer la disponibilité d'un plat"""
        item = self.get_object()
        item.is_available = not item.is_available
        item.save()
        return Response({'is_available': item.is_available})


class MenuItemSizeViewSet(viewsets.ModelViewSet):
    """ViewSet pour les formats de plats"""
    queryset = MenuItemSize.objects.all()
    serializer_class = MenuItemSizeSerializer
    
    def get_permissions(self):
        """Permissions selon l'action"""
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAuthenticated()]
    
    def get_queryset(self):
        queryset = MenuItemSize.objects.select_related('menu_item')
        menu_item_id = self.request.query_params.get('menu_item', None)
        
        if menu_item_id:
            queryset = queryset.filter(menu_item_id=menu_item_id)
        
        return queryset
    
    @action(detail=True, methods=['post'])
    def toggle_availability(self, request, pk=None):
        """Basculer la disponibilité d'un format"""
        size = self.get_object()
        size.is_available = not size.is_available
        size.save()
        return Response({'is_available': size.is_available})


