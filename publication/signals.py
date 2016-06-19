from django.dispatch import receiver
from django.db.models.signals import post_save

from publication.models import Publication, ContributorList


@receiver(post_save, sender=Publication)  # FIXME: move to model
def create_owner_in_contributor_list(sender, **kwargs):
    """ Create entry of owner in ContributorList model """

    if kwargs.get('created', True):
        publication = kwargs.get('instance')
        ContributorList.objects.create(contributor=publication.creator, share_XP=100, share_money=100,
                                       publication=publication, level='C')
