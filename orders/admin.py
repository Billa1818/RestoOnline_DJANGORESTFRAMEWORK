from django.contrib import admin
from django.utils.html import format_html
from .models import Order, OrderItem, Cart, CartItem


class OrderItemInline(admin.TabularInline):
    """Inline pour les articles d'une commande"""
    model = OrderItem
    extra = 0
    readonly_fields = ('item_name', 'size_name', 'item_price', 'subtotal', 'created_at')
    fields = ('item_name', 'size_name', 'item_price', 'quantity', 'subtotal', 'special_instructions')
    
    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """Gestion des commandes"""
    list_display = ('order_number', 'customer_name', 'status_badge', 'total', 'created_at', 'delivery_person')
    list_filter = ('status', 'created_at', 'payment__status')
    search_fields = ('order_number', 'customer_name', 'customer_phone', 'customer_email')
    readonly_fields = ('order_number', 'created_at', 'updated_at', 'accepted_at', 'ready_at', 'assigned_at', 'picked_up_at', 'delivered_at')
    
    fieldsets = (
        ('Informations de base', {
            'fields': ('order_number', 'status', 'created_at', 'updated_at')
        }),
        ('Informations client', {
            'fields': ('device', 'customer_name', 'customer_phone', 'customer_email')
        }),
        ('Adresse de livraison', {
            'fields': ('delivery_address', 'delivery_latitude', 'delivery_longitude', 'delivery_description')
        }),
        ('Gestion', {
            'fields': ('manager', 'delivery_person')
        }),
        ('Pricing', {
            'fields': ('subtotal', 'delivery_fee', 'total')
        }),
        ('Statuts temporels', {
            'fields': ('accepted_at', 'ready_at', 'assigned_at', 'picked_up_at', 'delivered_at'),
            'classes': ('collapse',)
        }),
        ('Notes & Raisons', {
            'fields': ('notes', 'cancellation_reason', 'refusal_reason'),
            'classes': ('collapse',)
        }),
    )
    
    inlines = [OrderItemInline]
    
    def status_badge(self, obj):
        """Affiche le statut avec couleur"""
        colors = {
            'pending': '#FF9800',      # Orange
            'accepted': '#2196F3',     # Bleu
            'preparing': '#9C27B0',    # Violet
            'ready': '#00BCD4',        # Cyan
            'assigned': '#3F51B5',     # Indigo
            'in_delivery': '#4CAF50',  # Vert
            'delivered': '#8BC34A',    # Vert clair
            'cancelled': '#F44336',    # Rouge
            'refused': '#E91E63',      # Rose
        }
        color = colors.get(obj.status, '#999')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 5px 10px; border-radius: 3px;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'Statut'
    
    def has_delete_permission(self, request, obj=None):
        # Empêcher la suppression des commandes
        return False


class CartItemInline(admin.TabularInline):
    """Inline pour les articles du panier"""
    model = CartItem
    extra = 0
    readonly_fields = ('menu_item', 'size', 'added_at', 'updated_at')
    fields = ('menu_item', 'size', 'quantity', 'special_instructions')


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    """Gestion des paniers"""
    list_display = ('device_id', 'items_count', 'created_at', 'updated_at')
    search_fields = ('device__device_id', 'device__customer_name')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Informations', {
            'fields': ('device', 'created_at', 'updated_at')
        }),
    )
    
    inlines = [CartItemInline]
    
    def device_id(self, obj):
        return obj.device.device_id
    device_id.short_description = 'Device ID'
    
    def items_count(self, obj):
        return obj.items.count()
    items_count.short_description = 'Nombre d\'articles'
    
    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    """Gestion des articles de commande"""
    list_display = ('item_name', 'order_number', 'size_name', 'quantity', 'item_price', 'subtotal')
    list_filter = ('created_at', 'order__status')
    search_fields = ('order__order_number', 'item_name')
    readonly_fields = ('order', 'menu_item', 'size', 'item_name', 'size_name', 'item_price', 'subtotal', 'created_at')
    
    fieldsets = (
        ('Informations', {
            'fields': ('order', 'menu_item', 'size', 'item_name', 'size_name', 'item_price')
        }),
        ('Quantité & Prix', {
            'fields': ('quantity', 'subtotal')
        }),
        ('Notes spéciales', {
            'fields': ('special_instructions',)
        }),
    )
    
    def order_number(self, obj):
        return obj.order.order_number
    order_number.short_description = 'N° Commande'
    
    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    """Gestion des articles de panier"""
    list_display = ('menu_item', 'device_id', 'size', 'quantity', 'added_at')
    list_filter = ('added_at', 'menu_item__category')
    search_fields = ('cart__device__device_id', 'menu_item__name')
    readonly_fields = ('cart', 'menu_item', 'size', 'added_at', 'updated_at')
    
    fieldsets = (
        ('Informations', {
            'fields': ('cart', 'menu_item', 'size')
        }),
        ('Quantité', {
            'fields': ('quantity', 'special_instructions')
        }),
        ('Dates', {
            'fields': ('added_at', 'updated_at')
        }),
    )
    
    def device_id(self, obj):
        return obj.cart.device.device_id
    device_id.short_description = 'Device ID'
