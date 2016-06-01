from __future__ import unicode_literals

from django.contrib.contenttypes.fields import GenericRelation
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.contrib.auth.models import AbstractUser
from cities_light.models import Region, Country, City
from django.conf import settings

from admin_custom.custom_errors import PermissionDenied


class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL)
    dob = models.DateField(blank=True, null=True)
    GENDER = (
        ('M', 'Male'),
        ('F', 'Female'),
    )
    gender = models.CharField(max_length=1, choices=GENDER, blank=True, null=True)
    area_city = models.ForeignKey(City, blank=True, null=True)  # TODO: test if all cities data is available/needed
    area_state = models.ForeignKey(Region, blank=True, null=True)
    area_country = models.ForeignKey(Country, blank=True, null=True)
    update_time = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return self.user.get_full_name()


class User(AbstractUser):
    """
    This model replaces default Auth.User model tom implement all reverse
    relations for generic foreign key. Subscribed relation will provide the
    subscriptions made by specific user. Subscriptions relation will provide
    users/publications that have subscribed to specific user. Related query
    name is reverse relationship in query for their respective generic foreign
    keys.
    """

    write_up_votes = GenericRelation('engagement.VoteWriteUp', related_query_name='extended_user')
    write_up_comments = GenericRelation('engagement.Comment', related_query_name='extended_user')
    vote_comments = GenericRelation('engagement.VoteComment', related_query_name='extended_user')
    subscribed = GenericRelation('engagement.Subscriber', related_query_name='extended_user_subscribed')
    subscriptions = GenericRelation('engagement.Subscriber', 'object_id_2', 'content_type_2',
                                    related_query_name='extended_user_subscriptions')
    contribution = GenericRelation('write_up.ContributorList', related_query_name='extended_user')

    def get_full_name(self):
        super(User, self).get_full_name()

    def get_short_name(self):
        super(User, self).get_short_name()

    def get_user_writeup_with_permission(self, write_up_uuid, permission_level):
        try:
            writeup_contributor = self.contribution.get_contributor_with_permission_for_writeup(write_up_uuid,
                                                                                                permission_level)
        except ObjectDoesNotExist:
            raise PermissionDenied
        else:
            return writeup_contributor.write_up
