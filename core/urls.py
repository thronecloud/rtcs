from django.conf.urls import url

import views

urlpatterns = [
    url(r'^$', views.index_view, name="home"),
    url(
        r'^new$',
        views.CreateCabRequest.as_view(),
        name="cabrequest_new"),
    url(
        r'^(?P<pk>\d+)$',
        views.CabRequestDetail.as_view(),
        name="cabrequest_view"),
    url(
        r'^(?P<pk>\d+)/delete$',
        views.CabRequestDelete.as_view(),
        name="cabrequest_delete"),
]
