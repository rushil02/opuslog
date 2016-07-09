from django.conf.urls import url

from user_custom.views.views_api_1 import (
    UserCommentFirstLevel, UserCommentNested, UserThreads, AddDeleteMemberToThread, MessageOfThread,
    UserCommentDelete, UserVoteWriteup, UserSubscriber, UserVoteComment, UserRequest)
from user_custom.views.views import MainView, CustomLoginView, CreateUserWriteUpView, edit_article_view, \
    edit_write_up_view, \
    collection_unit_view, edit_collection_article_view, user_page, user_contributor_request_view

urlpatterns = [
    url(r'^user_details/(?P<user_handler>[^/]+)/$', user_page, name='user_details'),

    url(r'^$', MainView.as_view()),  # TODO: name?
    url(r'^login/$', CustomLoginView.as_view(), name='custom_login'),
    url(r'^create_write_up/$', CreateUserWriteUpView.as_view(), name='create_write_up'),
    url(r'^edit_article/(?P<write_up_uuid>[^/]+)/$', edit_article_view, name='edit_independent_article'),
    url(r'^edit_write_up/(?P<write_up_uuid>[^/]+)/$', edit_write_up_view, name='edit_user_write_up'),
    url(r'^edit_magazine_chapters/(?P<write_up_uuid>[^/]+)/$', collection_unit_view, name='edit_magazine_chapters'),
    url(r'^edit_article/(?P<write_up_uuid>[^/]+)/(?P<chapter_index>[0-9]+)/$', edit_collection_article_view,
        name='edit_magazine_article'),

    url(r'^threads/$', UserThreads.as_view(), name='all_threads'),
    url(r'^threads/(?P<thread_id>[^/]+)/$', UserThreads.as_view(), name='update_thread'),
    url(r'^threads/members/(?P<thread_id>[^/]+)/$', AddDeleteMemberToThread.as_view(), name='add_members'),
    url(r'^messages/(?P<thread_id>[^/]+)/$', MessageOfThread.as_view(), name='thread_messages'),

    url(r'^comments/(?P<write_up_uuid>[^/]+)/$', UserCommentFirstLevel.as_view(), name='first_level_comments'),
    url(r'^comments/nested/(?P<write_up_uuid>[^/]+)/(?P<comment_id>[^/]+)/$', UserCommentNested.as_view(),
        name='nested_comments'),
    url(r'^contributor_request/(?P<write_up_uuid>[^/]+)/$', user_contributor_request_view,
        name='user_contributor_request_view'),
    url(r'^comments/delete/(?P<write_up_uuid>[^/]+)/(?P<comment_id>[^/]+)/$', UserCommentDelete.as_view(),
        name='delete_comment'),

    url(r'^vote/comment/(?P<comment_id>[^/]+)/$', UserVoteComment.as_view(), name='vote_comment'),

    url(r'^vote/write_up/(?P<write_up_uuid>[^/]+)/$', UserVoteWriteup.as_view(), name='vote_write_up'),

    url(r'^subscribe/$', UserSubscriber.as_view(), name='subscribe'),

    url(r'^request/(?P<notification_id>[0-9]+)/$', UserRequest.as_view(), name='request'),

]
