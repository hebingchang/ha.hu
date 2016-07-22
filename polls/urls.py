from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^accounts/login/$', views.login),
    url(r'^accounts/signup/$', views.signup),
    url(r'^profile/(?P<username>.*)/$', views.profile),
    url(r'^questions/(?P<question_id>\d*)/$', views.question),
    url(r'^questions/create/$', views.new_question),
    url(r'^vote/create/', views.vote),
    url(r'^settings/profile/', views.settings_profile),
    url(r'^accounts/logout/$', views.logout),
    url(r'^accounts/getinfo/$', views.getinfo)
]
