from django.conf.urls import url, include
from django.views import generic

from finance import views

urlpatterns = [
    url(r'^deposit/$', views.deposit, name='deposit'),
    url(r'^withdraw/$', views.withdraw, name='withdraw'),
    url(r'^loandevolution/$', views.loandevolution, name='loandevolution'),
    url(r'^loan_account_deposit/$/matches', views.loan_account_deposit_matches, name='loan_account_deposit_matches'),
    url(r'^loan_account_withdraw/$/matches', views.loan_account_withdraw_matches, name='loan_account_withdraw_matches'),
]