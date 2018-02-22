from django.conf.urls import url
from django.contrib import admin, messages
from django.http import HttpResponseRedirect
from django.template.response import TemplateResponse
from django.utils.html import format_html
from django.core.urlresolvers import reverse

from .exceptions import Error
# from .forms import DepositForm, WithdrawForm, TransferForm

# Register your models here.
from .models import Account, Operation
admin.site.register(Account)
admin.site.register(Operation)

