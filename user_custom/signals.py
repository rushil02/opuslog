from allauth.account.signals import user_signed_up
from django.contrib.auth import get_user_model
from django.dispatch import receiver

from essential.models import Group


@receiver(user_signed_up, sender=get_user_model())
def post_sign_up(sender, **kwargs):
    user = kwargs.get('user')
    Group.objects.bulk_create([
        Group(entity=user, name='Primary'),
        Group(entity=user, name='Contributed Write-ups', contributed_group=True)
    ])
