from django.contrib import admin

from engagement.models import *


class VoteWriteUpAdmin(admin.ModelAdmin):
    list_display = ('write_up', 'vote_type', 'content_type', 'object_id', 'publication_user', 'timestamp')


admin.site.register(VoteWriteUp, VoteWriteUpAdmin)
