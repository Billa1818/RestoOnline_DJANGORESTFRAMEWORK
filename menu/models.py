from django.db import models
from django.core.validators import MinValueValidator

class Category(models.Model):
    """Catégorie de menu (Boisson, Dessert, Plat, etc.)"""
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    icon = models.ImageField(upload_to='categories/', blank=True, null=True)
    order = models.IntegerField(default=0)  # Pour l'ordre d'affichage
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'categories'
        ordering = ['order', 'name']
        verbose_name_plural = 'Categories'
        
    def __str__(self):
        return self.name


class MenuItem(models.Model):
    """Plat du menu"""
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='items')
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    image = models.ImageField(upload_to='menu_items/', blank=True, null=True)
    is_available = models.BooleanField(default=True)
    preparation_time = models.IntegerField(default=15, validators=[MinValueValidator(1)])  # en minutes
    ingredients = models.TextField(blank=True)  # Liste des ingrédients
    
    # Statistiques
    total_orders = models.IntegerField(default=0)
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)
    total_ratings = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'menu_items'
        ordering = ['category', 'name']
        
    def __str__(self):
        return f"{self.name} ({self.category.name})"


class MenuItemSize(models.Model):
    """Format de plat (Petit, Normal, Grand)"""
    SIZE_CHOICES = (
        ('small', 'Petit'),
        ('medium', 'Normal'),
        ('large', 'Grand'),
    )
    
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE, related_name='sizes')
    size = models.CharField(max_length=20, choices=SIZE_CHOICES)
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    is_available = models.BooleanField(default=True)
    
    # Détails spécifiques au format
    portion_description = models.CharField(max_length=200, blank=True)  # Ex: "300g", "500ml"
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'menu_item_sizes'
        unique_together = ['menu_item', 'size']
        ordering = ['menu_item', 'size']
        
    def __str__(self):
        return f"{self.menu_item.name} - {self.get_size_display()} ({self.price} FCFA)"