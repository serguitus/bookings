from __future__ import unicode_literals
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

# from dateutil.parser import parse

from django.core.mail import EmailMessage
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.template.loader import get_template
from django.urls import reverse
from django.views import View

from booking.common_site import (
    QuoteSiteModel,
    BookingAllotmentSiteModel,
    BookingTransferSiteModel,
    BookingExtraSiteModel,
    BookingPackageSiteModel
)
from booking.constants import ACTIONS
from booking.models import (
    Package,
    Quote,
    Booking, BookingService,
    BookingPax, BookingServicePax,
    BookingAllotment, BookingTransfer, BookingExtra, BookingPackage
)
from booking.forms import EmailProviderForm
from booking.services import BookingServices

from common.views import ModelChangeFormProcessorView

from config.constants import (
    SERVICE_CATEGORY_ALLOTMENT, SERVICE_CATEGORY_TRANSFER,
    SERVICE_CATEGORY_EXTRA
)
from config.models import Service, Allotment, Place, Schedule, Transfer
from config.services import ConfigServices

from finance.models import Provider, Office

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

        package_list = inlines[4]

        if (
                (not allotment_list) and
                (not transfer_list) and
                (not extra_list) and
                (not package_list)):
            return JsonResponse({
                'code': 3,
                'message': 'Services Missing',
                'results': None,
            })

        code, message, results = BookingServices.find_quote_amounts(
            quote.agency, variant_list, allotment_list, transfer_list, extra_list, package_list)

        return JsonResponse({
            'code': code,
            'message': message,
            'results': results,
        })


class BookingAllotmentAmountsView(ModelChangeFormProcessorView):
    model = BookingAllotment
    common_sitemodel = BookingAllotmentSiteModel
    common_site = bookings_site

    def process_data(self, bookingallotment, inlines):
        if not bookingallotment.booking:
            return JsonResponse({
                'code': 3,
                'message': 'Booking Id Missing',
                'cost': None,
                'cost_message': 'Booking Id Missing',
                'price': None,
                'price_message': 'Booking Id Missing',
            })
        if not bookingallotment.service:
            return JsonResponse({
                'code': 3,
                'message': 'Service Id Missing',
                'cost': None,
                'cost_message': 'Service Id Missing',
                'price': None,
                'price_message': 'Service Id Missing',
            })
        pax_list = inlines[0]
        if not pax_list:
            return JsonResponse({
                'code': 3,
                'message': 'Paxes Missing',
                'cost': None,
                'cost_message': 'Paxes Missing',
                'price': None,
                'price_message': 'Paxes Missing',
            })
        service = bookingallotment.service
        cost_groups = BookingServices.find_paxes_groups(pax_list, service, True)
        price_groups = BookingServices.find_paxes_groups(pax_list, service, False)
        date_from = bookingallotment.datetime_from
        date_to = bookingallotment.datetime_to

        board_type = bookingallotment.board_type
        if board_type is None or board_type == '':
            return JsonResponse({
                'code': 3,
                'message': 'Board Missing',
                'cost': None,
                'cost_message': 'Board Missing',
                'price': None,
                'price_message': 'Board Missing',
            })
        room_type_id = bookingallotment.room_type_id
        if room_type_id is None or room_type_id == '':
            return JsonResponse({
                'code': 3,
                'message': 'Room Missing',
                'cost': None,
                'cost_message': 'Room Missing',
                'price': None,
                'price_message': 'Room Missing',
            })

        code, message, cost, cost_msg, price, price_msg = ConfigServices.allotment_amounts(
            bookingallotment.service_id, date_from, date_to, cost_groups, price_groups,
            bookingallotment.provider, bookingallotment.booking.agency,
            board_type, room_type_id,
        )
        return JsonResponse({
            'code': code,
            'message': message,
            'cost': cost,
            'cost_message': cost_msg,
            'price': price,
            'price_message': price_msg,
        })


