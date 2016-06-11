from django.conf.urls import url

from user_custom.views import MainView, CustomLoginView, UserThreads, AddDeleteMemberToThread, MessageOfThread

urlpatterns = [
    url(r'^$', MainView.as_view()),
    url(r'^login/$', CustomLoginView.as_view(), name='custom_login'),
    url(r'^threads/$', UserThreads.as_view(), name='all_threads'),
    url(r'^threads/(?P<thread_id>[^/]+)/$', UserThreads.as_view(), name='update_thread'),
    url(r'^threads/members/(?P<thread_id>[^/]+)/$', AddDeleteMemberToThread.as_view(), name='add_members'),
    url(r'^messages/(?P<thread_id>[^/]+)/$', MessageOfThread.as_view(), name='thread_messages'),
]
