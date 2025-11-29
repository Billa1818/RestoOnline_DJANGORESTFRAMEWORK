"""Utilitaires pour créer les notifications partout dans l'app"""

from django.utils import timezone
from .models import Notification
from accounts.models import User, ClientDevice


def send_notification(
    type_notification,
    title,
    message,
    device=None,
    user=None,
    order_id=None,
    delivery_id=None,
    related_user_id=None,
    data=None
):
    """
    Créer et envoyer une notification
    
    Args:
        type_notification: Type de notification (ex: 'order_created')
        title: Titre
        message: Message
        device: Instance ClientDevice (optionnel)
        user: Instance User (optionnel)
        order_id: ID de la commande (optionnel)
        delivery_id: ID de la livraison (optionnel)
        related_user_id: ID utilisateur lié (optionnel)
        data: Dict données supplémentaires (optionnel)
    """
    if not device and not user:
        return None
    
    notification = Notification.objects.create(
        type=type_notification,
        title=title,
        message=message,
        device=device,
        user=user,
        order_id=order_id,
        delivery_id=delivery_id,
        related_user_id=related_user_id,
        data=data or {}
    )
    
    # Optionnel: Envoyer via Celery (pour FCM, email, etc.)
    # send_notification_task.delay(notification.id)
    
    return notification


def notify_device(
    device,
    type_notification,
    title,
    message,
    order_id=None,
    delivery_id=None,
    data=None
):
    """Notifier un appareil spécifique"""
    return send_notification(
        type_notification=type_notification,
        title=title,
        message=message,
        device=device,
        order_id=order_id,
        delivery_id=delivery_id,
        data=data
    )


def notify_user(
    user,
    type_notification,
    title,
    message,
    order_id=None,
    delivery_id=None,
    related_user_id=None,
    data=None
):
    """Notifier un utilisateur spécifique"""
    return send_notification(
        type_notification=type_notification,
        title=title,
        message=message,
        user=user,
        order_id=order_id,
        delivery_id=delivery_id,
        related_user_id=related_user_id,
        data=data
    )


def notify_all_admin(
    type_notification,
    title,
    message,
    order_id=None,
    delivery_id=None,
    data=None
):
    """Notifier tous les administrateurs/managers"""
    admins = User.objects.filter(user_type__in=['admin', 'manager'])
    notifications = []
    
    for admin in admins:
        notification = send_notification(
            type_notification=type_notification,
            title=title,
            message=message,
            user=admin,
            order_id=order_id,
            delivery_id=delivery_id,
            data=data
        )
        notifications.append(notification)
    
    return notifications


def notify_device_on_order_created(device, order_number, total):
    """Notification: Commande créée"""
    return notify_device(
        device=device,
        type_notification='order_created',
        title='Commande créée',
        message=f'Votre commande #{order_number} a été créée. Montant: {total} FCFA',
        order_id=None,  # À définir après création
        data={'order_number': order_number}
    )


def notify_admin_on_order_created(order_number, customer_name, total):
    """Notification: Admin reçoit une nouvelle commande"""
    return notify_all_admin(
        type_notification='order_created',
        title='Nouvelle commande',
        message=f'Nouvelle commande #{order_number} de {customer_name}. Montant: {total} FCFA',
        data={'order_number': order_number, 'customer': customer_name}
    )


def notify_device_on_order_accepted(device, order_number):
    """Notification: Commande acceptée"""
    return notify_device(
        device=device,
        type_notification='order_accepted',
        title='Commande acceptée',
        message=f'Votre commande #{order_number} a été acceptée et est en préparation',
        data={'order_number': order_number}
    )


def notify_device_on_order_refused(device, order_number, reason=''):
    """Notification: Commande refusée"""
    message = f'Votre commande #{order_number} a été refusée'
    if reason:
        message += f'. Raison: {reason}'
    
    return notify_device(
        device=device,
        type_notification='order_refused',
        title='Commande refusée',
        message=message,
        data={'order_number': order_number, 'reason': reason}
    )


def notify_device_on_order_ready(device, order_number):
    """Notification: Commande prête"""
    return notify_device(
        device=device,
        type_notification='order_ready',
        title='Commande prête',
        message=f'Votre commande #{order_number} est prête! Le livreur arrive bientôt',
        data={'order_number': order_number}
    )


def notify_device_on_order_in_delivery(device, order_number, delivery_person_name):
    """Notification: Commande en livraison"""
    return notify_device(
        device=device,
        type_notification='order_in_delivery',
        title='Commande en livraison',
        message=f'Votre commande #{order_number} est en cours de livraison par {delivery_person_name}',
        data={'order_number': order_number, 'delivery_person': delivery_person_name}
    )


def notify_device_on_order_delivered(device, order_number):
    """Notification: Commande livrée"""
    return notify_device(
        device=device,
        type_notification='order_delivered',
        title='Commande livrée',
        message=f'Votre commande #{order_number} a été livrée. Merci!',
        data={'order_number': order_number}
    )


def notify_delivery_person_on_assignment(delivery_person, order_number, customer_phone=''):
    """Notification: Livreur assigné"""
    return notify_user(
        user=delivery_person,
        type_notification='delivery_assigned',
        title='Nouvelle livraison',
        message=f'Vous avez une nouvelle livraison pour la commande #{order_number}',
        data={'order_number': order_number, 'customer_phone': customer_phone}
    )


def notify_admin_on_delivery_completed(order_number, delivery_person_name, delivery_time=''):
    """Notification: Admin - Livraison complétée"""
    message = f'Livraison complétée pour la commande #{order_number} par {delivery_person_name}'
    if delivery_time:
        message += f' en {delivery_time}'
    
    return notify_all_admin(
        type_notification='delivery_completed',
        title='Livraison complétée',
        message=message,
        data={'order_number': order_number, 'delivery_person': delivery_person_name}
    )


def notify_device_on_new_user_account(device, username):
    """Notification: Compte créé"""
    return notify_device(
        device=device,
        type_notification='account_created',
        title='Compte créé',
        message=f'Votre compte {username} a été créé avec succès. Bienvenue!',
        data={'username': username}
    )


def notify_payment_received(device, order_number, amount):
    """Notification: Paiement reçu"""
    return notify_device(
        device=device,
        type_notification='payment_received',
        title='Paiement reçu',
        message=f'Paiement de {amount} FCFA pour la commande #{order_number} reçu',
        data={'order_number': order_number, 'amount': float(amount)}
    )


def notify_rating_received(user, order_number, rating):
    """Notification: Note reçue (pour livreur/client)"""
    return notify_user(
        user=user,
        type_notification='rating_received',
        title='Vous avez reçu une note',
        message=f'Commande #{order_number}: {rating}/5 étoiles',
        data={'order_number': order_number, 'rating': rating}
    )
