from django.contrib import messages
from django.db.models import Q
from django.forms.formsets import all_valid, DELETION_FIELD_NAME
from django.http import JsonResponse, HttpResponse

try:
    import cStringIO as StringIO
except ImportError:
    from io import StringIO

from xhtml2pdf import pisa

from dal import autocomplete

from dateutil.parser import parse

from django.core.mail import EmailMessage
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.template.loader import get_template
from django.urls import reverse
from django.views import View

from booking.common_site import QuoteSiteModel
from booking.models import (
    Quote,
    Booking, BookingService)
from booking.forms import EmailProviderForm
from booking.services import BookingService as Booking_Service
from reservas.admin import bookings_site
from common.views import ModelChangeFormProcessorView

from booking.models import BookingPax, BookingServicePax

from config.constants import (
    SERVICE_CATEGORY_ALLOTMENT, SERVICE_CATEGORY_TRANSFER, SERVICE_CATEGORY_EXTRA
)
from config.models import Service, Allotment, Place, Schedule, Transfer
from config.services import ConfigService

from finance.models import Provider

from reservas.admin import bookings_site


class BookingPaxAutocompleteView(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        if not self.request.user.is_authenticated():
            return BookingPax.objects.none()
        qs = BookingPax.objects.all()

        booking = self.forwarded.get('booking', None)
        booking_service = self.forwarded.get('booking_service', None)

        values = list()
        if booking_service:
            values = BookingServicePax.objects.filter(
                booking_service=booking_service).values_list('booking_pax', flat=True)

        if booking:
            if values:
                qs = qs.exclude(id__in=list(values))

            qs = qs.filter(
                booking=booking,
            )

        if self.q:
            qs = qs.filter(pax_name__icontains=self.q)
        return qs[:20]


class QuoteAmountsView(ModelChangeFormProcessorView):

    model = Quote
    common_sitemodel = QuoteSiteModel
    common_site = bookings_site

    def process_data(self, quote, inlines):

        variant_list = inlines[0]
        if not variant_list:
            return JsonResponse({
                'code': 3,
                'message': 'Pax Variants Missing',
                'results': None,
            })

        allotment_list = inlines[1]

        transfer_list = inlines[2]

        extra_list = inlines[3]

        if (not allotment_list) and (not transfer_list) and (not extra_list):
            return JsonResponse({
                'code': 3,
                'message': 'Services Missing',
                'results': None,
            })

        code, message, results = Booking_Service.find_quote_amounts(
            quote.agency, variant_list, allotment_list, transfer_list, extra_list)

        return JsonResponse({
            'code': code,
            'message': message,
            'results': results,
        })


class BookingServiceAmountsView(ModelChangeFormProcessorView):
    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        service_id = request.POST.get('service')
        if service_id is None or service_id == '':
            return JsonResponse({
                'code': 3,
                'message': 'Service Id Missing',
                'cost': None,
                'cost_message': 'Service Id Missing',
                'price': None,
                'price_message': 'Service Id Missing',
            })
        try:
            service = Service.objects.get(pk=service_id)
        except Service.DoesNotExist as ex:
            return JsonResponse({
                'code': 3,
                'message': 'Service Not Found for Id: %s' % service_id,
                'cost': None,
                'cost_message': 'Service Not Found for Id: %s' % service_id,
                'price': None,
                'price_message': 'Service Not Found for Id: %s' % service_id,
            })
        service_type = service.category

        date_from = request.POST.get('datetime_from', None)
        if date_from is None or date_from == '':
            return JsonResponse({
                'code': 3,
                'message': 'Date From Missing',
                'cost': None,
                'cost_message': 'Date From Missing',
                'price': None,
                'price_message': 'Date From Missing',
            })
        date_from = parse(date_from).date()

        date_to = request.POST.get('datetime_to', None)
        if date_to is None or date_to == '':
            return JsonResponse({
                'code': 3,
                'message': 'Date To Missing',
                'cost': None,
                'cost_message': 'Date To Missing',
                'price': None,
                'price_message': 'Date To Missing',
            })
        date_to = parse(date_to).date()

        booking_service_id = request.POST.get('id')
        try:
            booking_service = BookingService.objects.get(pk=booking_service_id)
        except BookingService.DoesNotExist as ex:
            booking_service = None

        groups = Booking_Service.find_groups(booking_service, service)
        if groups is None:
            return JsonResponse({
                'code': 3,
                'message': 'Paxes Missing',
                'cost': None,
                'cost_message': 'Paxes Missing',
                'price': None,
                'price_message': 'Paxes Missing',
            })

        provider_id = request.POST.get('provider')
        try:
            provider = Provider.objects.get(pk=provider_id)
        except Provider.DoesNotExist as ex:
            provider = None

        agency = None
        booking_id = request.POST.get('booking')
        if not (booking_id is None or booking_id == ''):
            try:
                booking = Booking.objects.get(pk=booking_id)
                agency = booking.agency
            except Booking.DoesNotExist as ex:
                booking = None

        if service_type == SERVICE_CATEGORY_ALLOTMENT:
            board_type = request.POST.get('board_type')
            if board_type is None or board_type == '':
                return JsonResponse({
                    'code': 3,
                    'message': 'Board Missing',
                    'cost': None,
                    'cost_message': 'Board Missing',
                    'price': None,
                    'price_message': 'Board Missing',
                })
            room_type_id = request.POST.get('room_type')
            if room_type_id is None or room_type_id == '':
                return JsonResponse({
                    'code': 3,
                    'message': 'Room Missing',
                    'cost': None,
                    'cost_message': 'Room Missing',
                    'price': None,
                    'price_message': 'Room Missing',
                })

            code, message, cost, cost_msg, price, price_msg = ConfigService.allotment_amounts(
                service_id, date_from, date_to, groups, provider, agency,
                board_type, room_type_id,
            )

        if service_type == SERVICE_CATEGORY_TRANSFER:
            location_from_id = request.POST.get('location_from')
            if location_from_id is None or location_from_id == '':
                return JsonResponse({
                    'code': 3,
                    'message': 'Location From Missing',
                    'cost': None,
                    'cost_message': 'Location From Missing',
                    'price': None,
                    'price_message': 'Location From Missing',
                })
            location_to_id = request.POST.get('location_to')
            if location_to_id is None or location_to_id == '':
                return JsonResponse({
                    'code': 3,
                    'message': 'Location To Missing',
                    'cost': None,
                    'cost_message': 'Location To Missing',
                    'price': None,
                    'price_message': 'Location To Missing',
                })

            code, message, cost, cost_msg, price, price_msg = ConfigService.transfer_amounts(
                service_id, date_from, date_to, groups, provider, agency,
                location_from_id, location_to_id,
            )


        if service_type == SERVICE_CATEGORY_EXTRA:
            addon_id = request.POST.get('addon')
            if addon_id == '':
                addon_id = None
            quantity = int(request.POST.get('quantity'))
            parameter = int(request.POST.get('parameter'))

            code, message, cost, cost_msg, price, price_msg = ConfigService.extra_amounts(
                service_id, date_from, date_to, groups, provider, agency,
                addon_id, quantity, parameter,
            )
        return JsonResponse({
            'code': code,
            'message': message,
            'cost': cost,
            'cost_message': cost_msg,
            'price': price,
            'price_message': price_msg,
        })


class BookingTransferTimeView(ModelChangeFormProcessorView):
    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):

        schedule_from_id = request.POST.get('schedule_from')
        schedule_to_id = request.POST.get('schedule_to')
        location_from_id = request.POST.get('location_from')
        location_to_id = request.POST.get('location_to')

        pickup_time, pickup_time_msg = ConfigService.transfer_time(
                schedule_from_id, schedule_to_id, location_from_id, location_to_id)

        return JsonResponse({
            'time': pickup_time,
            'time_message': pickup_time_msg,
        })


