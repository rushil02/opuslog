from django.contrib import admin

from write_up.models import *


class WriteUpCollectionAdmin(admin.ModelAdmin):
    list_display = ('user', 'publication', 'uuid', 'create_time', 'update_time')


admin.site.register(WriteUpCollection, WriteUpCollectionAdmin)
