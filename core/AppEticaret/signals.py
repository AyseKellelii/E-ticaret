from django.contrib.auth.models import User
from .models import *
from django.db.models.signals import post_save
from django.dispatch import receiver


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profil.objects.create(user=instance)


@receiver(post_save, sender=User)
def create_address(sender, instance, created, **kwargs):
    if created:
        Adress.objects.create(user=instance)