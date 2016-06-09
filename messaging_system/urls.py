from django.conf.urls import url

from messaging_system.views import ThreadView, MessageView

urlpatterns = [
    url(r'^threads/$', ThreadView.as_view()),
    url(r'^threads/(?P<thread_id>[^/]+)/$', MessageView.as_view()),
]
