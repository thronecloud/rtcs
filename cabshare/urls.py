"""cabshare URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf.urls import include, url
from django.contrib import admin

from core import views

urlpatterns = [
    url(r'^$', views.index_view, name="home"),
    url(
        r'^cabrequest/new$',
        views.CreateCabRequest.as_view(),
        name="cabrequest_new"),
    url(
        r'^cabrequest/(?P<pk>\d+)$',
        views.CabRequestDetail.as_view(),
        name="cabrequest_view"),
    url(
        r'^cabrequest/(?P<pk>\d+)/delete$',
        views.CabRequestDelete.as_view(),
        name="cabrequest_delete"),
    url(r'^accounts/', include('allauth.urls')),
    url(r'^accounts/profile$', views.userdetail_view, name="user_profile"),
    url(r'^admin/', include(admin.site.urls)),
]
