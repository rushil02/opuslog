from __future__ import unicode_literals

from django.db import models
from cities_light.abstract_models import (AbstractCity, AbstractRegion,
                                          AbstractCountry)
from cities_light.receivers import connect_default_signals


class Country(AbstractCountry):
    pass


connect_default_signals(Country)


class Region(AbstractRegion):
    pass


connect_default_signals(Region)


class City(AbstractCity):
    timezone = models.CharField(max_length=40)


connect_default_signals(City)
