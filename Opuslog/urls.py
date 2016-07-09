"""Opuslog URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin

urlpatterns = [
    url(r'^db/', admin.site.urls),
    url(r'^admin/', include('admin_custom.urls', namespace='admin_custom')),
    url(r'^staff/', include('staff_custom.urls', namespace='staff')),
    url(r'^accounts/', include('allauth.urls')),
    url(r'^', include('user_custom.urls', namespace='user_custom')),
    url(r'^pub/(?P<pub_handler>[^/]+)/', include('publication.urls', namespace='publication')),
    url(r'^tinymce/', include('tinymce.urls')),
    url(r'^es/', include('essential.urls', namespace='essential')),
    url(r'^search/', include('haystack.urls')),
]
