from django.contrib import admin

from engagement.models import VoteWriteUp, Comment, VoteComment, Subscriber


class EngagementAdmin(admin.ModelAdmin):
    list_display = ('publication_user', 'content_type', 'object_id', 'actor', 'timestamp')

    def get_readonly_fields(self, request, obj=None):
        if request.user.is_superuser:
            self.readonly_fields = ()
        else:
            self.readonly_fields = self.list_display
        return self.readonly_fields

    def get_list_display_links(self, request, list_display):
        if request.user.is_superuser:
            self.list_display_links = list(list_display)[:1]
        else:
            self.list_display_links = None
        return self.list_display_links

    list_filter = ('content_type',)
    date_hierarchy = 'timestamp'


class VoteWriteUpAdmin(EngagementAdmin):
    list_display = ('vote_type', 'write_up') + EngagementAdmin.list_display

    search_fields = ('video_id__name', 'promoter_id__promoter_id__email')


class CommentAdmin(EngagementAdmin):
    list_display = ('comment_text', 'write_up', 'reply_to', 'delete_request') + EngagementAdmin.list_display


class VoteCommentAdmin(EngagementAdmin):
    list_display = ('vote_type', 'comment') + EngagementAdmin.list_display


class SubscriberAdmin(EngagementAdmin):
    list_display = ('content_type_2', 'object_id_2', 'subscribed') + EngagementAdmin.list_display


admin.site.register(VoteWriteUp, VoteWriteUpAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(VoteComment, VoteCommentAdmin)
admin.site.register(Subscriber, SubscriberAdmin)
