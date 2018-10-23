from django.http import JsonResponse
from django.shortcuts import render
from django.views import View

from booking.models import BookingService, BookingServicePax

from config.constants import (
    SERVICE_CATEGORY_ALLOTMENT, SERVICE_CATEGORY_TRANSFER, SERVICE_CATEGORY_EXTRA
)
from config.models import Service
from config.services import ConfigService

from finance.models import Provider

class BookingServiceAmountsView(View):
    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        booking_service_id = request.post.get('booking_service_id')
        service_id = request.post.get('service_id')
        date_from = request.post.get('date_from')
        date_to = request.post.get('date_to')
        provider_id = request.post.get('provider_id')

        service = Service.objects.get(pk=service_id)
        service_type = service.service_type

        provider = Provider.objects.get(pk=provider_id)

        booking_service = BookingService.objects.get(pk=booking_service_id)
        agency = booking_service.booking.agency

        adults, children = self.findPaxes(booking_service, service)

        if service_type == SERVICE_CATEGORY_ALLOTMENT:
            board_type = request.post.get('board_type')
            room_type_id = request.post.get('room_type_id')

            code, message, cost, price = ConfigService.allotment_amounts(
                service_id, date_from, date_to, adults, children, provider, agency,
                board_type, room_type_id,
            )
        if service_type == SERVICE_CATEGORY_TRANSFER:
            location_from_id = request.post.get('location_from_id')
            location_to_id = request.post.get('location_to_id')

            code, message, cost, price = ConfigService.transfer_amounts(
                service_id, date_from, date_to, adults, children, provider, agency,
                location_from_id, location_to_id,
            )
        if service_type == SERVICE_CATEGORY_EXTRA:
            quantity = request.post.get('quantity')
            parameter = request.post.get('parameter')

            code, message, cost, price = ConfigService.extra_amounts(
                service_id, date_from, date_to, adults, children, provider, agency,
                quantity, parameter,
            )
        return JsonResponse({
            'code': code,
            'message': message,
            'cost': cost,
            'price': price,
        })

        def findPaxes(self, booking_service, service):
            pax_list = list(
                BookingServicePax.objects.filter(booking_service=booking_service.id))
            if service.child_age is None:
                return len(pax_list), 0
            adults = 0
            children = 0
            for pax in pax_list:
                if pax.pax_age > service.child_age:
                    adults += 1
                else:
                    children +=1
            return adults, children


def booking_list(request, instance):
    """ a list of bookings with their services """
    context = {}
    context.update(instance.get_model_extra_context(request))
    return render(request, 'booking/booking_list.html', context)
