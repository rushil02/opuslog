from django.conf.urls import url

from publication.views import PublicationThreads, AddDeleteMemberToThread, MessageOfThread, publication_page

urlpatterns = [
    url(r'^pub_details/(?P<publication_handler>[^/]+)/$', publication_page, name='publication_details'),
    url(r'^threads/$', PublicationThreads.as_view(), name='all_threads'),
    url(r'^threads/(?P<thread_id>[^/]+)/$', PublicationThreads.as_view(), name='update_thread'),
    url(r'^threads/members/(?P<thread_id>[^/]+)/$', AddDeleteMemberToThread.as_view(), name='add_members'),
    url(r'^messages/(?P<thread_id>[^/]+)/$', MessageOfThread.as_view(), name='thread_messages'),
]
