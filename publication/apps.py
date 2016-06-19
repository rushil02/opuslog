from __future__ import unicode_literals

from django.apps import AppConfig


class PublicationConfig(AppConfig):
    name = 'publication'
    verbose_name = 'Publication'

    def ready(self):
        pass