class BookingTransferAmountsView(ModelChangeFormProcessorView):
    model = BookingTransfer
    common_sitemodel = BookingTransferSiteModel
    common_site = bookings_site

    def process_data(self, bookingtransfer, inlines):
        if not bookingtransfer.booking:
            return JsonResponse({
                'code': 3,
                'message': 'Booking Id Missing',
                'cost': None,
                'cost_message': 'Booking Id Missing',
                'price': None,
                'price_message': 'Booking Id Missing',
            })
        if not bookingtransfer.service:
            return JsonResponse({
                'code': 3,
                'message': 'Service Id Missing',
                'cost': None,
                'cost_message': 'Service Id Missing',
                'price': None,
                'price_message': 'Service Id Missing',
            })
        pax_list = inlines[0]
        if not pax_list:
            return JsonResponse({
                'code': 3,
                'message': 'Paxes Missing',
                'cost': None,
                'cost_message': 'Paxes Missing',
                'price': None,
                'price_message': 'Paxes Missing',
            })
        service = bookingtransfer.service
        cost_groups = BookingServices.find_paxes_groups(pax_list, service, True)
        price_groups = BookingServices.find_paxes_groups(pax_list, service, False)
        date_from = bookingtransfer.datetime_from
        date_to = bookingtransfer.datetime_to

        location_from_id = bookingtransfer.location_from
        if location_from_id is None or location_from_id == '':
            return JsonResponse({
                'code': 3,
                'message': 'Location From Missing',
                'cost': None,
                'cost_message': 'Location From Missing',
                'price': None,
                'price_message': 'Location From Missing',
            })
        location_to_id = bookingtransfer.location_to
        if location_to_id is None or location_to_id == '':
            return JsonResponse({
                'code': 3,
                'message': 'Location To Missing',
                'cost': None,
                'cost_message': 'Location To Missing',
                'price': None,
                'price_message': 'Location To Missing',
            })

        code, message, cost, cost_msg, price, price_msg = ConfigServices.transfer_amounts(
            bookingtransfer.service_id, date_from, date_to, cost_groups, price_groups,
            bookingtransfer.provider, bookingtransfer.booking.agency,
            location_from_id, location_to_id,
        )
        return JsonResponse({
            'code': code,
            'message': message,
            'cost': cost,
            'cost_message': cost_msg,
            'price': price,
            'price_message': price_msg,
        })


