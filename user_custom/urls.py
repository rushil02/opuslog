from django.conf.urls import url

from user_custom.views.views import MainView, CustomLoginView, user_page
from user_custom.views.views_api_1 import (
    UserCommentFirstLevel, UserCommentNested, UserThreads, AddDeleteMemberToThread, MessageOfThread
)

urlpatterns = [
    url(r'^user_details/(?P<user_handler>[^/]+)/$', user_page, name='user_details'),

    url(r'^$', MainView.as_view()),  # TODO: name?
    url(r'^login/$', CustomLoginView.as_view(), name='custom_login'),

    url(r'^threads/$', UserThreads.as_view(), name='all_threads'),
    url(r'^threads/(?P<thread_id>[^/]+)/$', UserThreads.as_view(), name='update_thread'),
    url(r'^threads/members/(?P<thread_id>[^/]+)/$', AddDeleteMemberToThread.as_view(), name='add_members'),
    url(r'^messages/(?P<thread_id>[^/]+)/$', MessageOfThread.as_view(), name='thread_messages'),

    url(r'^comments/(?P<write_up_uuid>[^/]+)/$', UserCommentFirstLevel.as_view(), name='first_level_comments'),
    url(r'^comments/nested/(?P<write_up_uuid>[^/]+)/(?P<comment_id>[^/]+)/$', UserCommentNested.as_view(),
        name='nested_comments'),
]
