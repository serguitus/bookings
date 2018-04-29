from django.conf.urls import url

from . import views

urlpatterns = [
    # ex: /accounts/
    url(r'^$', views.IndexView.as_view(), name='accounts'),
    # ex: /accounts/10/
    url(r'^(?P<pk>[0-9]+)/$', views.DetailView.as_view(), name='detail'),
]
