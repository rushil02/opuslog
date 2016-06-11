from django.conf.urls import url

from publication.views import PublicationThreads

urlpatterns = [
    url(r'^threads/$', PublicationThreads.as_view(), name='all_threads'),
    # url(r'^messages/(?P<thread_id>[^/]+)/$', CustomLoginView.as_view(), name='thread_messages'),

]
