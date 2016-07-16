from django.conf.urls import url

from publication.views import (
    PublicationThreads, AddDeleteMemberToThread, MessageOfThread, publication_page, PublicationCommentNested,
    PublicationCommentFirstLevel, PublicationCommentDelete, PublicationVoteWriteup,
    PublicationSubscriber, PublicationVoteComment, publication_create_write_up_view, publication_edit_write_up_view,
    publication_edit_article_view, publication_collection_unit_view, publication_edit_collection_article_view)

urlpatterns = [
    url(r'^pub_details/$', publication_page, name='publication_details'),

    url(r'^threads/$', PublicationThreads.as_view(), name='all_threads'),
    url(r'^threads/(?P<thread_id>[^/]+)/$', PublicationThreads.as_view(), name='update_thread'),
    url(r'^threads/members/(?P<thread_id>[^/]+)/$', AddDeleteMemberToThread.as_view(), name='add_members'),
    url(r'^messages/(?P<thread_id>[^/]+)/$', MessageOfThread.as_view(), name='thread_messages'),

    url(r'^comments/(?P<write_up_uuid>[^/]+)/$', PublicationCommentFirstLevel.as_view(), name='first_level_comments'),
    url(r'^comments/nested/(?P<write_up_uuid>[^/]+)/(?P<comment_id>[^/]+)/$', PublicationCommentNested.as_view(),
        name='nested_comments'),
    url(r'^comments/delete/(?P<write_up_uuid>[^/]+)/(?P<comment_id>[^/]+)/$', PublicationCommentDelete.as_view(),
        name='delete_comment'),

    url(r'^vote/comment/(?P<comment_id>[^/]+)/$', PublicationVoteComment.as_view(), name='vote_comment'),

    url(r'^vote/write_up/(?P<write_up_uuid>[^/]+)/$', PublicationVoteWriteup.as_view(), name='vote_write_up'),

    url(r'^subscribe/$', PublicationSubscriber.as_view(), name='subscribe'),
    url(r'^create_write_up/$', publication_create_write_up_view, name='create_write_up'),
    url(r'^edit_write_up/(?P<write_up_uuid>[^/]+)/$', publication_edit_write_up_view, name='edit_write_up'),
    url(r'^edit_article/(?P<write_up_uuid>[^/]+)/$', publication_edit_article_view, name='edit_independent_article'),
    url(r'^edit_magazine_chapters/(?P<write_up_uuid>[^/]+)/$', publication_collection_unit_view,
        name='edit_magazine_chapters'),
    url(r'^edit_article/(?P<write_up_uuid>[^/]+)/(?P<chapter_index>[0-9]+)/$', publication_edit_collection_article_view,
        name='edit_magazine_article'),
]
