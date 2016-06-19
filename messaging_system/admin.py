from django.contrib import admin

from messaging_system.models import Thread, ThreadMember, Message

admin.site.register(Thread)
admin.site.register(ThreadMember)
admin.site.register(Message)
