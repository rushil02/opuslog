from django.contrib import admin

from essential.models import Notification


class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'write_up', 'notification_type', 'data', 'notified',
                    'add_on_actor_count', 'update_time', 'create_time')


admin.site.register(Notification, NotificationAdmin)
