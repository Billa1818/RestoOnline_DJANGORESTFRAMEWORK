
# ===================================
# ratings/serializers.py
# ===================================

from rest_framework import serializers
from .models import DeliveryRating, MenuItemRating
from accounts.serializers import DeliveryPersonSerializer
from menu.serializers import MenuItemListSerializer


class DeliveryRatingSerializer(serializers.ModelSerializer):
    """Serializer pour DeliveryRating"""
    delivery_person_details = DeliveryPersonSerializer(source='delivery_person', read_only=True)
    order_number = serializers.CharField(source='order.order_number', read_only=True)
    customer_name = serializers.CharField(source='order.customer_name', read_only=True)
    
    class Meta:
        model = DeliveryRating
        fields = [
            'id', 'order', 'order_number', 'device', 'delivery_person',
            'delivery_person_details', 'customer_name', 'rating',
            'comment', 'speed_rating', 'professionalism_rating',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def validate_rating(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError("La note doit être entre 1 et 5.")
        return value


class DeliveryRatingCreateSerializer(serializers.ModelSerializer):
    """Serializer pour la création d'une note de livraison"""
    class Meta:
        model = DeliveryRating
        fields = [
            'order', 'device', 'delivery_person', 'rating',
            'comment', 'speed_rating', 'professionalism_rating'
        ]


class MenuItemRatingSerializer(serializers.ModelSerializer):
    """Serializer pour MenuItemRating"""
    menu_item_details = MenuItemListSerializer(source='menu_item', read_only=True)
    order_number = serializers.CharField(source='order.order_number', read_only=True)
    customer_name = serializers.CharField(source='order.customer_name', read_only=True)
    
    class Meta:
        model = MenuItemRating
        fields = [
            'id', 'order_item', 'order', 'order_number', 'device',
            'menu_item', 'menu_item_details', 'customer_name',
            'rating', 'comment', 'taste_rating', 'presentation_rating',
            'portion_rating', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def validate_rating(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError("La note doit être entre 1 et 5.")
        return value


class MenuItemRatingCreateSerializer(serializers.ModelSerializer):
    """Serializer pour la création d'une note de plat"""
    class Meta:
        model = MenuItemRating
        fields = [
            'order_item', 'order', 'device', 'menu_item', 'rating',
            'comment', 'taste_rating', 'presentation_rating', 'portion_rating'
        ]

