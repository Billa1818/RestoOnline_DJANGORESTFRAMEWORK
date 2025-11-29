from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from accounts.models import User, ClientDevice
from orders.models import Order, OrderItem
from menu.models import MenuItem

class DeliveryRating(models.Model):
    """Note attribuée au livreur par le client"""
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='delivery_rating')
    device = models.ForeignKey(ClientDevice, on_delete=models.SET_NULL, null=True, related_name='delivery_ratings')
    delivery_person = models.ForeignKey(User, on_delete=models.CASCADE, 
                                       related_name='ratings', limit_choices_to={'user_type': 'delivery'})
    
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField(blank=True)
    
    # Critères spécifiques (optionnel)
    speed_rating = models.IntegerField(null=True, blank=True, 
                                      validators=[MinValueValidator(1), MaxValueValidator(5)])
    professionalism_rating = models.IntegerField(null=True, blank=True,
                                                 validators=[MinValueValidator(1), MaxValueValidator(5)])
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'delivery_ratings'
        ordering = ['-created_at']
        
    def __str__(self):
        return f"Rating {self.rating}/5 for {self.delivery_person.get_full_name()} on Order {self.order.order_number}"


class MenuItemRating(models.Model):
    """Note attribuée au plat par le client"""
    order_item = models.ForeignKey(OrderItem, on_delete=models.CASCADE, related_name='rating')
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='item_ratings')
    device = models.ForeignKey(ClientDevice, on_delete=models.SET_NULL, null=True, related_name='menu_ratings')
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE, related_name='ratings')
    
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField(blank=True)
    
    # Critères spécifiques (optionnel)
    taste_rating = models.IntegerField(null=True, blank=True,
                                      validators=[MinValueValidator(1), MaxValueValidator(5)])
    presentation_rating = models.IntegerField(null=True, blank=True,
                                            validators=[MinValueValidator(1), MaxValueValidator(5)])
    portion_rating = models.IntegerField(null=True, blank=True,
                                        validators=[MinValueValidator(1), MaxValueValidator(5)])
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'menu_item_ratings'
        ordering = ['-created_at']
        # Un client peut noter chaque plat d'une commande séparément
        unique_together = ['order_item', 'device']
        
    def __str__(self):
        return f"Rating {self.rating}/5 for {self.menu_item.name} on Order {self.order.order_number}"