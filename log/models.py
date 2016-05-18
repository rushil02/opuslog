from __future__ import unicode_literals

from django.contrib.auth.models import User
from django.db import models


class AnonymousViewer(models.Model):
    write_up = models.ForeignKey('write_up.WriteUpCollection')
    duration = models.PositiveSmallIntegerField(default=0)
    create_time = models.DateTimeField(auto_now_add=True)


class RegisteredViewer(models.Model):
    user = models.ForeignKey(User)
    write_up = models.ForeignKey('write_up.WriteUpCollection')
    duration = models.PositiveSmallIntegerField(default=0)
    create_time = models.DateTimeField(auto_now_add=True)
