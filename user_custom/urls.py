from django.conf.urls import url

from user_custom.views import MainView, CustomLoginView, edit_independent_article, CreateUserWriteUpView

urlpatterns = [
    url(r'^$', MainView.as_view()),
    url(r'^login/$', CustomLoginView.as_view(), name='custom_login'),
    url(r'^create_write_up/$', CreateUserWriteUpView.as_view(), name='create_write_up'),
    url(r'^edit_article/(?P<write_up_uuid>[^/]+)/$', edit_independent_article, name='edit_independent_article'),
]
