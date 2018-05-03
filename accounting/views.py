from django.shortcuts import *
from django.http import *
from django.core.urlresolvers import *
from django.views import generic

from .models import *
from .services import *

class IndexView(generic.ListView):
    template_name = 'account/index.html'
    context_object_name = 'account_list'

    def get_queryset(self):
        """Return the last five published questions."""
        return Account.objects.order_by('-pub_date')[:5]


class DetailView(generic.DetailView):
    model = Account
    template_name = 'account/detail.html'
    
def index(request):
    account_list = Account.objects.order_by('+name')[:20]
    context = { 'account_list': account_list }
    return render(request, 'accounting/account/index.html', context)

def detail(request, account_id):
    return HttpResponse("You're looking at question %s." % account_id)

def report(request, account_id):
    p = get_object_or_404(Account, pk=account_id)
    try:
        selected_choice = p.choice_set.get(pk=request.POST['choice'])
    except (KeyError, Choice.DoesNotExist):
        # Redisplay the question voting form.
        return render(request, 'accounting/account/detail.html', {
            'account': p,
            'error_message': "You didn't select a choice.",
        })
    else:
        selected_choice.votes += 1
        selected_choice.save()
        # Always return an HttpResponseRedirect after successfully dealing
        # with POST data. This prevents data from being posted twice if a
        # user hits the Back button.
        return HttpResponseRedirect(reverse('polls:results', args=(p.id,)))