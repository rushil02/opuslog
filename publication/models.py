from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User

from user_custom.models import Contributor


class Publication(models.Model):
    creator = models.OneToOneField(User)
    name = models.CharField(max_length=150)
    XP = models.BigIntegerField(default=0)
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)


class ContributorList(Contributor):
    publication = models.ForeignKey(Publication, null=True)
    LEVEL = (('A', 'Administrator'),
             ('E', 'Editor'),
             ('N', 'Noob'),
             )
    level = models.CharField(max_length=1, choices=LEVEL)

    class Meta:
        unique_together = ("publication", "contributor")
