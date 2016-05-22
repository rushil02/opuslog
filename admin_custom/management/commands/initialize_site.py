from allauth.socialaccount.models import SocialApp
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.contrib.sites.models import Site


def socail_apps_info():  # TODO: Update method with actual keys
    """ Creates OAuth api token information for django-allauth """

    site_obj, s_created = Site.objects.get_or_create(domain='opuslog.com', name='Opuslog')
    fb_obj, fb_created = SocialApp.objects.get_or_create(provider='facebook', name='Facebook',
                                                         secret='some-key', client_id='some-id')
    fb_obj.sites.add(site_obj)

    gg_obj, gg_created = SocialApp.objects.get_or_create(provider='google', name='Google',
                                                         secret='some-key', client_id='some-id')
    gg_obj.sites.add(site_obj)


class Command(BaseCommand):
    """ Initialize website db with data"""
    help = 'Initialize website with user settings and details'

    def handle(self, *args, **options):
        try:
            with transaction.atomic():
                socail_apps_info()
                self.stdout.write("Website initialized with data")
        except Exception as e:
            print e.message
            raise CommandError("Some problem occurred. Rolling back changes, please initialize again.")
