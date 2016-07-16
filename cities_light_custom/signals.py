import cities_light
from cities_light.settings import ICity


def set_city_fields(sender, instance, items, **kwargs):
    instance.timezone = items[ICity.timezone]


cities_light.signals.city_items_post_import.connect(set_city_fields)
