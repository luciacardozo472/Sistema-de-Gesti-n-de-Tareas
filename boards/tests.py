from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from .models import Board, List, Card


class BoardCreationTests(APITestCase):
    """Al crear un board se deben generar automáticamente las 5 listas por defecto."""

    def setUp(self):
        self.user = User.objects.create_user(username='owner', password='clave12345')
        self.client.force_authenticate(user=self.user)
        self.url = reverse('board-list')

    def test_create_board_generates_default_lists(self):
        response = self.client.post(self.url, {'title': 'Mi proyecto'})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        board = Board.objects.get(id=response.data['id'])
        self.assertEqual(board.lists.count(), 5)
        titles = list(board.lists.order_by('position').values_list('title', flat=True))
        self.assertEqual(
            titles,
            ['Por Hacer', 'En Progreso', 'En Revisión', 'Bloqueado', 'Hecho']
        )

    def test_created_board_owner_is_request_user(self):
        response = self.client.post(self.url, {'title': 'Otro proyecto'})
        board = Board.objects.get(id=response.data['id'])
        self.assertEqual(board.owner, self.user)


class BoardPermissionTests(APITestCase):
    """Un usuario solo debe ver/editar boards de los que es owner o member."""

    def setUp(self):
        self.owner = User.objects.create_user(username='owner', password='clave12345')
        self.member = User.objects.create_user(username='member', password='clave12345')
        self.outsider = User.objects.create_user(username='outsider', password='clave12345')
        self.board = Board.objects.create(title='Board privado', owner=self.owner)
        self.board.members.add(self.member)

    def test_owner_sees_own_board(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.get(reverse('board-detail', args=[self.board.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_member_sees_board(self):
        self.client.force_authenticate(user=self.member)
        response = self.client.get(reverse('board-detail', args=[self.board.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_outsider_cannot_see_board(self):
        self.client.force_authenticate(user=self.outsider)
        response = self.client.get(reverse('board-detail', args=[self.board.id]))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_only_owner_can_delete_board(self):
        self.client.force_authenticate(user=self.member)
        response = self.client.delete(reverse('board-detail', args=[self.board.id]))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_owner_can_delete_board(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.delete(reverse('board-detail', args=[self.board.id]))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_admin_sees_all_boards(self):
        self.outsider.profile.level = 0
        self.outsider.profile.save()
        self.client.force_authenticate(user=self.outsider)
        response = self.client.get(reverse('board-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        ids = [b['id'] for b in response.data]
        self.assertIn(self.board.id, ids)


class CardMoveTests(APITestCase):
    """El endpoint /cards/{id}/move/ debe actualizar lista y posición."""

    def setUp(self):
        self.owner = User.objects.create_user(username='owner', password='clave12345')
        self.board = Board.objects.create(title='Board', owner=self.owner)
        self.list_todo = List.objects.create(board=self.board, title='Por Hacer', position=1)
        self.list_progress = List.objects.create(board=self.board, title='En Progreso', position=2)
        self.card = Card.objects.create(title='Tarea 1', list=self.list_todo, position=1)
        self.client.force_authenticate(user=self.owner)

    def test_move_card_to_another_list(self):
        url = reverse('card-move', args=[self.card.id])
        response = self.client.patch(url, {'list': self.list_progress.id, 'position': 500})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.card.refresh_from_db()
        self.assertEqual(self.card.list_id, self.list_progress.id)
        self.assertEqual(self.card.position, 500)

    def test_move_card_requires_authentication(self):
        self.client.force_authenticate(user=None)
        url = reverse('card-move', args=[self.card.id])
        response = self.client.patch(url, {'list': self.list_progress.id})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_outsider_cannot_move_card(self):
        outsider = User.objects.create_user(username='outsider', password='clave12345')
        self.client.force_authenticate(user=outsider)
        url = reverse('card-move', args=[self.card.id])
        response = self.client.patch(url, {'list': self.list_progress.id})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class CardAssignmentTests(APITestCase):

    def setUp(self):
        self.owner = User.objects.create_user(username='owner', password='clave12345')
        self.assignee = User.objects.create_user(username='assignee', password='clave12345')
        self.board = Board.objects.create(title='Board', owner=self.owner)
        self.list_todo = List.objects.create(board=self.board, title='Por Hacer', position=1)
        self.client.force_authenticate(user=self.owner)

    def test_create_card_with_assignment(self):
        url = reverse('card-list')
        response = self.client.post(url, {
            'title': 'Nueva tarea',
            'list': self.list_todo.id,
            'assigned_to': self.assignee.id,
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['assigned_to_username'], 'assignee')
