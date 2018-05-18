from django.shortcuts import render

from finance.models import FinantialDocument
from finance.forms import DepositForm


# Create your views here.
def documents_list(request):
    document_list = FinantialDocument.objects.order_by('-date')[:20]
    context = {
        'document_list': document_list,
    }
    return render(request, 'list.html', context)


def document_edit(request, pk):
    """ A view to edit a FinantialDocument"""
    count = 0
    if request.method == 'POST':
        # submitting form
        deposit_form = DepositForm(request.POST)
        if deposit_form.is_valid():
            deposit_form.save()
            count = 1
    else:
        # GET request
        try:
            fd = FinantialDocument.objects.get(pk=pk)
        except FinantialDocument.DoesNotExist:
            fd = None
        deposit_form = DepositForm(instance=fd)
    context = {
        'count': count,
        'form': deposit_form
    }
    return render(request, 'edit.html', context)


def deposit(request):
    return render(request, 'aqui va la respuesta')


def withdraw(request):
    return render(request, 'aqui va la respuesta')


def loan(request):
    return render(request, 'aqui va la respuesta')


def loandevolution(request):
    return render(request, 'aqui va la respuesta')


def loanmatch(request):
    return render(request, 'aqui va la respuesta')
