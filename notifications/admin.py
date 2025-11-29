from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.db.models import Q
from .models import Notification, NotificationTemplate


class DeviceFilter(admin.SimpleListFilter):
    """Filtre personnalisé pour les appareils"""
    title = 'Appareil'
    parameter_name = 'device'
    
    def lookups(self, request, model_admin):
        devices = Notification.objects.filter(device__isnull=False).values_list(
            'device__device_id', flat=True
        ).distinct()[:20]
        return [(device, device[:30] + '...' if len(device) > 30 else device) for device in devices]
    
    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(device__device_id=self.value())
        return queryset


class UserFilter(admin.SimpleListFilter):
    """Filtre personnalisé pour les utilisateurs"""
    title = 'Utilisateur'
    parameter_name = 'user'
    
    def lookups(self, request, model_admin):
        users = Notification.objects.filter(user__isnull=False).values_list(
            'user__username', flat=True
        ).distinct()[:20]
        return [(user, user) for user in users]
    
    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(user__username=self.value())
        return queryset


class ReadStatusFilter(admin.SimpleListFilter):
    """Filtre pour le statut de lecture"""
    title = 'Statut de lecture'
    parameter_name = 'read_status'
    
    def lookups(self, request, model_admin):
        return (
            ('unread', 'Non lues'),
            ('read', 'Lues'),
        )
    
    def queryset(self, request, queryset):
        if self.value() == 'unread':
            return queryset.filter(is_read=False)
        elif self.value() == 'read':
            return queryset.filter(is_read=True)
        return queryset


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    """Admin amélioré pour les notifications"""
    
    # Affichage en liste
    list_display = (
        'id', 
        'type_badge', 
        'recipient_info', 
        'title_short',
        'read_status_badge',
        'order_info',
        'created_date',
        'action_buttons'
    )
    
    # Filtres personnalisés
    list_filter = (
        'type',
        ReadStatusFilter,
        DeviceFilter,
        UserFilter,
        ('created_at', admin.DateFieldListFilter),
    )
    
    # Recherche
    search_fields = (
        'title',
        'message',
        'device__device_id',
        'device__customer_name',
        'user__username',
        'user__email',
        'order_id',
    )
    
    # Champs en lecture seule
    readonly_fields = (
        'created_at',
        'updated_at',
        'read_at',
        'formatted_data',
        'type_display',
        'recipient_details',
    )
    
    # Organisation en sections
    fieldsets = (
        ('📬 Destinataire', {
            'fields': ('device', 'user', 'recipient_details')
        }),
        ('📝 Contenu', {
            'fields': ('type', 'type_display', 'title', 'message', 'formatted_data'),
            'classes': ('wide',)
        }),
        ('🔗 Références', {
            'fields': ('order_id', 'delivery_id', 'related_user_id'),
            'classes': ('collapse',)
        }),
        ('📖 Statut de lecture', {
            'fields': ('is_read', 'read_at'),
            'classes': ('collapse',)
        }),
        ('⏰ Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse', 'grp-collapse grp-closed'),
            'description': 'Ces champs ne peuvent pas être modifiés'
        }),
    )
    
    # Actions en masse
    actions = ['mark_as_read', 'mark_as_unread', 'delete_selected']
    
    # Pagination
    list_per_page = 50
    date_hierarchy = 'created_at'
    
    # Tri par défaut
    ordering = ('-created_at',)
    
    def has_add_permission(self, request):
        """Les notifications sont créées automatiquement, pas manuellement"""
        return True
    
    def has_delete_permission(self, request, obj=None):
        """Autoriser la suppression"""
        return True
    
    # === Méthodes personnalisées pour l'affichage ===
    
    def type_badge(self, obj):
        """Affiche le type avec un badge coloré"""
        colors = {
            'order_created': '#3498db',
            'order_accepted': '#2ecc71',
            'order_refused': '#e74c3c',
            'order_preparing': '#f39c12',
            'order_ready': '#27ae60',
            'order_assigned': '#9b59b6',
            'order_in_delivery': '#3498db',
            'order_delivered': '#16a085',
            'delivery_assigned': '#8e44ad',
            'delivery_accepted': '#27ae60',
            'delivery_completed': '#16a085',
            'payment_received': '#27ae60',
            'payment_failed': '#e74c3c',
            'rating_received': '#f39c12',
            'account_created': '#3498db',
        }
        color = colors.get(obj.type, '#95a5a6')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; '
            'border-radius: 3px; font-weight: bold;">{}</span>',
            color,
            obj.get_type_display()
        )
    type_badge.short_description = 'Type'
    
    def recipient_info(self, obj):
        """Affiche le destinataire avec icône"""
        if obj.device:
            return format_html(
                '📱 <strong>Device</strong><br/><small>{}</small>',
                obj.device.device_id[:25] + '...' if len(obj.device.device_id) > 25 else obj.device.device_id
            )
        elif obj.user:
            return format_html(
                '👤 <strong>User</strong><br/><small>{}</small>',
                obj.user.username
            )
        return '❌ N/A'
    recipient_info.short_description = 'Destinataire'
    
    def recipient_details(self, obj):
        """Affiche les détails du destinataire"""
        if obj.device:
            return format_html(
                '<strong>Appareil:</strong> {}<br/>'
                '<strong>Client:</strong> {}<br/>'
                '<strong>Téléphone:</strong> {}<br/>'
                '<strong>Email:</strong> {}',
                obj.device.device_id,
                obj.device.customer_name or 'N/A',
                obj.device.customer_phone or 'N/A',
                obj.device.customer_email or 'N/A'
            )
        elif obj.user:
            return format_html(
                '<strong>Utilisateur:</strong> {}<br/>'
                '<strong>Email:</strong> {}<br/>'
                '<strong>Type:</strong> {}',
                obj.user.username,
                obj.user.email,
                obj.user.get_user_type_display()
            )
        return 'Pas de destinataire'
    recipient_details.short_description = 'Détails du destinataire'
    
    def title_short(self, obj):
        """Affiche le titre raccourci"""
        return obj.title[:50] + '...' if len(obj.title) > 50 else obj.title
    title_short.short_description = 'Titre'
    
    def read_status_badge(self, obj):
        """Affiche le statut de lecture avec badge"""
        if obj.is_read:
            return format_html(
                '<span style="background-color: #95a5a6; color: white; padding: 3px 8px; '
                'border-radius: 3px;">✓ Lue</span>'
            )
        else:
            return format_html(
                '<span style="background-color: #e74c3c; color: white; padding: 3px 8px; '
                'border-radius: 3px;">● Non lue</span>'
            )
    read_status_badge.short_description = 'Statut'
    
    def order_info(self, obj):
        """Affiche les références"""
        info = []
        if obj.order_id:
            info.append(f"📋 Order: {obj.order_id}")
        if obj.delivery_id:
            info.append(f"🚚 Delivery: {obj.delivery_id}")
        if obj.related_user_id:
            info.append(f"👤 User: {obj.related_user_id}")
        return format_html('<br/>'.join(info)) if info else '—'
    order_info.short_description = 'Références'
    
    def created_date(self, obj):
        """Affiche la date de création"""
        return obj.created_at.strftime('%d/%m/%Y %H:%M')
    created_date.short_description = 'Créée le'
    
    def type_display(self, obj):
        """Affiche le type en lecture seule"""
        return obj.get_type_display()
    type_display.short_description = 'Type (affichage)'
    
    def formatted_data(self, obj):
        """Affiche les données JSON formatées"""
        import json
        if obj.data:
            return format_html(
                '<pre style="background-color: #f5f5f5; padding: 10px; '
                'border-radius: 3px; overflow-x: auto;">{}</pre>',
                json.dumps(obj.data, indent=2, ensure_ascii=False)
            )
        return '—'
    formatted_data.short_description = 'Données JSON'
    
    def action_buttons(self, obj):
        """Boutons d'action rapide"""
        buttons = []
        
        if not obj.is_read:
            buttons.append(
                f'<a class="button" href="javascript:void(0);" '
                f'onclick="admin_action(\'mark_read\', {obj.id})">Marquer lue</a>'
            )
        else:
            buttons.append(
                f'<a class="button" style="background-color: #417690;" '
                f'href="javascript:void(0);" onclick="admin_action(\'mark_unread\', {obj.id})">Marquer non lue</a>'
            )
        
        return format_html(' '.join(buttons))
    action_buttons.short_description = 'Actions'
    
    # === Actions en masse ===
    
    def mark_as_read(self, request, queryset):
        """Action: Marquer comme lues"""
        updated = queryset.filter(is_read=False).update(is_read=True)
        self.message_user(request, f'{updated} notification(s) marquée(s) comme lue(s).')
    mark_as_read.short_description = '✓ Marquer les sélectionnées comme lues'
    
    def mark_as_unread(self, request, queryset):
        """Action: Marquer comme non lues"""
        updated = queryset.filter(is_read=True).update(is_read=False)
        self.message_user(request, f'{updated} notification(s) marquée(s) comme non lue(s).')
    mark_as_unread.short_description = '● Marquer les sélectionnées comme non lues'
    
    def delete_selected(self, request, queryset):
        """Action: Supprimer (surcharge du défaut)"""
        count = queryset.count()
        queryset.delete()
        self.message_user(request, f'{count} notification(s) supprimée(s).')
    delete_selected.short_description = '🗑 Supprimer les sélectionnées'
    
    # Customisation CSS
    class Media:
        css = {
            'all': ('admin/css/notifications_admin.css',)
        }
        js = ('admin/js/notifications_admin.js',)


