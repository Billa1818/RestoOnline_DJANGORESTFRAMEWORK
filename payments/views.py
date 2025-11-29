# ===================================
# payments/views.py
# ===================================

from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.utils import timezone
from django.conf import settings
from .models import Payment, PaymentWebhook
from .serializers import (
    PaymentSerializer, PaymentCreateSerializer, PaymentWebhookSerializer
)
import hashlib
import json


class PaymentViewSet(viewsets.ModelViewSet):
    """ViewSet pour les paiements"""
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    
    def get_permissions(self):
        if self.action in ['create', 'verify', 'check_status']:
            return [AllowAny()]
        return [IsAuthenticated()]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return PaymentCreateSerializer
        return PaymentSerializer
    
    def get_queryset(self):
        queryset = Payment.objects.select_related('order')
        
        # Filtres
        order_id = self.request.query_params.get('order_id', None)
        payment_status = self.request.query_params.get('status', None)
        payment_method = self.request.query_params.get('payment_method', None)
        
        if order_id:
            queryset = queryset.filter(order_id=order_id)
        
        if payment_status:
            queryset = queryset.filter(status=payment_status)
        
        if payment_method:
            queryset = queryset.filter(payment_method=payment_method)
        
        return queryset.order_by('-created_at')
    
    def create(self, request, *args, **kwargs):
        """Initialiser un paiement avec PayDunya"""
        from orders.models import Order
        
        order_id = request.data.get('order')
        
        try:
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            return Response(
                {'error': 'Commande non trouvée'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        if hasattr(order, 'payment'):
            return Response(
                {'error': 'Un paiement existe déjà pour cette commande'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Créer le paiement
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            payment = serializer.save()
            
            # Intégration PayDunya
            paydunya_response = self._initialize_paydunya_payment(payment, order)
            
            if paydunya_response.get('success'):
                payment.paydunya_token = paydunya_response.get('token')
                payment.paydunya_invoice_url = paydunya_response.get('invoice_url')
                payment.paydunya_response_code = paydunya_response.get('response_code')
                payment.paydunya_response_text = paydunya_response.get('response_text')
                payment.paydunya_response = paydunya_response
                payment.status = 'processing'
                payment.save()
                
                return Response(
                    PaymentSerializer(payment).data,
                    status=status.HTTP_201_CREATED
                )
            else:
                payment.status = 'failed'
                payment.paydunya_response = paydunya_response
                payment.save()
                
                return Response(
                    {'error': 'Échec de l\'initialisation du paiement', 'details': paydunya_response},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def _initialize_paydunya_payment(self, payment, order):
        """
        Initialiser un paiement avec l'API PayDunya
        NOTE: Cette fonction est un exemple. Vous devez adapter selon la documentation PayDunya.
        """
        try:
            # Import de la bibliothèque PayDunya (à installer via pip)
            # pip install paydunya
            from paydunya import Invoice, Setup
            
            # Configuration PayDunya
            setup = Setup({
                'master_key': settings.PAYDUNYA_MASTER_KEY,
                'private_key': settings.PAYDUNYA_PRIVATE_KEY,
                'public_key': settings.PAYDUNYA_PUBLIC_KEY,
                'token': settings.PAYDUNYA_TOKEN,
                'mode': settings.PAYDUNYA_MODE  # 'test' ou 'live'
            })
            
            # Créer la facture
            invoice = Invoice(setup)
            invoice.add_item(
                name=f"Commande {order.order_number}",
                quantity=1,
                unit_price=float(payment.amount),
                total_price=float(payment.amount),
                description=f"Paiement pour la commande {order.order_number}"
            )
            
            # Informations client
            invoice.set_custom_data([
                ('order_id', order.id),
                ('order_number', order.order_number),
                ('customer_name', order.customer_name),
                ('customer_phone', order.customer_phone),
            ])
            
            # URLs de callback
            invoice.set_callback_url(f"{settings.SITE_URL}/api/payments/webhook/")
            invoice.set_return_url(f"{settings.SITE_URL}/orders/{order.order_number}/payment/success/")
            invoice.set_cancel_url(f"{settings.SITE_URL}/orders/{order.order_number}/payment/cancel/")
            
            # Créer la facture
            response = invoice.create()
            
            if response['response_code'] == '00':
                return {
                    'success': True,
                    'token': response['token'],
                    'invoice_url': response['response_text'],
                    'response_code': response['response_code'],
                    'response_text': response['response_text']
                }
            else:
                return {
                    'success': False,
                    'error': response.get('response_text', 'Erreur inconnue'),
                    'response_code': response.get('response_code')
                }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    @action(detail=True, methods=['get'], permission_classes=[AllowAny])
    def check_status(self, request, pk=None):
        """Vérifier le statut d'un paiement auprès de PayDunya"""
        payment = self.get_object()
        
        if not payment.paydunya_token:
            return Response(
                {'error': 'Token PayDunya manquant'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        status_response = self._check_paydunya_status(payment)
        
        # Mettre à jour le statut du paiement si nécessaire
        if status_response.get('status') == 'completed':
            payment.status = 'completed'
            payment.transaction_id = status_response.get('transaction_id')
            payment.completed_at = timezone.now()
            payment.save()
            
            # Mettre à jour le statut de la commande si nécessaire
            if payment.order.status == 'pending':
                payment.order.status = 'accepted'
                payment.order.save()
        
        serializer = PaymentSerializer(payment)
        return Response(serializer.data)
    
    def _check_paydunya_status(self, payment):
        """
        Vérifier le statut d'un paiement auprès de PayDunya
        NOTE: Adapter selon la documentation PayDunya
        """
        try:
            from paydunya import Invoice, Setup
            
            setup = Setup({
                'master_key': settings.PAYDUNYA_MASTER_KEY,
                'private_key': settings.PAYDUNYA_PRIVATE_KEY,
                'public_key': settings.PAYDUNYA_PUBLIC_KEY,
                'token': settings.PAYDUNYA_TOKEN,
                'mode': settings.PAYDUNYA_MODE
            })
            
            invoice = Invoice(setup)
            status = invoice.confirm(payment.paydunya_token)
            
            return {
                'status': 'completed' if status['status'] == 'completed' else 'pending',
                'transaction_id': status.get('transaction_id'),
                'response': status
            }
        
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Statistiques des paiements"""
        from django.db.models import Sum, Count
        
        queryset = self.get_queryset()
        
        total_payments = queryset.count()
        completed_payments = queryset.filter(status='completed')
        
        stats = {
            'total_payments': total_payments,
            'completed_count': completed_payments.count(),
            'pending_count': queryset.filter(status='pending').count(),
            'failed_count': queryset.filter(status='failed').count(),
            'total_amount': float(completed_payments.aggregate(
                Sum('amount')
            )['amount__sum'] or 0),
            'by_method': {}
        }
        
        # Statistiques par méthode de paiement
        for method, _ in Payment.PAYMENT_METHOD_CHOICES:
            method_payments = completed_payments.filter(payment_method=method)
            stats['by_method'][method] = {
                'count': method_payments.count(),
                'total_amount': float(method_payments.aggregate(
                    Sum('amount')
                )['amount__sum'] or 0)
            }
        
        return Response(stats)


@api_view(['POST'])
@permission_classes([AllowAny])
def paydunya_webhook(request):
    """
    Endpoint webhook pour recevoir les notifications PayDunya
    NOTE: Adapter selon la documentation PayDunya
    """
    try:
        # Récupérer les données du webhook
        webhook_data = request.data
        
        # Créer un enregistrement du webhook
        webhook = PaymentWebhook.objects.create(
            webhook_data=webhook_data,
            status=webhook_data.get('status', 'unknown')
        )
        
        # Extraire les informations importantes
        token = webhook_data.get('token')
        status_value = webhook_data.get('status')
        transaction_id = webhook_data.get('transaction_id')
        
        if not token:
            webhook.processing_error = 'Token manquant'
            webhook.save()
            return Response({'error': 'Token manquant'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Trouver le paiement correspondant
        try:
            payment = Payment.objects.get(paydunya_token=token)
            webhook.payment = payment
        except Payment.DoesNotExist:
            webhook.processing_error = 'Paiement non trouvé'
            webhook.save()
            return Response({'error': 'Paiement non trouvé'}, status=status.HTTP_404_NOT_FOUND)
        
        # Mettre à jour le statut du paiement
        if status_value == 'completed':
            payment.status = 'completed'
            payment.transaction_id = transaction_id
            payment.completed_at = timezone.now()
            payment.save()
            
            # Mettre à jour la commande
            if payment.order.status == 'pending':
                payment.order.status = 'accepted'
                payment.order.save()
        
        elif status_value in ['failed', 'cancelled']:
            payment.status = status_value
            payment.save()
        
        # Marquer le webhook comme traité
        webhook.processed = True
        webhook.processed_at = timezone.now()
        webhook.save()
        
        return Response({'success': True}, status=status.HTTP_200_OK)
    
    except Exception as e:
        if 'webhook' in locals():
            webhook.processing_error = str(e)
            webhook.save()
        
        return Response(
            {'error': 'Erreur de traitement', 'details': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


class PaymentWebhookViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet pour les webhooks (lecture seule, admin)"""
    queryset = PaymentWebhook.objects.all()
    serializer_class = PaymentWebhookSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = PaymentWebhook.objects.select_related('payment')
        
        # Filtres
        processed = self.request.query_params.get('processed', None)
        payment_id = self.request.query_params.get('payment_id', None)
        
        if processed is not None:
            queryset = queryset.filter(processed=processed.lower() == 'true')
        
        if payment_id:
            queryset = queryset.filter(payment_id=payment_id)
        
        return queryset.order_by('-received_at')
    
    @action(detail=False, methods=['get'])
    def unprocessed(self, request):
        """Webhooks non traités"""
        unprocessed = self.get_queryset().filter(processed=False)
        serializer = PaymentWebhookSerializer(unprocessed, many=True)
        return Response(serializer.data)

