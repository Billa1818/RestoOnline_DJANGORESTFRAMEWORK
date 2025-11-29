from rest_framework import serializers
from .models import Notification, NotificationTemplate


class NotificationSerializer(serializers.ModelSerializer):
    """Sérializer pour les notifications"""
    type_display = serializers.CharField(source='get_type_display', read_only=True)
    device_id = serializers.SerializerMethodField()
    user_username = serializers.SerializerMethodField()
    
    class Meta:
        model = Notification
        fields = [
            'id', 'type', 'type_display', 'title', 'message',
            'device_id', 'user_username', 'order_id', 'delivery_id',
            'data', 'is_read', 'read_at', 'created_at', 'updated_at'
        ]
        read_only_fields = fields
    
    def get_device_id(self, obj):
        return obj.device.device_id if obj.device else None
    
    def get_user_username(self, obj):
        return obj.user.username if obj.user else None


class NotificationCreateSerializer(serializers.ModelSerializer):
    """Sérializer pour créer des notifications"""
    
    class Meta:
        model = Notification
        fields = [
            'type', 'title', 'message', 'device', 'user',
            'order_id', 'delivery_id', 'related_user_id', 'data'
        ]


class NotificationTemplateSerializer(serializers.ModelSerializer):
    """Sérializer pour les templates de notification"""
    
    class Meta:
        model = NotificationTemplate
        fields = ['id', 'type', 'title_template', 'message_template', 'description', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']
