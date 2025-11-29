from django.contrib import admin
from django.utils.html import format_html
from .models import Payment, PaymentWebhook


class PaymentWebhookInline(admin.TabularInline):
    """Inline pour les webhooks d'un paiement"""
    model = PaymentWebhook
    extra = 0
    readonly_fields = ('webhook_data', 'status', 'received_at', 'processed_at', 'processing_error')
    fields = ('status', 'processed', 'received_at', 'processed_at')
    
    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    """Gestion des paiements"""
    list_display = ('order_number', 'amount', 'payment_method_display', 'status_badge', 'created_at')
    list_filter = ('status', 'payment_method', 'created_at')
    search_fields = ('order__order_number', 'transaction_id', 'paydunya_token')
    readonly_fields = (
        'paydunya_token', 'paydunya_invoice_url', 'paydunya_response_code', 
        'paydunya_response_text', 'paydunya_response', 'transaction_id', 
        'created_at', 'completed_at', 'updated_at'
    )
    
    fieldsets = (
        ('Informations de base', {
            'fields': ('order', 'amount', 'payment_method', 'status')
        }),
        ('PayDunya', {
            'fields': (
                'paydunya_token', 
                'paydunya_invoice_url', 
                'paydunya_response_code', 
                'paydunya_response_text'
            ),
            'classes': ('collapse',)
        }),
        ('Transaction', {
            'fields': ('transaction_id', 'paydunya_response'),
            'classes': ('collapse',)
        }),
        ('Notes', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
        ('Dates', {
            'fields': ('created_at', 'completed_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    inlines = [PaymentWebhookInline]
    
    def order_number(self, obj):
        return obj.order.order_number
    order_number.short_description = 'N° Commande'
    
    def payment_method_display(self, obj):
        """Affiche la méthode de paiement lisiblement"""
        methods = {
            'orange_money': '🟠 Orange Money',
            'mtn_money': '🟡 MTN Money',
            'moov_money': '🔴 Moov Money',
            'card': '💳 Carte bancaire',
            'cash': '💵 Espèces',
        }
        return methods.get(obj.payment_method, obj.get_payment_method_display())
    payment_method_display.short_description = 'Méthode'
    
    def status_badge(self, obj):
        """Affiche le statut avec couleur"""
        colors = {
            'pending': '#FF9800',      # Orange
            'processing': '#2196F3',   # Bleu
            'completed': '#4CAF50',    # Vert
            'failed': '#F44336',       # Rouge
            'cancelled': '#E91E63',    # Rose
            'refunded': '#9C27B0',     # Violet
        }
        color = colors.get(obj.status, '#999')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 5px 10px; border-radius: 3px;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'Statut'
    
    def has_delete_permission(self, request, obj=None):
        # Empêcher la suppression des paiements
        return False


@admin.register(PaymentWebhook)
class PaymentWebhookAdmin(admin.ModelAdmin):
    """Gestion des webhooks"""
    list_display = ('payment_order', 'status', 'processed_badge', 'received_at')
    list_filter = ('status', 'processed', 'received_at')
    search_fields = ('payment__order__order_number', 'status')
    readonly_fields = ('webhook_data', 'received_at', 'processed_at')
    
    fieldsets = (
        ('Informations', {
            'fields': ('payment', 'status', 'processed', 'processing_error')
        }),
        ('Données du webhook', {
            'fields': ('webhook_data',)
        }),
        ('Dates', {
            'fields': ('received_at', 'processed_at')
        }),
    )
    
    def payment_order(self, obj):
        if obj.payment:
            return obj.payment.order.order_number
        return 'N/A'
    payment_order.short_description = 'N° Commande'
    
    def processed_badge(self, obj):
        """Badge pour montrer si traité"""
        if obj.processed:
            return format_html(
                '<span style="background-color: #4CAF50; color: white; padding: 5px 10px; border-radius: 3px;">✓ Traité</span>'
            )
        else:
            return format_html(
                '<span style="background-color: #FF9800; color: white; padding: 5px 10px; border-radius: 3px;">⏳ En attente</span>'
            )
    processed_badge.short_description = 'Traitement'
    
    def has_delete_permission(self, request, obj=None):
        return False
