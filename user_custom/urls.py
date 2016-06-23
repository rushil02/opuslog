from django.conf.urls import url

from user_custom.views import MainView, CustomLoginView, CreateUserWriteUpView, edit_article_view, edit_write_up_view, \
    collection_unit_view, edit_collection_article_view

urlpatterns = [
    url(r'^$', MainView.as_view()),
    url(r'^login/$', CustomLoginView.as_view(), name='custom_login'),
    url(r'^create_write_up/$', CreateUserWriteUpView.as_view(), name='create_write_up'),
    url(r'^edit_article/(?P<write_up_uuid>[^/]+)/$', edit_article_view, name='edit_independent_article'),
    url(r'^edit_write_up/(?P<write_up_uuid>[^/]+)/$', edit_write_up_view, name='edit_user_write_up'),
    url(r'^edit_magazine_chapters/(?P<write_up_uuid>[^/]+)/$', collection_unit_view, name='edit_magazine_chapters'),
    url(r'^edit_article/(?P<write_up_uuid>[^/]+)/(?P<chapter_index>[0-9]+)/$', edit_collection_article_view,
        name='edit_magazine_article'),
]
