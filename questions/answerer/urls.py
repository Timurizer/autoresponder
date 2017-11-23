from django.conf.urls import url
from . import views

app_name = 'answerer'

urlpatterns = [
    url(r'^autoresponder/(?P<question>[\w\-]+)/$', views.ask_question, name='ask_question'),
    url(r'^autoresponder/(?P<question>[\w\-]+)/(?P<count>[0-9]+)/$', views.ask_question, name='ask_question'),
]
