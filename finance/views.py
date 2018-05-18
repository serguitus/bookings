from django.shortcuts import render

from finance.models import FinantialDocument


# Create your views here.
def documents(request):
    document_list = FinantialDocument.objects.order_by('-date')[:20]
    context = {
        'document_list': document_list,
    }
    return render(request, 'list.html', context)


def deposit(request):
    return render('aqui va la respuesta')


def withdraw(request):
    return render('aqui va la respuesta')


def loan(request):
    return render('aqui va la respuesta')


def loandevolution(request):
    return render('aqui va la respuesta')


def loanmatch(request):
    return render('aqui va la respuesta')
