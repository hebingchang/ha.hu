from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^accounts/login/$', views.login),
    url(r'^accounts/logout/$', views.logout),
    url(r'^accounts/signup/$', views.signup),
    url(r'^accounts/getinfo/$', views.getinfo),
    url(r'^accounts/deactive/$', views.deactive_user),
    url(r'^profile/(?P<username>.*)/$', views.profile),
    url(r'^questions/(?P<question_id>.*)/$', views.question),
    url(r'^question/create/$', views.new_question),
    url(r'^questions/delete/$', views.delete_question),
    url(r'^vote/create/$', views.vote),
    url(r'^settings/$', views.settings),
    url(r'^answers/create/(?P<question_id>\d*)/$', views.new_answer),
    url(r'^answers/delete/', views.delete_answer),
    url(r'^chat/', views.chat),
    url(r'^accounts/logout/$', views.logout),
    url(r'^follow/$', views.follow),
    url(r'^discover/$', views.discover)
]
