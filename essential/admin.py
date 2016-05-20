from django.contrib import admin

from essential.models import Notification


class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'data', 'notified', 'timestamp')


admin.site.register(Notification, NotificationAdmin)