class BookingExtraAmountsView(ModelChangeFormProcessorView):
    model = BookingExtra
    common_sitemodel = BookingExtraSiteModel
    common_site = bookings_site

    def process_data(self, bookingextra, inlines):
        if not bookingextra.booking:
            return JsonResponse({
                'code': 3,
                'message': 'Booking Id Missing',
                'cost': None,
                'cost_message': 'Booking Id Missing',
                'price': None,
                'price_message': 'Booking Id Missing',
            })
        if not bookingextra.service:
            return JsonResponse({
                'code': 3,
                'message': 'Service Id Missing',
                'cost': None,
                'cost_message': 'Service Id Missing',
                'price': None,
                'price_message': 'Service Id Missing',
            })
        pax_list = inlines[0]
        if not pax_list:
            return JsonResponse({
                'code': 3,
                'message': 'Paxes Missing',
                'cost': None,
                'cost_message': 'Paxes Missing',
                'price': None,
                'price_message': 'Paxes Missing',
            })
        service = bookingextra.service
        cost_groups = BookingServices.find_paxes_groups(pax_list, service, True)
        price_groups = BookingServices.find_paxes_groups(pax_list, service, False)
        date_from = bookingextra.datetime_from
        date_to = bookingextra.datetime_to

        addon_id = bookingextra.addon
        if addon_id == '':
            addon_id = None
        quantity = int(bookingextra.quantity)
        parameter = int(bookingextra.parameter)

        code, message, cost, cost_msg, price, price_msg = ConfigServices.extra_amounts(
            bookingextra.service_id, date_from, date_to, cost_groups, price_groups,
            bookingextra.provider, bookingextra.booking.agency,
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


class BookingPackageAmountsView(ModelChangeFormProcessorView):
    model = BookingPackage
    common_sitemodel = BookingPackageSiteModel
    common_site = bookings_site

    def process_data(self, bookingpackage, inlines):
        if not bookingpackage.booking:
            return JsonResponse({
                'code': 3,
                'message': 'Booking Id Missing',
                'cost': None,
                'cost_message': 'Booking Id Missing',
                'price': None,
                'price_message': 'Booking Id Missing',
            })
        if not bookingpackage.service:
            return JsonResponse({
                'code': 3,
                'message': 'Service Id Missing',
                'cost': None,
                'cost_message': 'Service Id Missing',
                'price': None,
                'price_message': 'Service Id Missing',
            })
        pax_list = inlines[0]
        if not pax_list:
            return JsonResponse({
                'code': 3,
                'message': 'Paxes Missing',
                'cost': None,
                'cost_message': 'Paxes Missing',
                'price': None,
                'price_message': 'Paxes Missing',
            })
        allotment_list = inlines[1]
        transfer_list = inlines[2]
        extra_list = inlines[3]
        service = bookingpackage.service
        cost_groups = BookingServices.find_paxes_groups(pax_list, service, True)
        price_groups = BookingServices.find_paxes_groups(pax_list, service, False)
        date_from = bookingpackage.datetime_from
        date_to = bookingpackage.datetime_to

        code, message, cost, cost_msg, price, price_msg = BookingServices.bookingpackage_amounts(
            bookingpackage.service_id, date_from, date_to, cost_groups, price_groups,
            bookingpackage.provider, bookingpackage.booking.agency,
            allotment_list, transfer_list, extra_list,
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

        pickup_time, pickup_time_msg = ConfigServices.transfer_time(
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
    template = get_template("booking/pdf/invoice.html")
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


def build_voucher(request, id):
    template = get_template("booking/pdf/voucher.html")
    booking = Booking.objects.get(id=id)
    context = {'pagesize': 'Letter',
               'booking': booking,
               'office': Office.objects.get(id=1),
               'services': [2, 1],}
    # html = template.render(context)
    # result = StringIO.StringIO()
    # pdf = pisa.pisaDocument(StringIO.StringIO(html), dest=result)
    # if not pdf.err:
    #     return HttpResponse(result.getvalue(), content_type='application/pdf')
    # else:
    #     return HttpResponse('Errors')
    return render(request, 'booking/pdf/voucher.html', context)


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
        subject, body, from_address, to_address,
        cc_address, bcc_address, reply_address):
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


def booking_actions(request, id):
    """
    This works as an entry point for any actions defined at the
    booking details view. There is one option for every defined action
    This view will redirect to the corresponding action view. All actions
    end redirecting to referer
    """
    from common_site import BookingSiteModel
    action = request.POST.get('action-selector', None)
    if action:
        items = request.POST.get('pk', None)
        return getattr(ACTIONS, action)(request, items)
    # here show some error message for unknown action
    return redirect(reverse('common:booking_booking_change',
                                        args=(id,)))


class PackageAutocompleteView(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        # Don't forget to filter out results depending on the visitor !
        if not self.request.user.is_authenticated():
            return Package.objects.none()
        qs = Package.objects.filter(enabled=True).all()
        if self.q:
            qs = qs.filter(name__icontains=self.q)
        return qs[:20]


class ProviderPackageAutocompleteView(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        if not self.request.user.is_authenticated():
            return Provider.objects.none()
        qs = Provider.objects.filter(enabled=True).all().distinct()

        service = self.forwarded.get('service', None)

        if service:
            qs = qs.filter(
                providerpackageservice__service=service,
            )

        if self.q:
            qs = qs.filter(name__icontains=self.q)
        return qs[:20]
