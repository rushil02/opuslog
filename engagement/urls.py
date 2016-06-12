from django.conf.urls import url

from engagement.views import CommentView

urlpatterns = [
    url(r'^test/(?P<write_up_id>[^/]+)/$', CommentView.as_view()),
]
