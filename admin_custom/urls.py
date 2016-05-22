from django.conf.urls import url

from admin_custom.views import *

urlpatterns = [
    url(r'^$', home, name='home'),
    url(r'^register_staff/', staff_registration, name='staff_register'),
]
