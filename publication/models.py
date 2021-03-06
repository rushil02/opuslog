from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User


class Publication(models.Model):
    """ creator is the sole owner of a Publication """

    creator = models.OneToOneField(User)
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
    """

    contributor = models.ForeignKey(User, related_name='publication_contributors')
    share_XP = models.PositiveSmallIntegerField(default=0)
    share_money = models.PositiveSmallIntegerField(default=0)
    publication = models.ForeignKey(Publication, null=True)
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
