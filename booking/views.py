from django.http import JsonResponse
from django.shortcuts import render
from django.views import View

from dateutil.parser import parse

from booking.models import Booking, BookingService, BookingServicePax

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
        service_id = request.POST.get('service')
        if service_id is None or service_id == '':
            return JsonResponse({
                'code': 3,
                'message': 'Service Id Missing',
                'cost': None,
                'price': None,
            })
        try:
            service = Service.objects.get(pk=service_id)
        except Service.DoesNotExist as ex:
            return JsonResponse({
                'code': 3,
                'message': 'Service Not Found for Id: %s' % service_id,
                'cost': None,
                'price': None,
            })
        service_type = service.category

        date_from = request.POST.get('datetime_from_0', None)
        if date_from is None or date_from == '':
            return JsonResponse({
                'code': 3,
                'message': 'Date From Missing',
                'cost': None,
                'price': None,
            })
        date_from = parse(date_from)

        date_to = request.POST.get('datetime_to_0', None)
        if date_to is None or date_to == '':
            return JsonResponse({
                'code': 3,
                'message': 'Date To Missing',
                'cost': None,
                'price': None,
            })
        date_to = parse(date_to)

        provider_id = request.POST.get('provider_id')
        try:
            provider = Provider.objects.get(pk=provider_id)
        except Provider.DoesNotExist as ex:
            provider = None

        booking_id = request.POST.get('booking')
        if booking_id is None or booking_id == '':
            return JsonResponse({
                'code': 3,
                'message': 'Booking Id Missing',
                'cost': None,
                'price': None,
            })
        
        try:
            booking = Booking.objects.get(pk=booking_id)
        except Booking.DoesNotExist as ex:
            booking_service = None
        agency = booking.agency

        booking_service_id = request.POST.get('booking_service')
        try:
            booking_service = BookingService.objects.get(pk=booking_service_id)
        except BookingService.DoesNotExist as ex:
            booking_service = None

        adults, children = self.find_paxes(booking_service, service)

        if service_type == SERVICE_CATEGORY_ALLOTMENT:
            if adults is None or children is None:
                return JsonResponse({
                    'code': 3,
                    'message': 'Paxes Missing',
                    'cost': None,
                    'price': None,
                })
                
            else:
                board_type = request.POST.get('board_type')
                if board_type is None or board_type == '':
                    return JsonResponse({
                        'code': 3,
                        'message': 'Board Missing',
                        'cost': None,
                        'price': None,
                    })
                room_type_id = request.POST.get('room_type')
                if room_type_id is None or room_type_id == '':
                    return JsonResponse({
                        'code': 3,
                        'message': 'Room Missing',
                        'cost': None,
                        'price': None,
                    })

                code, message, cost, price = ConfigService.allotment_amounts(
                    service_id, date_from, date_to, adults, children, provider, agency,
                    board_type, room_type_id,
                )
                
        if service_type == SERVICE_CATEGORY_TRANSFER:
            location_from_id = request.POST.get('location_from_id')
            if location_from_id is None or location_from_id == '':
                return JsonResponse({
                    'code': 3,
                    'message': 'Location From Missing',
                    'cost': None,
                    'price': None,
                })
            location_to_id = request.POST.get('location_to_id')
            if location_to_id is None or location_to_id == '':
                return JsonResponse({
                    'code': 3,
                    'message': 'Location To Missing',
                    'cost': None,
                    'price': None,
                })

            code, message, cost, price = ConfigService.transfer_amounts(
                service_id, date_from, date_to, adults, children, provider, agency,
                location_from_id, location_to_id,
            )
        if service_type == SERVICE_CATEGORY_EXTRA:
            quantity = request.POST.get('quantity')
            parameter = request.POST.get('parameter')

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

    def find_paxes(self, booking_service, service):
        if booking_service is None:
            return None, None
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
                children += 1
        return adults, children


def booking_list(request, instance):
    """ a list of bookings with their services """
    context = {}
    context.update(instance.get_model_extra_context(request))
    return render(request, 'booking/booking_list.html', context)
