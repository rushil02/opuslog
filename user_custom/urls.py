from django.conf.urls import url

from user_custom.views import MainView, CustomLoginView

urlpatterns = [
    url(r'^$', MainView.as_view()),
    url(r'^login/$', CustomLoginView.as_view(), name='custom_login'),
]
