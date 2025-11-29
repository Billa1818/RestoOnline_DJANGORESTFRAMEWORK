# ===================================
# delivery/views.py
# ===================================

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.db.models import Q
from .models import DeliveryAssignment, DeliveryLocation
from .serializers import (
    DeliveryAssignmentSerializer, DeliveryAssignmentCreateSerializer,
    DeliveryAssignmentListSerializer, DeliveryLocationSerializer
)
from orders.models import Order
from notifications.utils import (
    notify_delivery_person_on_assignment,
    notify_device_on_order_in_delivery,
    notify_device_on_order_delivered,
    notify_admin_on_delivery_completed,
    notify_all_admin
)


class DeliveryAssignmentViewSet(viewsets.ModelViewSet):
    """ViewSet pour les affectations de livraison"""
    queryset = DeliveryAssignment.objects.all()
    serializer_class = DeliveryAssignmentSerializer
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return DeliveryAssignmentCreateSerializer
        if self.action == 'list':
            return DeliveryAssignmentListSerializer
        return DeliveryAssignmentSerializer
    
    def get_queryset(self):
        queryset = DeliveryAssignment.objects.select_related(
            'order', 'delivery_person', 'assigned_by'
        ).prefetch_related('locations')
        
        # Filtres
        status_param = self.request.query_params.get('status', None)
        delivery_person_id = self.request.query_params.get('delivery_person_id', None)
        
        if status_param:
            queryset = queryset.filter(status=status_param)
        
        if delivery_person_id:
            queryset = queryset.filter(delivery_person_id=delivery_person_id)
        
        # Si c'est un livreur, ne montrer que ses affectations
        if self.request.user.user_type == 'delivery':
            queryset = queryset.filter(delivery_person=self.request.user)
        
        return queryset.order_by('-assigned_at')
    
    def create(self, request, *args, **kwargs):
        """Créer une affectation (assigner une commande à un livreur)"""
        order_id = request.data.get('order')
        
        try:
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            return Response(
                {'error': 'Commande non trouvée'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        if order.status != 'ready':
            return Response(
                {'error': 'Seules les commandes prêtes peuvent être assignées'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if hasattr(order, 'assignment'):
            return Response(
                {'error': 'Cette commande est déjà assignée'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            assignment = serializer.save()
            
            # Mettre à jour le statut de la commande
            order.status = 'assigned'
            order.delivery_person = assignment.delivery_person
            order.assigned_at = timezone.now()
            order.save()
            
            # Notifier le livreur
            notify_delivery_person_on_assignment(
                delivery_person=assignment.delivery_person,
                order_number=order.order_number,
                customer_phone=order.customer_phone
            )
            
            # Notifier le client
            if order.device:
                notify_device_on_order_in_delivery(
                    device=order.device,
                    order_number=order.order_number,
                    delivery_person_name=assignment.delivery_person.get_full_name()
                )
            
            return Response(
                DeliveryAssignmentSerializer(assignment).data,
                status=status.HTTP_201_CREATED
            )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def my_deliveries(self, request):
        """Mes livraisons (pour un livreur)"""
        if request.user.user_type != 'delivery':
            return Response(
                {'error': 'Réservé aux livreurs'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        assignments = self.get_queryset().filter(delivery_person=request.user)
        serializer = DeliveryAssignmentListSerializer(assignments, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def pending(self, request):
        """Affectations en attente d'acceptation"""
        pending = self.get_queryset().filter(status='assigned')
        serializer = DeliveryAssignmentListSerializer(pending, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def active(self, request):
        """Livraisons actives"""
        active = self.get_queryset().filter(
            status__in=['accepted', 'picked_up']
        )
        serializer = DeliveryAssignmentListSerializer(active, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def accept(self, request, pk=None):
        """Accepter une affectation (Livreur)"""
        assignment = self.get_object()
        
        if assignment.delivery_person != request.user:
            return Response(
                {'error': 'Non autorisé'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if assignment.status != 'assigned':
            return Response(
                {'error': 'Cette affectation ne peut pas être acceptée'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        assignment.status = 'accepted'
        assignment.accepted_at = timezone.now()
        assignment.save()
        
        serializer = DeliveryAssignmentSerializer(assignment)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def refuse(self, request, pk=None):
        """Refuser une affectation (Livreur)"""
        assignment = self.get_object()
        
        if assignment.delivery_person != request.user:
            return Response(
                {'error': 'Non autorisé'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if assignment.status != 'assigned':
            return Response(
                {'error': 'Cette affectation ne peut pas être refusée'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        assignment.status = 'refused'
        assignment.refused_at = timezone.now()
        assignment.refusal_reason = request.data.get('reason', '')
        assignment.save()
        
        # Remettre la commande en statut "ready"
        order = assignment.order
        order.status = 'ready'
        order.delivery_person = None
        order.save()
        
        serializer = DeliveryAssignmentSerializer(assignment)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def pickup(self, request, pk=None):
        """Confirmer la récupération de la commande (Livreur)"""
        assignment = self.get_object()
        
        if assignment.delivery_person != request.user:
            return Response(
                {'error': 'Non autorisé'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if assignment.status != 'accepted':
            return Response(
                {'error': "La livraison doit d'abord être acceptée"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        assignment.status = 'picked_up'
        assignment.picked_up_at = timezone.now()
        assignment.save()
        
        # Mettre à jour le statut de la commande
        order = assignment.order
        order.status = 'in_delivery'
        order.picked_up_at = timezone.now()
        order.save()
        
        serializer = DeliveryAssignmentSerializer(assignment)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """Marquer la livraison comme complétée (Livreur)"""
        assignment = self.get_object()
        
        if assignment.delivery_person != request.user:
            return Response(
                {'error': 'Non autorisé'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if assignment.status != 'picked_up':
            return Response(
                {'error': 'La commande doit être récupérée avant'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        assignment.status = 'delivered'
        assignment.delivered_at = timezone.now()
        assignment.save()
        
        # Mettre à jour le statut de la commande
        order = assignment.order
        order.status = 'delivered'
        order.delivered_at = timezone.now()
        order.save()
        
        # Mettre à jour les statistiques du livreur
        delivery_person = assignment.delivery_person
        delivery_person.total_deliveries += 1
        delivery_person.save()
        
        # Notifier le client
        if order.device:
            notify_device_on_order_delivered(
                device=order.device,
                order_number=order.order_number
            )
        
        # Notifier les admins
        delivery_time = None
        if assignment.picked_up_at and assignment.delivered_at:
            delta = assignment.delivered_at - assignment.picked_up_at
            hours = delta.seconds // 3600
            minutes = (delta.seconds % 3600) // 60
            if hours > 0:
                delivery_time = f"{hours}h {minutes}m"
            else:
                delivery_time = f"{minutes}m"
        
        notify_admin_on_delivery_completed(
            order_number=order.order_number,
            delivery_person_name=delivery_person.get_full_name(),
            delivery_time=delivery_time or 'N/A'
        )
        
        serializer = DeliveryAssignmentSerializer(assignment)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def update_location(self, request, pk=None):
        """Mettre à jour la position du livreur"""
        assignment = self.get_object()
        
        if assignment.delivery_person != request.user:
            return Response(
                {'error': 'Non autorisé'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        latitude = request.data.get('latitude')
        longitude = request.data.get('longitude')
        accuracy = request.data.get('accuracy')
        
        if not latitude or not longitude:
            return Response(
                {'error': 'Coordonnées requises'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        location = DeliveryLocation.objects.create(
            assignment=assignment,
            latitude=latitude,
            longitude=longitude,
            accuracy=accuracy
        )
        
        serializer = DeliveryLocationSerializer(location)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def tracking(self, request, pk=None):
        """Obtenir l'historique de position"""
        assignment = self.get_object()
        locations = assignment.locations.all()[:20]  # 20 dernières positions
        serializer = DeliveryLocationSerializer(locations, many=True)
        return Response(serializer.data)


class DeliveryLocationViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet pour les positions de livraison (lecture seule)"""
    queryset = DeliveryLocation.objects.all()
    serializer_class = DeliveryLocationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = DeliveryLocation.objects.select_related('assignment')
        assignment_id = self.request.query_params.get('assignment_id', None)
        
        if assignment_id:
            queryset = queryset.filter(assignment_id=assignment_id)
        
        return queryset.order_by('-timestamp')


