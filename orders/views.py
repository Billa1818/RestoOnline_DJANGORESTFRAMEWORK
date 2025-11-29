# ===================================
# orders/views.py
# ===================================

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.utils import timezone
from django.db.models import Q
from .models import Order, OrderItem, Cart, CartItem
from .serializers import (
    OrderSerializer, OrderCreateSerializer, OrderListSerializer,
    CartSerializer, CartItemSerializer
)
from notifications.utils import (
    notify_device_on_order_created,
    notify_admin_on_order_created,
    notify_device_on_order_accepted,
    notify_device_on_order_refused,
    notify_device_on_order_ready,
    notify_all_admin
)


class OrderViewSet(viewsets.ModelViewSet):
    """ViewSet pour les commandes"""
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    lookup_field = 'order_number'
    
    def get_permissions(self):
        if self.action in ['create', 'track', 'list', 'pending', 'active', 'retrieve']:
            return [AllowAny()]
        return [IsAuthenticated()]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return OrderCreateSerializer
        if self.action == 'list':
            return OrderListSerializer
        return OrderSerializer
    
    def get_queryset(self):
        queryset = Order.objects.select_related(
            'device', 'manager', 'delivery_person'
        ).prefetch_related('items')
        
        # Filtres
        status_param = self.request.query_params.get('status', None)
        device_id = self.request.query_params.get('device_id', None)
        delivery_person_id = self.request.query_params.get('delivery_person_id', None)
        
        if status_param:
            queryset = queryset.filter(status=status_param)
        
        if device_id:
            queryset = queryset.filter(device__device_id=device_id)
        
        if delivery_person_id:
            queryset = queryset.filter(delivery_person_id=delivery_person_id)
        
        return queryset.order_by('-created_at')
    
    @action(detail=False, methods=['get'])
    def pending(self, request):
        """Commandes en attente"""
        pending_orders = self.get_queryset().filter(status='pending')
        serializer = OrderListSerializer(pending_orders, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def active(self, request):
        """Commandes actives (en cours)"""
        active_orders = self.get_queryset().filter(
            status__in=['accepted', 'preparing', 'ready', 'assigned', 'in_delivery']
        )
        serializer = OrderListSerializer(active_orders, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def accept(self, request, order_number=None):
        """Accepter une commande (Manager)"""
        order = self.get_object()
        
        if order.status != 'pending':
            return Response(
                {'error': 'Seules les commandes en attente peuvent être acceptées'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        order.status = 'accepted'
        order.manager = request.user
        order.accepted_at = timezone.now()
        order.save()
        
        # Notifier le client
        if order.device:
            notify_device_on_order_accepted(
                device=order.device,
                order_number=order.order_number
            )
        
        serializer = OrderSerializer(order)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def refuse(self, request, order_number=None):
        """Refuser une commande (Manager)"""
        order = self.get_object()
        
        if order.status != 'pending':
            return Response(
                {'error': 'Seules les commandes en attente peuvent être refusées'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        reason = request.data.get('reason', '')
        order.status = 'refused'
        order.manager = request.user
        order.refusal_reason = reason
        order.save()
        
        # Notifier le client
        if order.device:
            notify_device_on_order_refused(
                device=order.device,
                order_number=order.order_number,
                reason=reason
            )
        
        serializer = OrderSerializer(order)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def start_preparing(self, request, order_number=None):
        """Démarrer la préparation"""
        order = self.get_object()
        
        if order.status != 'accepted':
            return Response(
                {'error': 'La commande doit être acceptée'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        order.status = 'preparing'
        order.save()
        
        return Response({'status': 'preparing'})
    
    @action(detail=True, methods=['post'])
    def mark_ready(self, request, order_number=None):
        """Marquer comme prête"""
        order = self.get_object()
        
        if order.status != 'preparing':
            return Response(
                {'error': 'La commande doit être en préparation'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        order.status = 'ready'
        order.ready_at = timezone.now()
        order.save()
        
        # Notifier le client
        if order.device:
            notify_device_on_order_ready(
                device=order.device,
                order_number=order.order_number
            )
        
        return Response({'status': 'ready'})
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, order_number=None):
        """Annuler une commande (Client ou Manager)"""
        order = self.get_object()
        
        if order.status in ['delivered', 'cancelled']:
            return Response(
                {'error': 'Cette commande ne peut pas être annulée'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        order.status = 'cancelled'
        order.cancellation_reason = request.data.get('reason', '')
        order.save()
        
        return Response({'status': 'cancelled'})
    
    @action(detail=True, methods=['get'], permission_classes=[AllowAny])
    def track(self, request, order_number=None):
        """Suivre une commande (public avec order_number)"""
        order = self.get_object()
        serializer = OrderSerializer(order)
        
        # Ajouter la position du livreur si en livraison
        data = serializer.data
        if order.status == 'in_delivery' and hasattr(order, 'assignment'):
            from delivery.models import DeliveryLocation
            latest_location = DeliveryLocation.objects.filter(
                assignment=order.assignment
            ).first()
            
            if latest_location:
                data['delivery_location'] = {
                    'latitude': float(latest_location.latitude),
                    'longitude': float(latest_location.longitude),
                    'timestamp': latest_location.timestamp
                }
        
        return Response(data)
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Statistiques des commandes"""
        queryset = self.get_queryset()
        
        return Response({
            'total': queryset.count(),
            'pending': queryset.filter(status='pending').count(),
            'active': queryset.filter(
                status__in=['accepted', 'preparing', 'ready', 'assigned', 'in_delivery']
            ).count(),
            'delivered': queryset.filter(status='delivered').count(),
            'cancelled': queryset.filter(status='cancelled').count(),
            'refused': queryset.filter(status='refused').count(),
        })


class CartViewSet(viewsets.ModelViewSet):
    """ViewSet pour les paniers"""
    queryset = Cart.objects.all()
    serializer_class = CartSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        device_id = self.request.query_params.get('device_id', None)
        if device_id:
            return Cart.objects.filter(device__device_id=device_id)
        return Cart.objects.all()
    
    @action(detail=False, methods=['get', 'post'])
    def my_cart(self, request):
        """Obtenir ou créer le panier d'un appareil"""
        device_id = request.data.get('device_id') or request.query_params.get('device_id')
        
        if not device_id:
            return Response(
                {'error': 'device_id requis'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        from accounts.models import ClientDevice
        device, _ = ClientDevice.objects.get_or_create(device_id=device_id)
        cart, _ = Cart.objects.get_or_create(device=device)
        
        serializer = CartSerializer(cart)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def add_item(self, request, pk=None):
        """Ajouter un article au panier"""
        cart = self.get_object()
        menu_item_id = request.data.get('menu_item_id')
        size_id = request.data.get('size_id')
        quantity = request.data.get('quantity', 1)
        special_instructions = request.data.get('special_instructions', '')
        
        from menu.models import MenuItem, MenuItemSize
        
        try:
            menu_item = MenuItem.objects.get(id=menu_item_id, is_available=True)
            size = MenuItemSize.objects.get(id=size_id, menu_item=menu_item, is_available=True)
        except (MenuItem.DoesNotExist, MenuItemSize.DoesNotExist):
            return Response(
                {'error': 'Article ou format non disponible'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Vérifier si l'article existe déjà dans le panier
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            menu_item=menu_item,
            size=size,
            defaults={
                'quantity': quantity,
                'special_instructions': special_instructions
            }
        )
        
        if not created:
            cart_item.quantity += quantity
            cart_item.save()
        
        serializer = CartSerializer(cart)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def update_item(self, request, pk=None):
        """Mettre à jour la quantité d'un article"""
        cart = self.get_object()
        item_id = request.data.get('item_id')
        quantity = request.data.get('quantity')
        
        try:
            cart_item = CartItem.objects.get(id=item_id, cart=cart)
            if quantity > 0:
                cart_item.quantity = quantity
                cart_item.save()
            else:
                cart_item.delete()
        except CartItem.DoesNotExist:
            return Response(
                {'error': 'Article non trouvé'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = CartSerializer(cart)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def remove_item(self, request, pk=None):
        """Retirer un article du panier"""
        cart = self.get_object()
        item_id = request.data.get('item_id')
        
        try:
            cart_item = CartItem.objects.get(id=item_id, cart=cart)
            cart_item.delete()
        except CartItem.DoesNotExist:
            return Response(
                {'error': 'Article non trouvé'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = CartSerializer(cart)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def clear(self, request, pk=None):
        """Vider le panier"""
        cart = self.get_object()
        cart.items.all().delete()
        
        serializer = CartSerializer(cart)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def checkout(self, request, pk=None):
        """Transformer le panier en commande"""
        cart = self.get_object()
        
        if not cart.items.exists():
            return Response(
                {'error': 'Le panier est vide'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Préparer les données de commande
        order_data = {
            'device': cart.device.id,
            'delivery_address': request.data.get('delivery_address'),
            'delivery_latitude': request.data.get('delivery_latitude'),
            'delivery_longitude': request.data.get('delivery_longitude'),
            'delivery_description': request.data.get('delivery_description', ''),
            'customer_name': request.data.get('customer_name'),
            'customer_phone': request.data.get('customer_phone'),
            'customer_email': request.data.get('customer_email', ''),
            'delivery_fee': request.data.get('delivery_fee', 0),
            'notes': request.data.get('notes', ''),
            'items': []
        }
        
        # Ajouter les articles du panier
        for cart_item in cart.items.all():
            order_data['items'].append({
                'size_id': cart_item.size.id,
                'quantity': cart_item.quantity,
                'special_instructions': cart_item.special_instructions
            })
        
        # Créer la commande
        serializer = OrderCreateSerializer(data=order_data)
        if serializer.is_valid():
            order = serializer.save()
            # Vider le panier
            cart.items.all().delete()
            
            return Response(
                OrderSerializer(order).data,
                status=status.HTTP_201_CREATED
            )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

