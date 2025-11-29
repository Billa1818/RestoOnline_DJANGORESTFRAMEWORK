from django.test import TestCase
from django.contrib.auth import get_user_model
from accounts.models import ClientDevice
from .models import Notification
from .utils import (
    notify_device,
    notify_user,
    notify_all_admin,
    notify_device_on_order_created,
)

User = get_user_model()


class NotificationModelTest(TestCase):
    """Tests pour le modèle Notification"""
    
    def setUp(self):
        self.device = ClientDevice.objects.create(
            device_id='test-device-123',
            customer_name='Test Customer'
        )
        
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            user_type='admin'
        )
    
    def test_create_device_notification(self):
        """Test création notification pour appareil"""
        notification = Notification.objects.create(
            device=self.device,
            type='order_created',
            title='Test Notification',
            message='Test message'
        )
        
        self.assertEqual(notification.type, 'order_created')
        self.assertEqual(notification.device, self.device)
        self.assertFalse(notification.is_read)
    
    def test_create_user_notification(self):
        """Test création notification pour utilisateur"""
        notification = Notification.objects.create(
            user=self.user,
            type='delivery_assigned',
            title='Delivery',
            message='New delivery assigned'
        )
        
        self.assertEqual(notification.user, self.user)
        self.assertTrue(Notification.objects.filter(user=self.user).exists())
    
    def test_mark_as_read(self):
        """Test marquer comme lue"""
        notification = Notification.objects.create(
            device=self.device,
            type='order_created',
            title='Test',
            message='Test'
        )
        
        self.assertFalse(notification.is_read)
        notification.mark_as_read()
        
        self.assertTrue(notification.is_read)
        self.assertIsNotNone(notification.read_at)


class NotificationUtilsTest(TestCase):
    """Tests pour les fonctions utils"""
    
    def setUp(self):
        self.device = ClientDevice.objects.create(
            device_id='test-device-456'
        )
        
        self.user = User.objects.create_user(
            username='testdelivery',
            email='delivery@example.com',
            password='testpass123',
            user_type='delivery'
        )
        
        self.admin = User.objects.create_user(
            username='testadmin',
            email='admin@example.com',
            password='testpass123',
            user_type='admin'
        )
    
    def test_notify_device(self):
        """Test notify_device utility"""
        notification = notify_device(
            device=self.device,
            type_notification='test_notification',
            title='Test',
            message='Test message',
            data={'test': 'data'}
        )
        
        self.assertIsNotNone(notification)
        self.assertEqual(notification.device, self.device)
        self.assertEqual(notification.data['test'], 'data')
    
    def test_notify_user(self):
        """Test notify_user utility"""
        notification = notify_user(
            user=self.user,
            type_notification='delivery_assigned',
            title='Delivery',
            message='You have a delivery',
        )
        
        self.assertIsNotNone(notification)
        self.assertEqual(notification.user, self.user)
    
    def test_notify_all_admin(self):
        """Test notify_all_admin utility"""
        # Créer plusieurs admins
        User.objects.create_user(
            username='admin2',
            email='admin2@example.com',
            password='pass',
            user_type='admin'
        )
        
        notifications = notify_all_admin(
            type_notification='order_created',
            title='New Order',
            message='Order received'
        )
        
        self.assertGreater(len(notifications), 0)
        
        # Vérifier que les notifs ont été créées
        admin_notifications = Notification.objects.filter(
            user__user_type__in=['admin', 'manager']
        )
        self.assertGreater(admin_notifications.count(), 0)


class NotificationQueryTest(TestCase):
    """Tests pour les requêtes notifications"""
    
    def setUp(self):
        self.device1 = ClientDevice.objects.create(device_id='device1')
        self.device2 = ClientDevice.objects.create(device_id='device2')
        
        # Créer notifications
        Notification.objects.create(
            device=self.device1,
            type='order_created',
            title='Order 1',
            message='First order'
        )
        
        Notification.objects.create(
            device=self.device1,
            type='order_accepted',
            title='Order Accepted',
            message='Your order accepted',
            is_read=True
        )
        
        Notification.objects.create(
            device=self.device2,
            type='order_created',
            title='Order 2',
            message='Second order'
        )
    
    def test_filter_by_device(self):
        """Test filtrer par appareil"""
        notifs = Notification.objects.filter(device=self.device1)
        self.assertEqual(notifs.count(), 2)
        
        notifs2 = Notification.objects.filter(device=self.device2)
        self.assertEqual(notifs2.count(), 1)
    
    def test_filter_unread(self):
        """Test filtrer non lues"""
        unread = Notification.objects.filter(is_read=False)
        self.assertEqual(unread.count(), 2)
        
        read = Notification.objects.filter(is_read=True)
        self.assertEqual(read.count(), 1)
    
    def test_order_by_date(self):
        """Test tri par date"""
        notifs = Notification.objects.all().order_by('-created_at')
        self.assertEqual(notifs.count(), 3)
        
        # La plus récente doit être en premier
        self.assertEqual(notifs.first().device, self.device2)
