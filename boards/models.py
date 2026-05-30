from django.db import models
from django.contrib.auth.models import User


class Board(models.Model):
    title = models.CharField(max_length=255)
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='owned_boards'
    )
    members = models.ManyToManyField(
        User,
        related_name='member_boards',
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class List(models.Model):
    title = models.CharField(max_length=255)
    board = models.ForeignKey(
        Board,
        on_delete=models.CASCADE,
        related_name='lists'
    )
    position = models.IntegerField(default=0)

    class Meta:
        ordering = ['position']

    def __str__(self):
        return self.title


class Card(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    list = models.ForeignKey(
        List,
        on_delete=models.CASCADE,
        related_name='cards'
    )
    position = models.IntegerField(default=0)
    assigned_to = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_cards'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['position']

    def __str__(self):
        return self.title