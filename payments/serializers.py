

# ===================================
# payments/serializers.py
# ===================================

from rest_framework import serializers
from .models import Payment, PaymentWebhook


class PaymentSerializer(serializers.ModelSerializer):
    """Serializer pour Payment"""
    order_number = serializers.CharField(source='order.order_number', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    payment_method_display = serializers.CharField(source='get_payment_method_display', read_only=True)
    
    class Meta:
        model = Payment
        fields = [
            'id', 'order', 'order_number', 'paydunya_token',
            'paydunya_invoice_url', 'paydunya_response_code',
            'paydunya_response_text', 'amount', 'payment_method',
            'payment_method_display', 'status', 'status_display',
            'transaction_id', 'paydunya_response', 'notes',
            'created_at', 'completed_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'paydunya_token', 'paydunya_invoice_url',
            'paydunya_response_code', 'paydunya_response_text',
            'transaction_id', 'paydunya_response', 'created_at',
            'completed_at', 'updated_at'
        ]


class PaymentCreateSerializer(serializers.ModelSerializer):
    """Serializer pour l'initialisation d'un paiement"""
    class Meta:
        model = Payment
        fields = ['order', 'amount', 'payment_method']


class PaymentWebhookSerializer(serializers.ModelSerializer):
    """Serializer pour PaymentWebhook"""
    class Meta:
        model = PaymentWebhook
        fields = [
            'id', 'payment', 'webhook_data', 'status',
            'processed', 'processing_error', 'received_at',
            'processed_at'
        ]
        read_only_fields = ['id', 'received_at', 'processed_at']