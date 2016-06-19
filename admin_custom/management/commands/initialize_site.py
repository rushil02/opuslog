from allauth.socialaccount.models import SocialApp
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.contrib.sites.models import Site
from django.apps import apps

from essential.models import Permission, Tag


def socail_apps_info():  # TODO: Update method with actual keys
    """ Creates OAuth api token information for django-allauth """

    site_obj, s_created = Site.objects.get_or_create(domain='opuslog.com', name='Opuslog')
    fb_obj, fb_created = SocialApp.objects.get_or_create(provider='facebook', name='Facebook',
                                                         secret='some-key', client_id='some-id')
    fb_obj.sites.add(site_obj)

    gg_obj, gg_created = SocialApp.objects.get_or_create(provider='google', name='Google',
                                                         secret='some-key', client_id='some-id')
    gg_obj.sites.add(site_obj)


def create_permissions():
    """
    Creates type of permissions to be set for each contributor in a writeup/Publication
    Fetches from all the registered models, if any publication permission is defined

    Structure -> [{'name': 'abc', 'help_text': 'help for abc', 'code_name': 'abc_code',
                   'for' :'W/P/B'}, {...}, ... ]
    """

    for model in apps.get_models():
        try:
            permissions = model.Permissions.permission_list
        except Exception:
            continue
        else:
            content_type = ContentType.objects.get_for_model(model)
            for perm in permissions:
                Permission.objects.get_or_create(
                    name=perm.get('name'),
                    code_name=perm.get('code_name'),
                    permission_for=perm.get('for', 'B'),
                    help_text=perm.get('help_text', None),
                    content_type=content_type
                )


def create_tags():  # TODO: Set all tags here
    """ Creates primary tags to be set for each writeup/Publication """

    Tag.objects.get_or_create(name="sports", tag_type='P')


class Command(BaseCommand):
    """ Initialize website db with data """

    help = 'Initialize website with settings and details data'

    def handle(self, *args, **options):
        try:
            with transaction.atomic():
                socail_apps_info()
                create_permissions()
                create_tags()
        except Exception as e:
            print e.message
            raise CommandError("Some problem occurred. Rolling back changes.")
        else:
            self.stdout.write("Website initialized with data")
