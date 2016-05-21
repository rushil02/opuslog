from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User


class Publication(models.Model):
    """ creator is the sole owner of a Publication """

    creator = models.OneToOneField(User)
    contributors = models.ManyToManyField(User, related_name='contributors_in_publication',
                                          through='publication.ContributorList',
                                          through_fields=('publication', 'contributor'))
    name = models.CharField(max_length=150)
    XP = models.BigIntegerField(default=0)
    money = models.BigIntegerField(default=0)
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return self.name


class ContributorList(models.Model):
    """
    Every activity of publication is attached via this list and not to Publication model.
    On every new Publication creation, an entry will be created with owner set as the user.

    level -> Indicate just tags for the user with relation to a publication. While settings
    do not depend on it. But every tag will have a default list of settings (not implemented at db level).
    """

    contributor = models.ForeignKey(User, related_name='publication_contributors')
    share_XP = models.DecimalField(default=0.0, max_digits=8, decimal_places=5)
    share_money = models.DecimalField(default=0.0, max_digits=8, decimal_places=5)
    publication = models.ForeignKey(Publication)
    LEVEL = (('A', 'Administrator'),
             ('E', 'Editor'),
             ('N', 'Noob'),
             ('O', 'Owner'),
             )
    level = models.CharField(max_length=1, choices=LEVEL)
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("publication", "contributor")

    def __unicode__(self):
        return "'%s' of '%s'" % (self.contributor, self.publication)
