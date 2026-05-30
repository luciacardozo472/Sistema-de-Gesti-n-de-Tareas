from rest_framework import serializers
from .models import Board, List, Card


class CardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Card
        fields = [
            'id',
            'title',
            'description',
            'list',
            'position',
            'assigned_to',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class ListSerializer(serializers.ModelSerializer):
    cards = CardSerializer(many=True, read_only=True)

    class Meta:
        model = List
        fields = ['id', 'title', 'board', 'position', 'cards']
        read_only_fields = ['id']


class BoardSerializer(serializers.ModelSerializer):
    lists = ListSerializer(many=True, read_only=True)
    owner = serializers.ReadOnlyField(source='owner.username')

    class Meta:
        model = Board
        fields = ['id', 'title', 'owner', 'members', 'lists', 'created_at']
        read_only_fields = ['id', 'owner', 'created_at']