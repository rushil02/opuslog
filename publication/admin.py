from django.contrib import admin

from publication.models import *


class PublicationAdmin(admin.ModelAdmin):
    list_display = ('creator', 'name', 'XP', 'create_time', 'update_time')


admin.site.register(Publication, PublicationAdmin)
