from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^deposit/$', views.deposit, name='deposit'),
    url(r'^withdraw/$', views.withdraw, name='withdraw'),
    url(r'^loan/$', views.loan, name='loan'),
    url(r'^loandevolution/$', views.loandevolution, name='loandevolution'),
    url(r'^loanmatch/$', views.loanmatch, name='loanmatch'),
]