def booking_list(request, instance):
    """ a list of bookings with their services """
    context = {}
    context.update(instance.get_model_extra_context(request))
    return render(request, 'booking/booking_list.html', context)


def get_invoice(request, id):
    template = get_template("booking/invoice.html")
    booking = Booking.objects.get(id=id)
    context = {'pagesize': 'Letter',
               'booking': booking,}
    html = template.render(context)
    result = StringIO.StringIO()
    pdf = pisa.pisaDocument(StringIO.StringIO(html), dest=result)
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    else:
        return HttpResponse('Errors')


class EmailProviderView(View):
    """
    A view to handle the email that will be sent to providers
    It allows to customice the default email
    """

    def get(self, request, id, *args, **kwargs):
        """
        This will render the default email for certain provider
        allowing it to be customiced
        """
        bs = BookingService.objects.get(id=id)
        services = BookingService.objects.filter(
            booking=bs.booking,
            provider=bs.provider)
        provider_name = ''
        if bs.provider:
            provider_name = bs.provider.name
        rooming = bs.rooming_list.all()
        initial = {
            'services': services,
            'provider': provider_name,
            'rooming': rooming,
            'user': request.user,
        }
        t = get_template('booking/emails/provider_email.html')
        form = EmailProviderForm(request.user,
                                 initial={
                                     'subject': 'Solicitud de Confirmacion',
                                     'body': t.render(initial)
                                 })
        context = dict()
        context.update(bookings_site.get_site_extra_context(request))
        request.current_app = bookings_site.name
        context.update({'form': form})
        return render(request, 'booking/email_provider_form.html', context)

    def post(self, request, id, *args, **kwargs):
        booking_service = BookingService.objects.get(id=id)
        from_address = request.POST.get('from_address')
        to_address = request.POST.get('to_address')
        cc_address = request.POST.get('cc_address')
        bcc_address = request.POST.get('bcc_address')
        subject = request.POST.get('subject')
        body = request.POST.get('body')

        _send_service_request(
            subject, body, from_address, to_address, cc_address, bcc_address, from_address)
        messages.add_message(
            request=request, level=messages.SUCCESS,
            message='Email  sent successfully.',
            extra_tags='', fail_silently=False)
        return HttpResponseRedirect(
            reverse('common:booking_booking_change', args=(booking_service.booking.id,)))


