from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth.models import User
from ..models import Notification
from .serializers import NotificationSerializer


def is_admin(user):
    return hasattr(user, 'profile') and user.profile.level == 0


class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(recipient=self.request.user)

    @action(detail=True, methods=['patch'])
    def mark_as_read(self, request, pk=None):
        notification = self.get_object()
        notification.is_read = True
        notification.save()
        return Response({'status': 'notificación marcada como leída'})

    @action(detail=False, methods=['patch'])
    def mark_all_as_read(self, request):
        self.get_queryset().update(is_read=True)
        return Response({'status': 'todas las notificaciones marcadas como leídas'})

    @action(detail=False, methods=['post'])
    def send(self, request):
        if not is_admin(request.user):
            return Response(
                {'error': 'Solo el administrador puede enviar notificaciones'},
                status=status.HTTP_403_FORBIDDEN
            )
        recipient_id = request.data.get('recipient_id')
        message = request.data.get('message', '').strip()
        if not recipient_id or not message:
            return Response(
                {'error': 'recipient_id y message son requeridos'},
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            recipient = User.objects.get(id=recipient_id)
            full_message = f'📢 Mensaje del administrador: {message}'
            notification = Notification.objects.create(
                recipient=recipient,
                message=full_message
            )
            try:
                from channels.layers import get_channel_layer
                from asgiref.sync import async_to_sync
                channel_layer = get_channel_layer()
                async_to_sync(channel_layer.group_send)(
                    f'user_{recipient.id}',
                    {'type': 'notification_message', 'message': full_message}
                )
            except Exception:
                pass
            return Response(NotificationSerializer(notification).data, status=status.HTTP_201_CREATED)
        except User.DoesNotExist:
            return Response({'error': 'Usuario no encontrado'}, status=status.HTTP_404_NOT_FOUND)