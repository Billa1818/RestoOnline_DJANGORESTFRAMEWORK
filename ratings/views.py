# ===================================
# ratings/views.py
# ===================================

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.db.models import Avg
from .models import DeliveryRating, MenuItemRating
from .serializers import (
    DeliveryRatingSerializer, DeliveryRatingCreateSerializer,
    MenuItemRatingSerializer, MenuItemRatingCreateSerializer
)


class DeliveryRatingViewSet(viewsets.ModelViewSet):
    """ViewSet pour les notes de livraison"""
    queryset = DeliveryRating.objects.all()
    serializer_class = DeliveryRatingSerializer
    
    def get_permissions(self):
        if self.action in ['create']:
            return [AllowAny()]
        return [IsAuthenticated()]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return DeliveryRatingCreateSerializer
        return DeliveryRatingSerializer
    
    def get_queryset(self):
        queryset = DeliveryRating.objects.select_related(
            'order', 'device', 'delivery_person'
        )
        
        # Filtres
        delivery_person_id = self.request.query_params.get('delivery_person_id', None)
        device_id = self.request.query_params.get('device_id', None)
        order_id = self.request.query_params.get('order_id', None)
        
        if delivery_person_id:
            queryset = queryset.filter(delivery_person_id=delivery_person_id)
        
        if device_id:
            queryset = queryset.filter(device__device_id=device_id)
        
        if order_id:
            queryset = queryset.filter(order_id=order_id)
        
        return queryset.order_by('-created_at')
    
    def create(self, request, *args, **kwargs):
        """Créer une note de livraison"""
        from orders.models import Order
        
        order_id = request.data.get('order')
        
        try:
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            return Response(
                {'error': 'Commande non trouvée'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        if order.status != 'delivered':
            return Response(
                {'error': 'Seules les commandes livrées peuvent être notées'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if hasattr(order, 'delivery_rating'):
            return Response(
                {'error': 'Cette livraison a déjà été notée'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            rating = serializer.save()
            
            # Mettre à jour la moyenne du livreur
            self._update_delivery_person_rating(rating.delivery_person)
            
            return Response(
                DeliveryRatingSerializer(rating).data,
                status=status.HTTP_201_CREATED
            )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def _update_delivery_person_rating(self, delivery_person):
        """Mettre à jour la note moyenne du livreur"""
        avg_rating = DeliveryRating.objects.filter(
            delivery_person=delivery_person
        ).aggregate(Avg('rating'))['rating__avg']
        
        if avg_rating:
            delivery_person.average_rating = round(avg_rating, 2)
            delivery_person.save()
    
    @action(detail=False, methods=['get'])
    def by_delivery_person(self, request):
        """Notes d'un livreur spécifique"""
        delivery_person_id = request.query_params.get('delivery_person_id')
        
        if not delivery_person_id:
            return Response(
                {'error': 'delivery_person_id requis'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        ratings = self.get_queryset().filter(delivery_person_id=delivery_person_id)
        serializer = DeliveryRatingSerializer(ratings, many=True)
        
        # Calculer les statistiques
        total = ratings.count()
        if total > 0:
            avg = ratings.aggregate(Avg('rating'))['rating__avg']
            distribution = {
                '5_stars': ratings.filter(rating=5).count(),
                '4_stars': ratings.filter(rating=4).count(),
                '3_stars': ratings.filter(rating=3).count(),
                '2_stars': ratings.filter(rating=2).count(),
                '1_star': ratings.filter(rating=1).count(),
            }
        else:
            avg = 0
            distribution = {}
        
        return Response({
            'average_rating': round(avg, 2) if avg else 0,
            'total_ratings': total,
            'distribution': distribution,
            'ratings': serializer.data
        })


class MenuItemRatingViewSet(viewsets.ModelViewSet):
    """ViewSet pour les notes de plats"""
    queryset = MenuItemRating.objects.all()
    serializer_class = MenuItemRatingSerializer
    
    def get_permissions(self):
        if self.action in ['create', 'by_menu_item']:
            return [AllowAny()]
        return [IsAuthenticated()]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return MenuItemRatingCreateSerializer
        return MenuItemRatingSerializer
    
    def get_queryset(self):
        queryset = MenuItemRating.objects.select_related(
            'order_item', 'order', 'device', 'menu_item'
        )
        
        # Filtres
        menu_item_id = self.request.query_params.get('menu_item_id', None)
        device_id = self.request.query_params.get('device_id', None)
        order_id = self.request.query_params.get('order_id', None)
        
        if menu_item_id:
            queryset = queryset.filter(menu_item_id=menu_item_id)
        
        if device_id:
            queryset = queryset.filter(device__device_id=device_id)
        
        if order_id:
            queryset = queryset.filter(order_id=order_id)
        
        return queryset.order_by('-created_at')
    
    def create(self, request, *args, **kwargs):
        """Créer une note de plat"""
        from orders.models import Order, OrderItem
        
        order_id = request.data.get('order')
        order_item_id = request.data.get('order_item')
        
        try:
            order = Order.objects.get(id=order_id)
            order_item = OrderItem.objects.get(id=order_item_id, order=order)
        except (Order.DoesNotExist, OrderItem.DoesNotExist):
            return Response(
                {'error': 'Commande ou article non trouvé'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        if order.status != 'delivered':
            return Response(
                {'error': 'Seules les commandes livrées peuvent être notées'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Vérifier si cet article a déjà été noté
        if MenuItemRating.objects.filter(
            order_item=order_item,
            device__device_id=request.data.get('device')
        ).exists():
            return Response(
                {'error': 'Cet article a déjà été noté'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            rating = serializer.save()
            
            # Mettre à jour la moyenne du plat
            self._update_menu_item_rating(rating.menu_item)
            
            return Response(
                MenuItemRatingSerializer(rating).data,
                status=status.HTTP_201_CREATED
            )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def _update_menu_item_rating(self, menu_item):
        """Mettre à jour la note moyenne du plat"""
        ratings = MenuItemRating.objects.filter(menu_item=menu_item)
        total = ratings.count()
        
        if total > 0:
            avg = ratings.aggregate(Avg('rating'))['rating__avg']
            menu_item.average_rating = round(avg, 2)
            menu_item.total_ratings = total
            menu_item.save()
    
    @action(detail=False, methods=['get'])
    def by_menu_item(self, request):
        """Notes d'un plat spécifique"""
        menu_item_id = request.query_params.get('menu_item_id')
        
        if not menu_item_id:
            return Response(
                {'error': 'menu_item_id requis'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        ratings = self.get_queryset().filter(menu_item_id=menu_item_id)
        serializer = MenuItemRatingSerializer(ratings, many=True)
        
        # Calculer les statistiques
        total = ratings.count()
        if total > 0:
            avg = ratings.aggregate(Avg('rating'))['rating__avg']
            distribution = {
                '5_stars': ratings.filter(rating=5).count(),
                '4_stars': ratings.filter(rating=4).count(),
                '3_stars': ratings.filter(rating=3).count(),
                '2_stars': ratings.filter(rating=2).count(),
                '1_star': ratings.filter(rating=1).count(),
            }
            
            # Moyennes des critères spécifiques
            taste_avg = ratings.exclude(taste_rating__isnull=True).aggregate(
                Avg('taste_rating')
            )['taste_rating__avg']
            presentation_avg = ratings.exclude(presentation_rating__isnull=True).aggregate(
                Avg('presentation_rating')
            )['presentation_rating__avg']
            portion_avg = ratings.exclude(portion_rating__isnull=True).aggregate(
                Avg('portion_rating')
            )['portion_rating__avg']
        else:
            avg = 0
            distribution = {}
            taste_avg = presentation_avg = portion_avg = None
        
        return Response({
            'average_rating': round(avg, 2) if avg else 0,
            'total_ratings': total,
            'distribution': distribution,
            'criteria_averages': {
                'taste': round(taste_avg, 2) if taste_avg else None,
                'presentation': round(presentation_avg, 2) if presentation_avg else None,
                'portion': round(portion_avg, 2) if portion_avg else None,
            },
            'ratings': serializer.data
        })
    
    @action(detail=False, methods=['post'])
    def rate_order_items(self, request):
        """Noter plusieurs plats d'une commande en une fois"""
        from orders.models import Order
        
        order_id = request.data.get('order_id')
        items_ratings = request.data.get('items', [])
        
        if not order_id or not items_ratings:
            return Response(
                {'error': 'order_id et items requis'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            return Response(
                {'error': 'Commande non trouvée'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        if order.status != 'delivered':
            return Response(
                {'error': 'Seules les commandes livrées peuvent être notées'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        created_ratings = []
        errors = []
        
        for item_rating in items_ratings:
            item_rating['order'] = order_id
            serializer = MenuItemRatingCreateSerializer(data=item_rating)
            
            if serializer.is_valid():
                rating = serializer.save()
                self._update_menu_item_rating(rating.menu_item)
                created_ratings.append(MenuItemRatingSerializer(rating).data)
            else:
                errors.append({
                    'order_item_id': item_rating.get('order_item'),
                    'errors': serializer.errors
                })
        
        return Response({
            'created': created_ratings,
            'errors': errors
        }, status=status.HTTP_201_CREATED if created_ratings else status.HTTP_400_BAD_REQUEST)


