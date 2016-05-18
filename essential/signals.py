from django.dispatch import receiver
from django.db.models.signals import post_save

from essential.models import RevisionHistory


@receiver(post_save, sender='write_up.BaseDesign')
def create_revision_history(sender, **kwargs):
    base_design = kwargs.get('instance')  # TODO: send user
    user = kwargs.get('user')
    RevisionHistory.objects.create(parent=base_design, user=user, text=base_design.text)
