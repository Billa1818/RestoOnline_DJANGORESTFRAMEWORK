from django.db import models
from django.core.validators import MinValueValidator
from accounts.models import User, ClientDevice
from menu.models import MenuItem, MenuItemSize

class Order(models.Model):
    """Commande"""
    STATUS_CHOICES = (
        ('pending', 'En attente'),
        ('accepted', 'Acceptée'),
        ('preparing', 'En préparation'),
        ('ready', 'Prête'),
        ('assigned', 'Assignée au livreur'),
        ('in_delivery', 'En cours de livraison'),
        ('delivered', 'Livrée'),
        ('cancelled', 'Annulée'),
        ('refused', 'Refusée'),
    )
    
    order_number = models.CharField(max_length=20, unique=True, db_index=True)
    device = models.ForeignKey(ClientDevice, on_delete=models.SET_NULL, null=True, related_name='orders')
    
    # Adresse de livraison
    delivery_address = models.TextField()
    delivery_latitude = models.DecimalField(max_digits=10, decimal_places=8, null=True, blank=True)
    delivery_longitude = models.DecimalField(max_digits=11, decimal_places=8, null=True, blank=True)
    delivery_description = models.TextField(blank=True)  # Description réelle de la position
    
    # Informations de contact
    customer_name = models.CharField(max_length=200)
    customer_phone = models.CharField(max_length=20)
    customer_email = models.EmailField(blank=True)
    
    # Statut et suivi
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    manager = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, 
                                related_name='managed_orders', limit_choices_to={'user_type': 'manager'})
    delivery_person = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                       related_name='delivery_orders', limit_choices_to={'user_type': 'delivery'})
    
    # Prix
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    delivery_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Notes et instructions
    notes = models.TextField(blank=True)
    cancellation_reason = models.TextField(blank=True)
    refusal_reason = models.TextField(blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    accepted_at = models.DateTimeField(null=True, blank=True)
    ready_at = models.DateTimeField(null=True, blank=True)
    assigned_at = models.DateTimeField(null=True, blank=True)
    picked_up_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'orders'
        ordering = ['-created_at']
        
    def __str__(self):
        return f"Order {self.order_number} - {self.get_status_display()}"


class OrderItem(models.Model):
    """Article dans une commande"""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    menu_item = models.ForeignKey(MenuItem, on_delete=models.PROTECT)
    size = models.ForeignKey(MenuItemSize, on_delete=models.PROTECT)
    
    # Snapshot des infos au moment de la commande
    item_name = models.CharField(max_length=200)
    size_name = models.CharField(max_length=20)
    item_price = models.DecimalField(max_digits=10, decimal_places=2)
    
    quantity = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    special_instructions = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'order_items'
        
    def __str__(self):
        return f"{self.item_name} ({self.size_name}) x{self.quantity}"


class Cart(models.Model):
    """Panier temporaire pour un appareil"""
    device = models.OneToOneField(ClientDevice, on_delete=models.CASCADE, related_name='cart')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'carts'
        
    def __str__(self):
        return f"Cart for {self.device.device_id}"


class CartItem(models.Model):
    """Article dans un panier"""
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    size = models.ForeignKey(MenuItemSize, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])
    special_instructions = models.TextField(blank=True)
    added_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'cart_items'
        # Permet d'avoir le même plat plusieurs fois avec des tailles différentes
        
    def __str__(self):
        return f"{self.menu_item.name} ({self.size.get_size_display()}) x{self.quantity}"