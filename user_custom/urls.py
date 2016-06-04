from django.conf.urls import url

from user_custom.views import MainView, test_view

urlpatterns = [
    url(r'^$', MainView.as_view()),
    url(r'^test$', test_view),
]
