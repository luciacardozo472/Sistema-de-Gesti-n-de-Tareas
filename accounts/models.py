from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class UserProfile(models.Model):
    LEVEL_ADMIN = 0
    LEVEL_USER = 1
    LEVEL_CHOICES = [
        (LEVEL_ADMIN, 'Administrador'),
        (LEVEL_USER, 'Usuario'),
    ]
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile'
    )
    level = models.IntegerField(
        choices=LEVEL_CHOICES,
        default=LEVEL_USER
    )

    class Meta:
        verbose_name = 'Perfil de usuario'
        verbose_name_plural = 'Perfiles de usuario'

    def __str__(self):
        rol = 'Administrador' if self.level == 0 else 'Usuario'
        return f"{self.user.username} ({rol})"

    @property
    def is_admin(self):
        return self.level == 0


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.get_or_create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'profile'):
        instance.profile.save()