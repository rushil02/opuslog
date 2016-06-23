from django.contrib import admin

from write_up.models import *


class WriteUpAdmin(admin.ModelAdmin):
    list_display = ('uuid', 'create_time', 'update_time')


admin.site.register(WriteUp, WriteUpAdmin)
admin.site.register(WriteupProfile)
admin.site.register(ContributorList)
admin.site.register(BaseDesign)
admin.site.register(Unit)
admin.site.register(UnitContributor)
admin.site.register(CollectionUnit)
admin.site.register(LiveWriting)
admin.site.register(GroupWriting)
admin.site.register(GroupWritingText)
admin.site.register(RevisionHistory)
