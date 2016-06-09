from django.contrib import admin

from messaging_system.models import Thread, ThreadMembers, Message

admin.site.register(Thread)
admin.site.register(ThreadMembers)
admin.site.register(Message)
