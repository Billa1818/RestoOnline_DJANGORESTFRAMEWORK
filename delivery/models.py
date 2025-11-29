from django.db import models
from accounts.models import User
from orders.models import Order

class DeliveryAssignment(models.Model):
    """Affectation d'une commande à un livreur"""
    STATUS_CHOICES = (
        ('assigned', 'Assignée'),
        ('accepted', 'Acceptée'),
        ('refused', 'Refusée'),
        ('picked_up', 'Récupérée'),
        ('delivered', 'Livrée'),
    )
    
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='assignment')
    delivery_person = models.ForeignKey(User, on_delete=models.CASCADE, 
                                       related_name='assignments', limit_choices_to={'user_type': 'delivery'})
    assigned_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True,
                                   related_name='assignments_created', limit_choices_to={'user_type': 'manager'})
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='assigned')
    
    assigned_at = models.DateTimeField(auto_now_add=True)
    accepted_at = models.DateTimeField(null=True, blank=True)
    refused_at = models.DateTimeField(null=True, blank=True)
    picked_up_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    
    refusal_reason = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    
    class Meta:
        db_table = 'delivery_assignments'
        ordering = ['-assigned_at']
        
    def __str__(self):
        return f"Assignment {self.order.order_number} to {self.delivery_person.get_full_name()}"


class DeliveryLocation(models.Model):
    """Suivi de la position du livreur pendant une livraison"""
    assignment = models.ForeignKey(DeliveryAssignment, on_delete=models.CASCADE, related_name='locations')
    latitude = models.DecimalField(max_digits=10, decimal_places=8)
    longitude = models.DecimalField(max_digits=11, decimal_places=8)
    accuracy = models.FloatField(null=True, blank=True)  # Précision en mètres
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'delivery_locations'
        ordering = ['-timestamp']
        
    def __str__(self):
        return f"Location for {self.assignment.order.order_number} at {self.timestamp}"