from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Board, List, Card
from .serializers import BoardSerializer, ListSerializer, CardSerializer
from .permissions import IsBoardOwner, IsBoardMemberOrOwner


class BoardViewSet(viewsets.ModelViewSet):
    serializer_class = BoardSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Board.objects.filter(owner=user) | Board.objects.filter(members=user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def get_permissions(self):
        if self.action in ['update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsBoardOwner()]
        return [IsAuthenticated()]


class ListViewSet(viewsets.ModelViewSet):
    serializer_class = ListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return List.objects.filter(board__owner=user) | List.objects.filter(board__members=user)


class CardViewSet(viewsets.ModelViewSet):
    serializer_class = CardSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Card.objects.filter(
            list__board__owner=user
        ) | Card.objects.filter(
            list__board__members=user
        )

    @action(detail=True, methods=['patch'])
    def move(self, request, pk=None):
        card = self.get_object()
        list_id = request.data.get('list')
        position = request.data.get('position')
        if list_id:
            card.list_id = list_id
        if position is not None:
            card.position = position
        card.save()
        return Response(CardSerializer(card).data)