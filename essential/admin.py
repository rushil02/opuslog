from django.contrib import admin

from essential.models import Notification, Tag, Permission, Group, RequestLog, NotificationSetting


class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'acted_on', 'notification_type', 'context', 'data', 'notified',
                    'add_on_actor_count', 'verbose', 'update_time', 'create_time')


admin.site.register(Notification, NotificationAdmin)
admin.site.register(Tag)
admin.site.register(Permission)
admin.site.register(Group)
admin.site.register(RequestLog)
admin.site.register(NotificationSetting)
