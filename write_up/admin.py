from django.contrib import admin

from write_up.models import *


class WriteUpAdmin(admin.ModelAdmin):
    list_display = ('uuid', 'create_time', 'update_time')


admin.site.register(WriteUp, WriteUpAdmin)
admin.site.register(WriteupProfile)
admin.site.register(ContributorList)