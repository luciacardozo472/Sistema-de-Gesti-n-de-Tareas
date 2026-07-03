from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from .models import UserProfile


class UserProfileSignalTests(APITestCase):
    """Verifica que el perfil se crea automáticamente al crear un User."""

    def test_profile_created_on_user_creation(self):
        user = User.objects.create_user(username='juan', password='clave12345')
        self.assertTrue(UserProfile.objects.filter(user=user).exists())
        self.assertEqual(user.profile.level, UserProfile.LEVEL_USER)

    def test_is_admin_property(self):
        user = User.objects.create_user(username='admin1', password='clave12345')
        user.profile.level = UserProfile.LEVEL_ADMIN
        user.profile.save()
        self.assertTrue(user.profile.is_admin)


class RegisterViewTests(APITestCase):
    """El endpoint de registro solo debe estar disponible para administradores."""

    def setUp(self):
        self.url = reverse('register')
        self.admin = User.objects.create_user(username='admin', password='clave12345')
        self.admin.profile.level = UserProfile.LEVEL_ADMIN
        self.admin.profile.save()
        self.regular_user = User.objects.create_user(username='pepe', password='clave12345')

    def test_admin_can_register_new_user(self):
        self.client.force_authenticate(user=self.admin)
        payload = {'username': 'nuevo', 'email': 'nuevo@test.com', 'password': 'clave12345'}
        response = self.client.post(self.url, payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(username='nuevo').exists())

    def test_regular_user_cannot_register(self):
        self.client.force_authenticate(user=self.regular_user)
        payload = {'username': 'otro', 'email': 'otro@test.com', 'password': 'clave12345'}
        response = self.client.post(self.url, payload)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthenticated_cannot_register(self):
        payload = {'username': 'otro', 'email': 'otro@test.com', 'password': 'clave12345'}
        response = self.client.post(self.url, payload)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_registered_user_gets_requested_level(self):
        self.client.force_authenticate(user=self.admin)
        payload = {
            'username': 'admin2', 'email': 'a2@test.com',
            'password': 'clave12345', 'level': UserProfile.LEVEL_ADMIN
        }
        self.client.post(self.url, payload)
        created = User.objects.get(username='admin2')
        self.assertEqual(created.profile.level, UserProfile.LEVEL_ADMIN)


class CurrentUserViewTests(APITestCase):

    def setUp(self):
        self.url = reverse('user-me')
        self.user = User.objects.create_user(username='maria', password='clave12345')

    def test_authenticated_user_gets_own_data(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'maria')

    def test_unauthenticated_request_rejected(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class UserListViewTests(APITestCase):

    def setUp(self):
        self.url = reverse('user-list')
        self.user = User.objects.create_user(username='ana', password='clave12345')
        User.objects.create_user(username='luis', password='clave12345')

    def test_authenticated_user_can_list_users(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
