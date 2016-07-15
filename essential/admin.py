from django.contrib import admin

from essential.models import Notification, Tag, Permission, Group, RequestLog, GroupContributor, WriteUpContributor


class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'write_up', 'notification_type', 'data', 'notified',
                    'add_on_actor_count', 'update_time', 'create_time')


admin.site.register(Notification, NotificationAdmin)
admin.site.register(Tag)
admin.site.register(Permission)
admin.site.register(Group)
admin.site.register(RequestLog)
admin.site.register(GroupContributor)
admin.site.register(WriteUpContributor)
