
# ===================================
# orders/serializers.py
# ===================================

from rest_framework import serializers
from .models import Order, OrderItem, Cart, CartItem
from menu.serializers import MenuItemListSerializer, MenuItemSizeSerializer
from accounts.serializers import DeliveryPersonSerializer, ClientDeviceSerializer


class OrderItemSerializer(serializers.ModelSerializer):
    """Serializer pour OrderItem"""
    menu_item_details = MenuItemListSerializer(source='menu_item', read_only=True)
    size_details = MenuItemSizeSerializer(source='size', read_only=True)
    
    class Meta:
        model = OrderItem
        fields = [
            'id', 'menu_item', 'size', 'menu_item_details', 'size_details',
            'item_name', 'size_name', 'item_price', 'quantity',
            'subtotal', 'special_instructions', 'created_at'
        ]
        read_only_fields = ['id', 'item_name', 'size_name', 'item_price', 'subtotal', 'created_at']


class OrderSerializer(serializers.ModelSerializer):
    """Serializer complet pour Order"""
    items = OrderItemSerializer(many=True, read_only=True)
    device_info = ClientDeviceSerializer(source='device', read_only=True)
    manager_info = serializers.SerializerMethodField()
    delivery_person_info = DeliveryPersonSerializer(source='delivery_person', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'device', 'device_info',
            'delivery_address', 'delivery_latitude', 'delivery_longitude',
            'delivery_description', 'customer_name', 'customer_phone',
            'customer_email', 'status', 'status_display', 'manager',
            'manager_info', 'delivery_person', 'delivery_person_info',
            'subtotal', 'delivery_fee', 'total', 'notes',
            'cancellation_reason', 'refusal_reason', 'items',
            'created_at', 'accepted_at', 'ready_at', 'assigned_at',
            'picked_up_at', 'delivered_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'order_number', 'subtotal', 'total',
            'created_at', 'accepted_at', 'ready_at', 'assigned_at',
            'picked_up_at', 'delivered_at', 'updated_at'
        ]
    
    def get_manager_info(self, obj):
        if obj.manager:
            return {
                'id': obj.manager.id,
                'username': obj.manager.username,
                'name': obj.manager.get_full_name()
            }
        return None


class OrderCreateSerializer(serializers.ModelSerializer):
    """Serializer pour la création d'une commande"""
    items = serializers.ListField(child=serializers.DictField(), write_only=True)
    
    class Meta:
        model = Order
        fields = [
            'device', 'delivery_address', 'delivery_latitude',
            'delivery_longitude', 'delivery_description',
            'customer_name', 'customer_phone', 'customer_email',
            'delivery_fee', 'notes', 'items'
        ]
    
    def validate_items(self, value):
        if not value:
            raise serializers.ValidationError("La commande doit contenir au moins un article.")
        return value
    
    def create(self, validated_data):
        from menu.models import MenuItem, MenuItemSize
        import uuid
        
        items_data = validated_data.pop('items')
        
        # Générer le numéro de commande
        validated_data['order_number'] = f"ORD-{uuid.uuid4().hex[:8].upper()}"
        
        # Calculer le sous-total
        subtotal = 0
        for item_data in items_data:
            size = MenuItemSize.objects.get(id=item_data['size_id'])
            subtotal += size.price * item_data['quantity']
        
        validated_data['subtotal'] = subtotal
        validated_data['total'] = subtotal + validated_data.get('delivery_fee', 0)
        
        # Créer la commande
        order = Order.objects.create(**validated_data)
        
        # Créer les items
        for item_data in items_data:
            size = MenuItemSize.objects.get(id=item_data['size_id'])
            OrderItem.objects.create(
                order=order,
                menu_item=size.menu_item,
                size=size,
                item_name=size.menu_item.name,
                size_name=size.get_size_display(),
                item_price=size.price,
                quantity=item_data['quantity'],
                subtotal=size.price * item_data['quantity'],
                special_instructions=item_data.get('special_instructions', '')
            )
        
        return order


class OrderListSerializer(serializers.ModelSerializer):
    """Serializer simplifié pour les listes de commandes"""
    items_count = serializers.SerializerMethodField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'customer_name', 'customer_phone',
            'status', 'status_display', 'total', 'items_count',
            'created_at', 'delivered_at'
        ]
    
    def get_items_count(self, obj):
        return obj.items.count()


class CartItemSerializer(serializers.ModelSerializer):
    """Serializer pour CartItem"""
    menu_item_details = MenuItemListSerializer(source='menu_item', read_only=True)
    size_details = MenuItemSizeSerializer(source='size', read_only=True)
    item_total = serializers.SerializerMethodField()
    
    class Meta:
        model = CartItem
        fields = [
            'id', 'menu_item', 'size', 'menu_item_details',
            'size_details', 'quantity', 'special_instructions',
            'item_total', 'added_at', 'updated_at'
        ]
        read_only_fields = ['id', 'added_at', 'updated_at']
    
    def get_item_total(self, obj):
        return obj.size.price * obj.quantity


class CartSerializer(serializers.ModelSerializer):
    """Serializer pour Cart"""
    items = CartItemSerializer(many=True, read_only=True)
    total_items = serializers.SerializerMethodField()
    total_amount = serializers.SerializerMethodField()
    
    class Meta:
        model = Cart
        fields = [
            'id', 'device', 'items', 'total_items',
            'total_amount', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_total_items(self, obj):
        return sum(item.quantity for item in obj.items.all())
    
    def get_total_amount(self, obj):
        return sum(item.size.price * item.quantity for item in obj.items.all())

