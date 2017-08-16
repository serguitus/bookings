from django.shortcuts import render
from django.http import HttpResponse
from cuentas.models import Caja

# Create your views here.

def index(request):
    c = Caja.objects.get(id=4)
    return HttpResponse('esto es lo de siempre... Hola Mundo. total %s' % c.balance)

def transfer(request):
    return HttpResponse('aqui va la respuesta')
