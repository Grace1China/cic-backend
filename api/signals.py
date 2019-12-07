from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import userProfile
import logging
import pprint


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    print('-----------create_profile----------')

    if created:
        logging.debug('-----------create_profile----------')
        pp = pprint.PrettyPrinter(4)
        pp.pprint(sender)
        pp.pprint(instance)
        pp.pprint(kwargs)
        userProfile.objects.create(user=instance)
# post_save.connect(create_profile)