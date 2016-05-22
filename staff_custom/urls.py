from django.conf.urls import url

from staff_custom.views import *

urlpatterns = [
    url(r'^$', home, name='home'),
]
