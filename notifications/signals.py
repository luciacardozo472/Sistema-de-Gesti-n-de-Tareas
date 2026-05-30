from django.db.models.signals import post_save
from django.dispatch import receiver
from boards.models import Card
from .models import Notification


@receiver(post_save, sender=Card)
def notify_card_assignment(sender, instance, created, **kwargs):
    if instance.assigned_to is not None:
        if created:
            message = f'Te asignaron la tarjeta "{instance.title}"'
        else:
            message = f'Te reasignaron la tarjeta "{instance.title}"'

        Notification.objects.create(
            recipient=instance.assigned_to,
            message=message
        )