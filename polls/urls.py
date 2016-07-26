from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^accounts/login/$', views.login),
    url(r'^accounts/signup/$', views.signup),
    url(r'^profile/(?P<username>.*)/$', views.profile),
    url(r'^questions/(?P<question_id>\d*)/$', views.question),
    url(r'^questions/create/$', views.new_question),
    url(r'^vote/create/$', views.vote),
    url(r'^settings/$', views.settings),
    url(r'^accounts/logout/$', views.logout),
    url(r'^accounts/getinfo/$', views.getinfo),
    url(r'^answers/create/(?P<question_id>\d*)/$', views.new_answer),
    url(r'^follow/$', views.follow),
    url(r'^accounts/deactive/$', views.deactive_user),
    url(r'^chat/', views.chat)
]
