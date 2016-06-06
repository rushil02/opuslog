from __future__ import unicode_literals
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

from django.db import models


class Privilege(models.Model):
    """
    Privileges are defined in multiple classes, where higher order class
    defines higher level privileges.
    It contains both kind of privileges,
        - to block
        - to unblock
    """

    name = models.CharField(max_length=100)
    help_text = models.CharField(max_length=250, null=True, blank=True)
    code_name = models.CharField(max_length=30)
    LEVEL = (('1', 'Level 1'),
             ('2', 'Level 2')
             )
    level = models.CharField(max_length=1, choices=LEVEL)
    create_time = models.DateTimeField(auto_now_add=True)


class Moderator(models.Model):
    """
    Moderator acts as the controlling entity for complete website with certain
    restricted rights. Classification defines the level of predefined
    privileges to the moderator.

    There is no precedence of a moderator's action over the other.
    """

    user = models.OneToOneField(settings.AUTH_USER_MODEL)
    privileges = models.ManyToManyField(Privilege)
    CHOICES = (('R', 'Reviewer'),
               ('A', 'Administrator'),
               )
    classification = models.CharField(max_length=1, choices=CHOICES)


class FlaggedEntity(models.Model):
    """ Stores all the flagged entities to be reviewed by a Moderator """

    LIMIT = models.Q(
        app_label='publication', model='publication'
    ) | models.Q(
        app_label='write_up', model='writeup'
    ) | models.Q(
        app_label='engagement', model='comment'
    ) | models.Q(
        app_label='user_custom', model='user'
    )
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, limit_choices_to=LIMIT)
    object_id = models.PositiveIntegerField()
    entity = GenericForeignKey('content_type', 'object_id')

    weight = models.PositiveIntegerField(default=0)
    CHOICES = (('C', 'Closed'),  # TODO: increase list
               ('O', 'Open'),
               ('P', 'Review Pending'),
               )
    status = models.CharField(max_length=1)
    update_time = models.DateTimeField(auto_now=True)
    create_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('content_type', 'object_id')


class ModeratorActionLog(models.Model):
    """
    Log to store moderator activity
    privilege_used is action done by moderator on entity
    """

    moderator = models.ForeignKey(Moderator)
    description = models.TextField()
    privilege_used = models.ForeignKey(Privilege)
    entity = models.ForeignKey(FlaggedEntity)
    create_time = models.DateTimeField(auto_now_add=True)


class FlagLog(models.Model):
    """ Logs all the flags on each entity """

    entity = models.ForeignKey(FlaggedEntity)
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    description = models.TextField()
    XP_at_flag_time = models.PositiveIntegerField()
    create_time = models.DateTimeField(auto_now_add=True)
