from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from .models import Notification, NotificationTemplate
from .serializers import NotificationSerializer, NotificationCreateSerializer, NotificationTemplateSerializer


class NotificationViewSet(viewsets.ModelViewSet):
    """ViewSet pour les notifications"""
    serializer_class = NotificationSerializer
    permission_classes = [permissions.AllowAny]
    
    def get_queryset(self):
        """Récupérer les notifications de l'utilisateur ou de son appareil"""
        user = self.request.user
        device_id = self.request.query_params.get('device_id')
        
        queryset = Notification.objects.all()
        
        # Si c'est un utilisateur authentifié (admin, manager, livreur)
        if user.is_authenticated:
            # Admin/Manager voient toutes les notifications
            if user.user_type in ['admin', 'manager']:
                return queryset.order_by('-created_at')
            
            # Utilisateur connecté voit ses notifications
            if device_id:
                queryset = queryset.filter(device__device_id=device_id)
            else:
                queryset = queryset.filter(user=user)
        else:
            # Client non authentifié - filtrer par device_id obligatoirement
            if device_id:
                queryset = queryset.filter(device__device_id=device_id)
            else:
                # Pas de device_id fourni et pas authentifié - pas de notifications
                queryset = queryset.none()
        
        return queryset.order_by('-created_at')
    
    @action(detail=False, methods=['get'])
    def my_notifications(self, request):
        """Récupérer les notifications de l'utilisateur connecté ou du device"""
        device_id = request.query_params.get('device_id')
        
        # Utilisateur authentifié
        if request.user.is_authenticated:
            if request.user.user_type in ['admin', 'manager']:
                # Admin/Manager voient toutes les notifications
                notifications = Notification.objects.all().order_by('-created_at')
            else:
                # Utilisateur normal voit ses notifications
                if device_id:
                    notifications = Notification.objects.filter(
                        device__device_id=device_id
                    ).order_by('-created_at')
                else:
                    notifications = Notification.objects.filter(
                        user=request.user
                    ).order_by('-created_at')
        else:
            # Client non authentifié - doit fournir device_id
            if device_id:
                notifications = Notification.objects.filter(
                    device__device_id=device_id
                ).order_by('-created_at')
            else:
                notifications = Notification.objects.none()
        
        serializer = self.get_serializer(notifications, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def unread_count(self, request):
        """Compter les notifications non lues"""
        device_id = request.query_params.get('device_id')
        
        if device_id:
            # Client sans authentification - filtrer par device_id
            count = Notification.objects.filter(
                device__device_id=device_id,
                is_read=False
            ).count()
        elif request.user.is_authenticated:
            # Utilisateur authentifié
            count = Notification.objects.filter(
                user=request.user,
                is_read=False
            ).count()
        else:
            # Pas de device_id et pas authentifié
            count = 0
        
        return Response({'unread_count': count})
    
    @action(detail=True, methods=['post'])
    def mark_as_read(self, request, pk=None):
        """Marquer une notification comme lue"""
        notification = self.get_object()
        notification.mark_as_read()
        serializer = self.get_serializer(notification)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def mark_all_as_read(self, request):
        """Marquer toutes les notifications comme lues"""
        device_id = request.query_params.get('device_id')
        
        if device_id:
            # Client sans authentification - filtrer par device_id
            notifications = Notification.objects.filter(
                device__device_id=device_id,
                is_read=False
            )
        elif request.user.is_authenticated:
            # Utilisateur authentifié
            notifications = Notification.objects.filter(
                user=request.user,
                is_read=False
            )
        else:
            # Pas de device_id et pas authentifié
            notifications = Notification.objects.none()
        
        count = notifications.update(is_read=True)
        return Response({'marked_as_read': count})
    
    @action(detail=False, methods=['delete'])
    def delete_old_notifications(self, request):
        """Supprimer les notifications lues plus de 30 jours"""
        from django.utils import timezone
        from datetime import timedelta
        
        old_date = timezone.now() - timedelta(days=30)
        count, _ = Notification.objects.filter(
            is_read=True,
            read_at__lt=old_date
        ).delete()
        
        return Response({'deleted': count})


class NotificationTemplateViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet pour les templates de notification (lecture seule)"""
    queryset = NotificationTemplate.objects.all()
    serializer_class = NotificationTemplateSerializer
    permission_classes = [permissions.IsAdminUser]
