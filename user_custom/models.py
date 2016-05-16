from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User
from cities_light.models import Region, Country, City


# Create your models here.


class UserProfile(models.Model):
    user = models.OneToOneField(User)
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


class Contributor(models.Model):
    contributor = models.ForeignKey(User)
    share_XP = models.PositiveSmallIntegerField(default=0)
    share_money = models.PositiveSmallIntegerField(default=0)

    class Meta:
        abstract = True
