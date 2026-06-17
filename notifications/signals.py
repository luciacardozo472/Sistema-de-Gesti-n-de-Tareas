from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from boards.models import Card
from .models import Notification

_previous_assigned = {}


@receiver(pre_save, sender=Card)
def track_assigned_to(sender, instance, **kwargs):
    if instance.pk:
        try:
            old = Card.objects.get(pk=instance.pk)
            _previous_assigned[instance.pk] = old.assigned_to_id
        except Card.DoesNotExist:
            _previous_assigned[instance.pk] = None
    else:
        _previous_assigned[instance.pk] = None


@receiver(post_save, sender=Card)
def notify_card_assignment(sender, instance, created, **kwargs):
    if instance.assigned_to is None:
        return

    prev = _previous_assigned.pop(instance.pk, None)
    if instance.assigned_to_id == prev and not created:
        return

    message = (
        f'Te asignaron la tarjeta "{instance.title}"'
        if created else
        f'Te reasignaron la tarjeta "{instance.title}"'
    )

    Notification.objects.create(
        recipient=instance.assigned_to,
        message=message
    )

    try:
        from channels.layers import get_channel_layer
        from asgiref.sync import async_to_sync
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f'user_{instance.assigned_to.id}',
            {'type': 'notification_message', 'message': message}
        )
    except Exception:
        pass