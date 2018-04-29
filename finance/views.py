from django.shortcuts import render

# Create your views here.
def documents(request):
    cocument_list = FinantialDocument.objects.order_by('-date')[:20]
    template = loader.get_template('finance/documents.html')
    context = {
        'document_list': document_list,
    }
    return HttpResponse(template.render(context, request))


def deposit(request):
    return HttpResponse('aqui va la respuesta')

def withdraw(request):
    return HttpResponse('aqui va la respuesta')

def loan(request):
    return HttpResponse('aqui va la respuesta')

def loandevolution(request):
    return HttpResponse('aqui va la respuesta')

def loanmatch(request):
    return HttpResponse('aqui va la respuesta')
