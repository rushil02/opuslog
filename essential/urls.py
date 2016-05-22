from django.conf.urls import url

from essential.views import NotificationView

urlpatterns = [
    url(r'^notification/$', NotificationView.as_view(), name='user_notification'),
]
