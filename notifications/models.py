from django.db import models
from django.utils.translation import gettext_lazy as _
from accounts.models import User, ClientDevice


class Notification(models.Model):
    """Notification pour appareils client et admin"""
    
    NOTIFICATION_TYPES = (
        ('account_created', 'Compte créé'),
        ('order_created', 'Commande créée'),
        ('order_accepted', 'Commande acceptée'),
        ('order_refused', 'Commande refusée'),
        ('order_preparing', 'Commande en préparation'),
        ('order_ready', 'Commande prête'),
        ('order_assigned', 'Commande assignée au livreur'),
        ('order_picked_up', 'Commande récupérée'),
        ('order_in_delivery', 'Commande en livraison'),
        ('order_delivered', 'Commande livrée'),
        ('order_cancelled', 'Commande annulée'),
        ('delivery_assigned', 'Livraison assignée'),
        ('delivery_accepted', 'Livraison acceptée'),
        ('delivery_refused', 'Livraison refusée'),
        ('delivery_pickup', 'Récupération effectuée'),
        ('delivery_in_progress', 'Livraison en cours'),
        ('delivery_completed', 'Livraison complétée'),
        ('payment_received', 'Paiement reçu'),
        ('payment_failed', 'Paiement échoué'),
        ('rating_received', 'Note reçue'),
    )
    
    # Destinataires
    device = models.ForeignKey(ClientDevice, on_delete=models.CASCADE, null=True, blank=True, 
                              related_name='notifications', verbose_name='Appareil')
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, 
                            related_name='notifications', verbose_name='Utilisateur')
    
    # Contenu
    type = models.CharField(max_length=50, choices=NOTIFICATION_TYPES, verbose_name='Type')
    title = models.CharField(max_length=255, verbose_name='Titre')
    message = models.TextField(verbose_name='Message')
    
    # Données supplémentaires (pour action)
    data = models.JSONField(default=dict, blank=True, verbose_name='Données additionnelles')
    
    # Références
    order_id = models.IntegerField(null=True, blank=True, verbose_name='ID Commande')
    delivery_id = models.IntegerField(null=True, blank=True, verbose_name='ID Livraison')
    related_user_id = models.IntegerField(null=True, blank=True, verbose_name='ID Utilisateur lié')
    
    # Statut
    is_read = models.BooleanField(default=False, verbose_name='Lue')
    read_at = models.DateTimeField(null=True, blank=True, verbose_name='Date de lecture')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Créée le')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Mise à jour')
    
    class Meta:
        db_table = 'notifications'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['device', '-created_at']),
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['is_read']),
        ]
        verbose_name = 'Notification'
        verbose_name_plural = 'Notifications'
    
    def __str__(self):
        recipient = f"Device {self.device.device_id[:10]}" if self.device else f"User {self.user.username}"
        return f"{self.get_type_display()} - {recipient}"
    
    def mark_as_read(self):
        """Marquer la notification comme lue"""
        from django.utils import timezone
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save(update_fields=['is_read', 'read_at'])


class NotificationTemplate(models.Model):
    """Template pour les notifications réutilisables"""
    
    type = models.CharField(max_length=50, unique=True, verbose_name='Type')
    title_template = models.CharField(max_length=255, verbose_name='Template titre')
    message_template = models.TextField(verbose_name='Template message')
    description = models.TextField(blank=True, verbose_name='Description')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'notification_templates'
        verbose_name = 'Template de notification'
        verbose_name_plural = 'Templates de notification'
    
    def __str__(self):
        return self.type
