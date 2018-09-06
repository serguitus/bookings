from django.shortcuts import render

# Create your views here.

def booking_list(request, instance):
    """ a list of bookings with their services """
    context = {}
    context.update(instance.get_model_extra_context(request))
    return render(request, 'booking/booking_list.html', context)
