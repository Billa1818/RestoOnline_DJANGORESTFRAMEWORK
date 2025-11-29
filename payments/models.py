from django.db import models
from orders.models import Order

class Payment(models.Model):
    """Paiement via PayDunya"""
    STATUS_CHOICES = (
        ('pending', 'En attente'),
        ('processing', 'En cours'),
        ('completed', 'Complété'),
        ('failed', 'Échoué'),
        ('cancelled', 'Annulé'),
        ('refunded', 'Remboursé'),
    )
    
    PAYMENT_METHOD_CHOICES = (
        ('orange_money', 'Orange Money'),
        ('mtn_money', 'MTN Mobile Money'),
        ('moov_money', 'Moov Money'),
        ('card', 'Carte bancaire'),
        ('cash', 'Espèces'),
    )
    
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='payment')
    
    # Informations PayDunya
    paydunya_token = models.CharField(max_length=255, unique=True, null=True, blank=True)
    paydunya_invoice_url = models.URLField(blank=True)
    paydunya_response_code = models.CharField(max_length=50, blank=True)
    paydunya_response_text = models.CharField(max_length=255, blank=True)
    
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=30, choices=PAYMENT_METHOD_CHOICES, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Informations de transaction
    transaction_id = models.CharField(max_length=255, blank=True)
    
    # Réponse complète de l'API PayDunya
    paydunya_response = models.JSONField(default=dict, blank=True)
    
    # Notes
    notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'payments'
        ordering = ['-created_at']
        
    def __str__(self):
        return f"Payment for Order {self.order.order_number} - {self.get_status_display()}"


class PaymentWebhook(models.Model):
    """Logs des webhooks PayDunya"""
    payment = models.ForeignKey(Payment, on_delete=models.SET_NULL, null=True, 
                               blank=True, related_name='webhooks')
    
    webhook_data = models.JSONField()
    status = models.CharField(max_length=50)
    processed = models.BooleanField(default=False)
    processing_error = models.TextField(blank=True)
    
    received_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'payment_webhooks'
        ordering = ['-received_at']
        
    def __str__(self):
        return f"Webhook for Payment {self.payment_id} at {self.received_at}"