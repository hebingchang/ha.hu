from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^accounts/login/$', views.login),
    url(r'^accounts/signup/$', views.signup),
    url(r'^profile/(?P<username>.*)', views.profile),
]
