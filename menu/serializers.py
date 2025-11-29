# ===================================
# menu/serializers.py
# ===================================

from rest_framework import serializers
from .models import Category, MenuItem, MenuItemSize


class CategorySerializer(serializers.ModelSerializer):
    """Serializer pour Category"""
    items_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Category
        fields = [
            'id', 'name', 'slug', 'description', 'icon',
            'order', 'is_active', 'items_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_items_count(self, obj):
        return obj.items.filter(is_available=True).count()


class MenuItemSizeSerializer(serializers.ModelSerializer):
    """Serializer pour MenuItemSize"""
    size_display = serializers.CharField(source='get_size_display', read_only=True)
    
    class Meta:
        model = MenuItemSize
        fields = [
            'id', 'size', 'size_display', 'price', 'is_available',
            'portion_description', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class MenuItemSerializer(serializers.ModelSerializer):
    """Serializer pour MenuItem avec ses formats"""
    category_name = serializers.CharField(source='category.name', read_only=True)
    sizes = MenuItemSizeSerializer(many=True, read_only=True)
    
    class Meta:
        model = MenuItem
        fields = [
            'id', 'category', 'category_name', 'name', 'slug',
            'description', 'image', 'is_available', 'preparation_time',
            'ingredients', 'sizes', 'total_orders', 'average_rating',
            'total_ratings', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'total_orders', 'average_rating', 'total_ratings',
            'created_at', 'updated_at'
        ]


class MenuItemListSerializer(serializers.ModelSerializer):
    """Serializer simplifié pour les listes de plats"""
    category_name = serializers.CharField(source='category.name', read_only=True)
    min_price = serializers.SerializerMethodField()
    max_price = serializers.SerializerMethodField()
    
    class Meta:
        model = MenuItem
        fields = [
            'id', 'category', 'category_name', 'name', 'slug',
            'image', 'is_available', 'preparation_time',
            'min_price', 'max_price', 'average_rating'
        ]
    
    def get_min_price(self, obj):
        sizes = obj.sizes.filter(is_available=True)
        if sizes.exists():
            return min(size.price for size in sizes)
        return None
    
    def get_max_price(self, obj):
        sizes = obj.sizes.filter(is_available=True)
        if sizes.exists():
            return max(size.price for size in sizes)
        return None


class MenuItemCreateSerializer(serializers.ModelSerializer):
    """Serializer pour la création de MenuItem"""
    sizes = MenuItemSizeSerializer(many=True, required=False)
    
    class Meta:
        model = MenuItem
        fields = [
            'category', 'name', 'slug', 'description', 'image',
            'is_available', 'preparation_time', 'ingredients', 'sizes'
        ]
    
    def create(self, validated_data):
        sizes_data = validated_data.pop('sizes', [])
        menu_item = MenuItem.objects.create(**validated_data)
        
        for size_data in sizes_data:
            MenuItemSize.objects.create(menu_item=menu_item, **size_data)
        
        return menu_item

