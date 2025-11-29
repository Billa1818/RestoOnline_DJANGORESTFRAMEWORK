from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

class User(AbstractUser):
    """Utilisateur personnalisé"""
    USER_TYPE_CHOICES = (
        ('admin', 'Administrateur'),
        ('manager', 'Gestionnaire'),
        ('delivery', 'Livreur'),
    )
    
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES, null=True, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    is_available = models.BooleanField(default=True)  # Pour les livreurs
    profile_picture = models.ImageField(upload_to='profiles/', blank=True, null=True)
    
    # Statistiques livreur
    total_deliveries = models.IntegerField(default=0)
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'users'
        
    def __str__(self):
        return f"{self.username} ({self.get_user_type_display()})"


class ClientDevice(models.Model):
    """Appareil client (pour Device-Based Authentication)"""
    device_id = models.CharField(max_length=255, unique=True, db_index=True)
    device_info = models.JSONField(default=dict)  # OS, version, modèle, etc.
    device_name = models.CharField(max_length=100, blank=True)  # Ex: "iPhone de Jean"
    fcm_token = models.CharField(max_length=255, blank=True)  # Pour les notifications push
    
    # Informations utilisateur (optionnel)
    customer_name = models.CharField(max_length=200, blank=True)
    customer_phone = models.CharField(max_length=20, blank=True)
    customer_email = models.EmailField(blank=True)
    
    first_seen = models.DateTimeField(auto_now_add=True)
    last_seen = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    is_blocked = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'client_devices'
        
    def __str__(self):
        return f"{self.device_id} - {self.customer_name or 'Anonymous'}"