def _send_service_request(
        subject, body, from_address, to_address, cc_address, bcc_address, reply_address):
    """
    This helper sends emails
    """
    email = EmailMessage(
        subject=subject,
        body=body,
        from_email=from_address,
        to=_find_address_list(to_address),
        cc=_find_address_list(cc_address),
        bcc=_find_address_list(bcc_address),
        reply_to=_find_address_list(reply_address))
    email.send()

def _find_address_list(str_address=''):
    address_list = list()
    if str_address:
        comma_addresses = str_address.split(',')
        for comma_address in comma_addresses:
            if comma_address:
                split_addresses = comma_address.split(';')
                for split_address in split_addresses:
                    if split_address:
                        address_list.append(split_address)
    return address_list


class PickUpAutocompleteView(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        # Don't forget to filter out results depending on the visitor !
        if not self.request.user.is_authenticated():
            return Allotment.objects.none()
        qs = Allotment.objects.filter(enabled=True).all()

        location = self.forwarded.get('location_from', None)
        if location:
            qs = qs.filter(location=location)

        service = self.forwarded.get('service', None)
        if service:
            transfer = Transfer.objects.get(pk=service)
            if transfer.is_shared:
                qs = qs.filter(is_shared_point=True)

        if self.q:
            qs = qs.filter(name__icontains=self.q)
        return qs[:20]


class DropOffAutocompleteView(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        # Don't forget to filter out results depending on the visitor !
        if not self.request.user.is_authenticated():
            return Allotment.objects.none()
        qs = Allotment.objects.filter(enabled=True).all()

        location = self.forwarded.get('location_to', None)
        if location:
            qs = qs.filter(location=location)

        service = self.forwarded.get('service', None)
        if service:
            transfer = Transfer.objects.get(pk=service)
            if transfer.is_shared:
                qs = qs.filter(is_shared_point=True)

        if self.q:
            qs = qs.filter(name__icontains=self.q)
        return qs[:20]


class PlaceAutocompleteView(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        # Don't forget to filter out results depending on the visitor !
        if not self.request.user.is_authenticated():
            return Place.objects.none()
        qs = Place.objects.all()

        location_from = self.forwarded.get('location_from', None)
        location_to = self.forwarded.get('location_to', None)

        if location_from:
            qs = qs.filter(
                location=location_from,
            )
        if location_to:
            qs = qs.filter(
                location=location_to,
            )

        if self.q:
            qs = qs.filter(name__icontains=self.q)
        return qs[:20]


class ScheduleArrivalAutocompleteView(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        # Don't forget to filter out results depending on the visitor !
        if not self.request.user.is_authenticated():
            return Schedule.objects.none()
        qs = Schedule.objects.filter(is_arrival=True).all()

        location = self.forwarded.get('location_from', None)

        if location:
            qs = qs.filter(
                location=location,
            )

        if self.q:
            qs = qs.filter(name__icontains=self.q)
        return qs[:20]


class ScheduleDepartureAutocompleteView(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        # Don't forget to filter out results depending on the visitor !
        if not self.request.user.is_authenticated():
            return Schedule.objects.none()
        qs = Schedule.objects.filter(is_arrival=False).all()

        location = self.forwarded.get('location_to', None)

        if location:
            qs = qs.filter(
                location=location,
            )

        if self.q:
            qs = qs.filter(name__icontains=self.q)
        return qs[:20]
