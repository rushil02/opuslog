from django.conf.urls import url

from publication.views import (
    PublicationThreads, AddDeleteMemberToThread, MessageOfThread, publication_page, PublicationCommentNested,
    PublicationCommentFirstLevel,
    PublicationCommentDelete, PublicationUpVoteWriteup, PublicationDownVoteWriteup, PublicationRemoveVoteWriteup
)

urlpatterns = [
    url(r'^pub_details/(?P<publication_handler>[^/]+)/$', publication_page, name='publication_details'),

    url(r'^threads/$', PublicationThreads.as_view(), name='all_threads'),
    url(r'^threads/(?P<thread_id>[^/]+)/$', PublicationThreads.as_view(), name='update_thread'),
    url(r'^threads/members/(?P<thread_id>[^/]+)/$', AddDeleteMemberToThread.as_view(), name='add_members'),
    url(r'^messages/(?P<thread_id>[^/]+)/$', MessageOfThread.as_view(), name='thread_messages'),

    url(r'^comments/(?P<write_up_uuid>[^/]+)/$', PublicationCommentFirstLevel.as_view(), name='first_level_comments'),
    url(r'^comments/nested/(?P<write_up_uuid>[^/]+)/(?P<comment_id>[^/]+)/$', PublicationCommentNested.as_view(),
        name='nested_comments'),
    url(r'^comments/delete/(?P<write_up_uuid>[^/]+)/(?P<comment_id>[^/]+)/$', PublicationCommentDelete.as_view(),
        name='delete_comment'),

    url(r'^vote/write_up/up/(?P<write_up_uuid>[^/]+)/$', PublicationUpVoteWriteup.as_view(),
        name='up_vote_write_up'),
    url(r'^vote/write_up/down/(?P<write_up_uuid>[^/]+)/$', PublicationDownVoteWriteup.as_view(),
        name='up_vote_write_up'),
    url(r'^vote/write_up/remove/(?P<write_up_uuid>[^/]+)/$', PublicationRemoveVoteWriteup.as_view(),
        name='up_vote_write_up'),
]
