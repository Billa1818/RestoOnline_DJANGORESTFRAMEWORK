
# ===================================
# delivery/serializers.py
# ===================================

from rest_framework import serializers
from .models import DeliveryAssignment, DeliveryLocation
from orders.serializers import OrderSerializer
from accounts.serializers import DeliveryPersonSerializer


class DeliveryLocationSerializer(serializers.ModelSerializer):
    """Serializer pour DeliveryLocation"""
    class Meta:
        model = DeliveryLocation
        fields = [
            'id', 'assignment', 'latitude', 'longitude',
            'accuracy', 'timestamp'
        ]
        read_only_fields = ['id', 'timestamp']


class DeliveryAssignmentSerializer(serializers.ModelSerializer):
    """Serializer complet pour DeliveryAssignment"""
    order_details = OrderSerializer(source='order', read_only=True)
    delivery_person_details = DeliveryPersonSerializer(source='delivery_person', read_only=True)
    assigned_by_name = serializers.CharField(source='assigned_by.get_full_name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    latest_location = serializers.SerializerMethodField()
    
    class Meta:
        model = DeliveryAssignment
        fields = [
            'id', 'order', 'order_details', 'delivery_person',
            'delivery_person_details', 'assigned_by', 'assigned_by_name',
            'status', 'status_display', 'assigned_at', 'accepted_at',
            'refused_at', 'picked_up_at', 'delivered_at',
            'refusal_reason', 'notes', 'latest_location'
        ]
        read_only_fields = [
            'id', 'assigned_at', 'accepted_at', 'refused_at',
            'picked_up_at', 'delivered_at'
        ]
    
    def get_latest_location(self, obj):
        latest = obj.locations.first()
        if latest:
            return DeliveryLocationSerializer(latest).data
        return None


class DeliveryAssignmentCreateSerializer(serializers.ModelSerializer):
    """Serializer pour la création d'une affectation"""
    class Meta:
        model = DeliveryAssignment
        fields = ['order', 'delivery_person', 'assigned_by', 'notes']


class DeliveryAssignmentListSerializer(serializers.ModelSerializer):
    """Serializer simplifié pour les listes"""
    order_number = serializers.CharField(source='order.order_number', read_only=True)
    delivery_person_name = serializers.CharField(source='delivery_person.get_full_name', read_only=True)
    customer_name = serializers.CharField(source='order.customer_name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = DeliveryAssignment
        fields = [
            'id', 'order_number', 'delivery_person_name',
            'customer_name', 'status', 'status_display',
            'assigned_at', 'delivered_at'
        ]

