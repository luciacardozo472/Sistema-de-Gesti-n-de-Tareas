from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Board, List, Card
from .serializers import BoardSerializer, ListSerializer, CardSerializer
from .permissions import IsBoardOwner, IsBoardMemberOrOwner


class BoardViewSet(viewsets.ModelViewSet):
    serializer_class = BoardSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Board.objects.filter(
            owner=user
        ) | Board.objects.filter(
            members=user
        )

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
        return List.objects.filter(
            board__owner=user
        ) | List.objects.filter(
            board__members=user
        )


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