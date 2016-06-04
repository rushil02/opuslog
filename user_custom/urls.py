from django.conf.urls import url

from user_custom.views import MainView

urlpatterns = [
    url(r'^$', MainView.as_view()),
]
