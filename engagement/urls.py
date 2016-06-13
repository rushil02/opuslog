from django.conf.urls import url

from engagement.views import CommentFirstLevelView, CommentNestedView

urlpatterns = [
    url(r'^comments/(?P<write_up_id>[^/]+)/$', CommentFirstLevelView.as_view()),
    url(r'^comments/s_level/(?P<write_up_id>[^/]+)/(?P<comment_id>[^/]+)/$', CommentNestedView.as_view()),
]
# TODO: change to uuid
