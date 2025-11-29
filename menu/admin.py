from django.contrib import admin
from .models import Category, MenuItem, MenuItemSize

# Inline pour afficher les tailles directement dans le menu item
class MenuItemSizeInline(admin.TabularInline):
    model = MenuItemSize
    extra = 1  # Nombre de formulaires vides par défaut
    readonly_fields = ('created_at', 'updated_at')
    fields = ('size', 'price', 'is_available', 'portion_description')

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'order', 'is_active', 'created_at', 'updated_at')
    list_filter = ('is_active',)
    search_fields = ('name', 'slug', 'description')
    prepopulated_fields = {"slug": ("name",)}
    ordering = ('order', 'name')
    readonly_fields = ('created_at', 'updated_at')

@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'is_available', 'preparation_time', 'total_orders', 'average_rating', 'total_ratings')
    list_filter = ('category', 'is_available')
    search_fields = ('name', 'description', 'ingredients')
    prepopulated_fields = {"slug": ("name",)}
    inlines = [MenuItemSizeInline]
    readonly_fields = ('total_orders', 'average_rating', 'total_ratings', 'created_at', 'updated_at')
    ordering = ('category', 'name')

@admin.register(MenuItemSize)
class MenuItemSizeAdmin(admin.ModelAdmin):
    list_display = ('menu_item', 'size', 'price', 'is_available', 'portion_description')
    list_filter = ('size', 'is_available')
    search_fields = ('menu_item__name', 'portion_description')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('menu_item', 'size')
