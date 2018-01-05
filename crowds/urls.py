from django.conf.urls import url

from . import views

app_name = 'crowds'
urlpatterns = [
    url(r'^$', views.index, name='index'),
    #url(r'^predicted/$', views.predicted, name='predicted'),
]
