from django.conf.urls import url
from django.contrib.auth.decorators import login_required

from admin_custom.decorators import has_write_up_perm
from user_custom.views import MainView, CustomLoginView, edit_independent_article, CreateUserWriteUpView, \
    EditUserWriteUpView

urlpatterns = [
    url(r'^$', MainView.as_view()),
    url(r'^login/$', CustomLoginView.as_view(), name='custom_login'),
    url(r'^create_write_up/$', CreateUserWriteUpView.as_view(), name='create_write_up'),
    url(r'^edit_article/(?P<write_up_uuid>[^/]+)/$', edit_independent_article, name='edit_independent_article'),
    url(r'^edit_write_up/(?P<write_up_uuid>[^/]+)/$',
        login_required()(has_write_up_perm("CAN_EDIT")(EditUserWriteUpView.as_view())), name='edit_user_write_up'),
]
