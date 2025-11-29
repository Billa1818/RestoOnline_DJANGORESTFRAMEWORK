from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, ClientDevice

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Administration pour le modèle utilisateur personnalisé"""
    list_display = (
        'username', 'email', 'user_type', 'is_active', 'is_staff', 'is_superuser',
        'is_available', 'total_deliveries', 'average_rating', 'last_login', 'date_joined'
    )
    list_filter = ('user_type', 'is_active', 'is_available', 'is_staff', 'is_superuser')
    search_fields = ('username', 'email', 'phone', 'first_name', 'last_name')
    ordering = ('username',)
    readonly_fields = ('total_deliveries', 'average_rating', 'date_joined', 'last_login')
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Informations personnelles', {'fields': ('first_name', 'last_name', 'email', 'phone', 'profile_picture')}),
        ('Permissions', {'fields': ('user_type', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Statistiques livreur', {'fields': ('total_deliveries', 'average_rating', 'is_available')}),
        ('Dates', {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'user_type', 'is_active', 'is_staff')}
        ),
    )

@admin.register(ClientDevice)
class ClientDeviceAdmin(admin.ModelAdmin):
    list_display = (
        'device_id', 'device_name', 'customer_name', 'customer_email', 'is_active', 'is_blocked', 'first_seen', 'last_seen'
    )
    list_filter = ('is_active', 'is_blocked')
    search_fields = ('device_id', 'device_name', 'customer_name', 'customer_email', 'customer_phone')
    readonly_fields = ('first_seen', 'last_seen')
    ordering = ('-last_seen',)