@admin.register(NotificationTemplate)
class NotificationTemplateAdmin(admin.ModelAdmin):
    """Admin pour les templates de notification"""
    
    # Affichage en liste
    list_display = (
        'type',
        'title_preview',
        'usage_count',
        'created_date',
        'modified_date'
    )
    
    # Filtres
    list_filter = (
        ('created_at', admin.DateFieldListFilter),
        ('updated_at', admin.DateFieldListFilter),
    )
    
    # Recherche
    search_fields = (
        'type',
        'title_template',
        'message_template',
        'description'
    )
    
    # Champs en lecture seule
    readonly_fields = (
        'created_at',
        'updated_at',
        'usage_count_display',
        'preview'
    )
    
    # Organisation en sections
    fieldsets = (
        ('📋 Information', {
            'fields': ('type', 'description')
        }),
        ('📝 Template', {
            'fields': ('title_template', 'message_template'),
            'classes': ('wide',)
        }),
        ('👁 Aperçu', {
            'fields': ('preview',),
            'classes': ('collapse',)
        }),
        ('📊 Utilisation', {
            'fields': ('usage_count_display',),
            'classes': ('collapse',)
        }),
        ('⏰ Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse', 'grp-collapse grp-closed'),
            'description': 'Ces champs ne peuvent pas être modifiés'
        }),
    )
    
    # Tri par défaut
    ordering = ('-created_at',)
    
    # === Méthodes personnalisées ===
    
    def title_preview(self, obj):
        """Aperçu du titre"""
        return obj.title_template[:60] + '...' if len(obj.title_template) > 60 else obj.title_template
    title_preview.short_description = 'Titre Template'
    
    def usage_count(self, obj):
        """Compte l'utilisation"""
        count = Notification.objects.filter(type=obj.type).count()
        return format_html(
            '<span style="background-color: #3498db; color: white; padding: 3px 8px; '
            'border-radius: 3px;"><strong>{}</strong></span>',
            count
        )
    usage_count.short_description = 'Utilisations'
    
    def usage_count_display(self, obj):
        """Affiche le nombre d'utilisations"""
        count = Notification.objects.filter(type=obj.type).count()
        return f'{count} notification(s) de ce type'
    usage_count_display.short_description = 'Nombre de notifications'
    
    def created_date(self, obj):
        """Date de création"""
        return obj.created_at.strftime('%d/%m/%Y')
    created_date.short_description = 'Créé'
    
    def modified_date(self, obj):
        """Date de modification"""
        return obj.updated_at.strftime('%d/%m/%Y')
    modified_date.short_description = 'Modifié'
    
    def preview(self, obj):
        """Aperçu du template"""
        return format_html(
            '<div style="background-color: #ecf0f1; padding: 15px; border-radius: 5px;">'
            '<h4 style="margin-top: 0;">{}</h4>'
            '<p style="margin-bottom: 0; white-space: pre-wrap;">{}</p>'
            '</div>',
            obj.title_template,
            obj.message_template
        )
    preview.short_description = 'Aperçu'
