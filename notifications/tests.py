from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from .models import Notification


class NotificationListTests(APITestCase):
    """Un usuario solo debe ver sus propias notificaciones."""

    def setUp(self):
        self.user = User.objects.create_user(username='ana', password='clave12345')
        self.other = User.objects.create_user(username='luis', password='clave12345')
        Notification.objects.create(recipient=self.user, message='Para ana')
        Notification.objects.create(recipient=self.other, message='Para luis')
        self.client.force_authenticate(user=self.user)

    def test_user_only_sees_own_notifications(self):
        response = self.client.get(reverse('notification-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['message'], 'Para ana')

    def test_unauthenticated_cannot_list_notifications(self):
        self.client.force_authenticate(user=None)
        response = self.client.get(reverse('notification-list'))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class MarkAsReadTests(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='ana', password='clave12345')
        self.notification = Notification.objects.create(recipient=self.user, message='Hola')
        self.client.force_authenticate(user=self.user)

    def test_mark_single_notification_as_read(self):
        url = reverse('notification-mark-as-read', args=[self.notification.id])
        response = self.client.patch(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.notification.refresh_from_db()
        self.assertTrue(self.notification.is_read)

    def test_mark_all_as_read(self):
        Notification.objects.create(recipient=self.user, message='Otra')
        url = reverse('notification-mark-all-as-read')
        response = self.client.patch(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        unread_count = Notification.objects.filter(recipient=self.user, is_read=False).count()
        self.assertEqual(unread_count, 0)

    def test_cannot_mark_others_notification_as_read(self):
        other = User.objects.create_user(username='luis', password='clave12345')
        other_notification = Notification.objects.create(recipient=other, message='No es tuya')
        url = reverse('notification-mark-as-read', args=[other_notification.id])
        response = self.client.patch(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class SendNotificationTests(APITestCase):
    """Solo un usuario con nivel admin puede enviar notificaciones a otros."""

    def setUp(self):
        self.admin = User.objects.create_user(username='admin', password='clave12345')
        self.admin.profile.level = 0
        self.admin.profile.save()
        self.regular = User.objects.create_user(username='pepe', password='clave12345')
        self.url = reverse('notification-send')

    def test_admin_can_send_notification(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.post(self.url, {
            'recipient_id': self.regular.id,
            'message': 'Reunión a las 10',
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            Notification.objects.filter(recipient=self.regular).exists()
        )

    def test_regular_user_cannot_send_notification(self):
        self.client.force_authenticate(user=self.regular)
        response = self.client.post(self.url, {
            'recipient_id': self.admin.id,
            'message': 'No debería poder',
        })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_send_requires_message_and_recipient(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.post(self.url, {'recipient_id': self.regular.id})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_send_to_nonexistent_user_returns_404(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.post(self.url, {
            'recipient_id': 9999,
            'message': 'Hola',
        })
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
