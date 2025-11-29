from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth import authenticate
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User, ClientDevice
from .serializers import (
    UserSerializer, UserListSerializer, DeliveryPersonSerializer,
    ClientDeviceSerializer, ClientDeviceCreateSerializer,
    PasswordResetRequestSerializer, PasswordResetConfirmSerializer
)
from notifications.utils import (
    notify_device_on_new_user_account,
    notify_all_admin
)


class UserViewSet(viewsets.ModelViewSet):
    """ViewSet pour la gestion des utilisateurs"""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'list':
            return UserListSerializer
        return UserSerializer
    
    def get_queryset(self):
        queryset = User.objects.all()
        user_type = self.request.query_params.get('user_type', None)
        if user_type:
            queryset = queryset.filter(user_type=user_type)
        return queryset
    
    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def login(self, request):
        """Connexion utilisateur"""
        username = request.data.get('username')
        password = request.data.get('password')
        
        user = authenticate(username=username, password=password)
        if user:
            # Vérifier que c'est un utilisateur du système (pas un client)
            if user.user_type not in ['admin', 'manager', 'delivery']:
                return Response(
                    {'error': 'Accès non autorisé'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user': UserSerializer(user).data
            })
        return Response(
            {'error': 'Identifiants invalides'},
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        """Informations de l'utilisateur connecté"""
        serializer = UserSerializer(request.user)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def toggle_availability(self, request, pk=None):
        """Basculer la disponibilité d'un livreur"""
        user = self.get_object()
        if user.user_type != 'delivery':
            return Response(
                {'error': 'Cette action est réservée aux livreurs'},
                status=status.HTTP_400_BAD_REQUEST
            )
        user.is_available = not user.is_available
        user.save()
        return Response({'is_available': user.is_available})
    
    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def password_reset_request(self, request):
        """Demande de réinitialisation de mot de passe"""
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        email = serializer.validated_data['email']
        
        try:
            user = User.objects.get(
                email=email,
                user_type__in=['admin', 'manager', 'delivery']
            )
        except User.DoesNotExist:
            # Pour des raisons de sécurité, on renvoie toujours un message de succès
            return Response({
                'message': 'Si cette adresse email existe dans notre système, vous recevrez un lien de réinitialisation.'
            })
        
        # Générer le token de réinitialisation
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        
        # Créer le lien de réinitialisation
        reset_url = f"{settings.FRONTEND_URL}/reset-password/{uid}/{token}/"
        
        # Préparer le contexte pour l'email
        context = {
            'user': user,
            'reset_url': reset_url,
            'site_name': getattr(settings, 'SITE_NAME', 'Delivery System'),
        }
        
        # Envoyer l'email
        subject = 'Réinitialisation de votre mot de passe'
        html_message = render_to_string('accounts/password_reset_email.html', context)
        plain_message = render_to_string('accounts/password_reset_email.txt', context)
        
        try:
            send_mail(
                subject=subject,
                message=plain_message,
                html_message=html_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=False,
            )
        except Exception as e:
            return Response(
                {'error': 'Erreur lors de l\'envoi de l\'email. Veuillez réessayer.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        return Response({
            'message': 'Si cette adresse email existe dans notre système, vous recevrez un lien de réinitialisation.'
        })
    
    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def password_reset_confirm(self, request):
        """Confirmer la réinitialisation du mot de passe"""
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        uid = serializer.validated_data['uid']
        token = serializer.validated_data['token']
        new_password = serializer.validated_data['new_password']
        
        try:
            user_id = force_str(urlsafe_base64_decode(uid))
            user = User.objects.get(
                pk=user_id,
                user_type__in=['admin', 'manager', 'delivery']
            )
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return Response(
                {'error': 'Lien de réinitialisation invalide'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Vérifier le token
        if not default_token_generator.check_token(user, token):
            return Response(
                {'error': 'Lien de réinitialisation expiré ou invalide'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Mettre à jour le mot de passe
        user.set_password(new_password)
        user.save()
        
        # Envoyer un email de confirmation
        subject = 'Votre mot de passe a été modifié'
        message = f"""
Bonjour {user.get_full_name() or user.username},

Votre mot de passe a été modifié avec succès.

Si vous n'êtes pas à l'origine de cette modification, veuillez contacter immédiatement l'administrateur.

Cordialement,
L'équipe {getattr(settings, 'SITE_NAME', 'Delivery System')}
        """
        
        try:
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=True,
            )
        except:
            pass  # On ne bloque pas si l'email de confirmation échoue
        
        return Response({
            'message': 'Votre mot de passe a été réinitialisé avec succès.'
        })
    
    @action(detail=False, methods=['post'])
    def change_password(self, request):
        """Changer le mot de passe de l'utilisateur connecté"""
        user = request.user
        old_password = request.data.get('old_password')
        new_password = request.data.get('new_password')
        confirm_password = request.data.get('confirm_password')
        
        if not all([old_password, new_password, confirm_password]):
            return Response(
                {'error': 'Tous les champs sont requis'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if new_password != confirm_password:
            return Response(
                {'error': 'Les nouveaux mots de passe ne correspondent pas'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not user.check_password(old_password):
            return Response(
                {'error': 'Mot de passe actuel incorrect'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user.set_password(new_password)
        user.save()
        
        return Response({
            'message': 'Mot de passe modifié avec succès'
        })


class DeliveryPersonViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet pour les livreurs (lecture seule)"""
    queryset = User.objects.filter(user_type='delivery')
    serializer_class = DeliveryPersonSerializer
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def available(self, request):
        """Liste des livreurs disponibles"""
        available_drivers = self.queryset.filter(is_available=True)
        serializer = self.get_serializer(available_drivers, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def statistics(self, request, pk=None):
        """Statistiques détaillées d'un livreur"""
        driver = self.get_object()
        from delivery.models import DeliveryAssignment
        from ratings.models import DeliveryRating
        
        assignments = DeliveryAssignment.objects.filter(delivery_person=driver)
        ratings = DeliveryRating.objects.filter(delivery_person=driver)
        
        return Response({
            'total_deliveries': driver.total_deliveries,
            'average_rating': float(driver.average_rating),
            'completed_deliveries': assignments.filter(status='delivered').count(),
            'refused_deliveries': assignments.filter(status='refused').count(),
            'total_ratings': ratings.count(),
            'ratings_breakdown': {
                '5_stars': ratings.filter(rating=5).count(),
                '4_stars': ratings.filter(rating=4).count(),
                '3_stars': ratings.filter(rating=3).count(),
                '2_stars': ratings.filter(rating=2).count(),
                '1_star': ratings.filter(rating=1).count(),
            }
        })


class ClientDeviceViewSet(viewsets.ModelViewSet):
    """ViewSet pour la gestion des appareils clients"""
    queryset = ClientDevice.objects.all()
    serializer_class = ClientDeviceSerializer
    permission_classes = [AllowAny]
    lookup_field = 'device_id'
    
    def get_serializer_class(self):
        if self.action == 'create':
            return ClientDeviceCreateSerializer
        return ClientDeviceSerializer
    
    @action(detail=False, methods=['post'])
    def register(self, request):
        """Enregistrer ou récupérer un appareil client"""
        device_id = request.data.get('device_id')
        
        if not device_id:
            return Response(
                {'error': 'device_id requis'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        device, created = ClientDevice.objects.get_or_create(
            device_id=device_id,
            defaults={
                'device_info': request.data.get('device_info', {}),
                'device_name': request.data.get('device_name', ''),
                'fcm_token': request.data.get('fcm_token', ''),
            }
        )
        
        if not created:
            # Mettre à jour les informations si l'appareil existe
            device.device_info = request.data.get('device_info', device.device_info)
            device.fcm_token = request.data.get('fcm_token', device.fcm_token)
            device.save()
        else:
            # Créer une notification pour le nouvel appareil
            customer_name = request.data.get('customer_name', 'Utilisateur')
            device_name = request.data.get('device_name', '')
            notify_device_on_new_user_account(
                device=device,
                username=customer_name
            )
            # Notifier les admins
            notify_all_admin(
                type_notification='account_created',
                title='Nouvel appareil enregistré',
                message=f'Nouvel appareil: {device_name or device_id}',
                data={'device_id': device_id, 'customer_name': customer_name}
            )
        
        serializer = ClientDeviceSerializer(device)
        return Response({
            'device': serializer.data,
            'is_new': created
        }, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)
    
    @action(detail=True, methods=['patch'], url_path='update-info')
    def update_customer_info(self, request, device_id=None):
        """Mettre à jour les informations client de l'appareil"""
        device = self.get_object()
        device.customer_name = request.data.get('customer_name', device.customer_name)
        device.customer_phone = request.data.get('customer_phone', device.customer_phone)
        device.customer_email = request.data.get('customer_email', device.customer_email)
        device.save()
        
        serializer = ClientDeviceSerializer(device)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def orders(self, request, device_id=None):
        """Historique des commandes d'un appareil"""
        device = self.get_object()
        from orders.serializers import OrderListSerializer
        orders = device.orders.all()
        serializer = OrderListSerializer(orders, many=True)
        return Response(serializer.data)