# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.models import User
from django.db.models import Q
from django.forms.formsets import all_valid, DELETION_FIELD_NAME
from django.http import JsonResponse, HttpResponse

try:
    from cStringIO import StringIO
except ImportError:
    from _io import BytesIO as StringIO

from xhtml2pdf import pisa

from dal import autocomplete
from urllib.parse import urlencode
# from dateutil.parser import parse

from django.core.exceptions import ValidationError
from django.core.mail import EmailMessage
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.template.loader import get_template
from django.urls import reverse
from django.utils.six import PY2
from django.views import View

from booking.common_site import (
    QuoteSiteModel,
    NewQuoteAllotmentSiteModel, NewQuoteTransferSiteModel,
    NewQuoteExtraSiteModel, QuoteExtraPackageSiteModel,
    BookingSiteModel,
    BookingProvidedAllotmentSiteModel, BookingProvidedTransferSiteModel,
    BookingProvidedExtraSiteModel,
    BookingExtraPackageSiteModel,
    BookingBookDetailAllotmentSiteModel, BookingBookDetailTransferSiteModel,
    BookingBookDetailExtraSiteModel,
    default_requests_mail_from, default_requests_mail_to,
    default_requests_mail_bcc, default_requests_mail_subject,
    default_requests_mail_body, default_mail_cc
)
from booking.constants import (
    ACTIONS, SERVICE_STATUS_CANCELLED,
    BASE_BOOKING_SERVICE_CATEGORY_BOOKING_ALLOTMENT,
    BASE_BOOKING_SERVICE_CATEGORY_BOOKING_TRANSFER,
    BASE_BOOKING_SERVICE_CATEGORY_BOOKING_EXTRA,
    BASE_BOOKING_SERVICE_CATEGORY_BOOKING_PACKAGE,
    BASE_BOOKING_SERVICE_CATEGORY_BOOKING_PACKAGE_ALLOTMENT,
    BASE_BOOKING_SERVICE_CATEGORY_BOOKING_PACKAGE_TRANSFER,
    BASE_BOOKING_SERVICE_CATEGORY_BOOKING_PACKAGE_EXTRA,

)
from booking.models import (
    Quote, QuotePaxVariant, QuoteService,
    NewQuoteAllotment, NewQuoteTransfer, NewQuoteExtra, QuoteExtraPackage,
    Booking, BaseBookingService, BookingProvidedService,
    BookingPax, BaseBookingServicePax,
    BookingProvidedAllotment, BookingProvidedTransfer, BookingProvidedExtra, BookingExtraPackage,
    BookingBookDetailAllotment, BookingBookDetailTransfer, BookingBookDetailExtra,
    BookingInvoice, BookingInvoiceDetail, BookingInvoiceLine, BookingInvoicePartial,
    get_bookingservice_objects,
)
from booking.forms import EmailProviderForm
from booking.services import BookingServices

from common.views import ModelChangeFormProcessorView

from config.constants import (
    SERVICE_CATEGORY_ALLOTMENT, SERVICE_CATEGORY_TRANSFER,
    SERVICE_CATEGORY_EXTRA
)
from config.models import (
    Service, Allotment, Place, Schedule, Transfer, Extra,
    ProviderAllotmentService, ProviderTransferService, ProviderExtraService,
)

from config.services import ConfigServices

from finance.models import Provider, Office

from reservas.admin import bookings_site
from reservas.custom_settings import ADDON_FOR_NO_ADDON


class BookingPaxAutocompleteView(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return BookingPax.objects.none()
        qs = BookingPax.objects.all()

        booking = self.forwarded.get('booking', None)
        booking_service = self.forwarded.get('booking_service', None)

        values = list()
        if booking_service:
            values = BaseBookingServicePax.objects.filter(
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

        code, message, results = BookingServices.find_quote_amounts(
            quote, variant_list)

        return JsonResponse({
            'code': code,
            'message': message,
            'results': results,
        })


class NewQuoteAllotmentAmountsView(ModelChangeFormProcessorView):

    model = NewQuoteAllotment
    common_sitemodel = NewQuoteAllotmentSiteModel
    common_site = bookings_site

    def process_data(self, quoteallotment, inlines):

        variant_list = inlines[0]
        if not variant_list:
            return JsonResponse({
                'code': 3,
                'message': 'Pax Variants Missing',
                'results': None,
            })

        code, message, results = BookingServices.find_quoteservice_amounts(
            quoteallotment, variant_list)

        return JsonResponse({
            'code': code,
            'message': message,
            'results': results,
        })


class NewQuoteTransferAmountsView(ModelChangeFormProcessorView):

    model = NewQuoteTransfer
    common_sitemodel = NewQuoteTransferSiteModel
    common_site = bookings_site

    def process_data(self, quotetransfer, inlines):

        variant_list = inlines[0]
        if not variant_list:
            return JsonResponse({
                'code': 3,
                'message': 'Pax Variants Missing',
                'results': None,
            })

        code, message, results = BookingServices.find_quoteservice_amounts(
            quotetransfer, variant_list)

        return JsonResponse({
            'code': code,
            'message': message,
            'results': results,
        })


class NewQuoteExtraAmountsView(ModelChangeFormProcessorView):

    model = NewQuoteExtra
    common_sitemodel = NewQuoteExtraSiteModel
    common_site = bookings_site

    def process_data(self, quoteextra, inlines):

        variant_list = inlines[0]
        if not variant_list:
            return JsonResponse({
                'code': 3,
                'message': 'Pax Variants Missing',
                'results': None,
            })

        code, message, results = BookingServices.find_quoteservice_amounts(
            quoteextra, variant_list)

        return JsonResponse({
            'code': code,
            'message': message,
            'results': results,
        })


class QuoteExtraPackageAmountsView(ModelChangeFormProcessorView):

    model = QuoteExtraPackage
    common_sitemodel = QuoteExtraPackageSiteModel
    common_site = bookings_site

    def process_data(self, quotepackage, inlines):

        variant_list = inlines[0]
        if not variant_list:
            return JsonResponse({
                'code': 3,
                'message': 'Pax Variants Missing',
                'results': None,
            })

        code, message, results = BookingServices.find_quoteservice_amounts(
            quotepackage, variant_list)

        return JsonResponse({
            'code': code,
            'message': message,
            'results': results,
        })


class BookingAmountsView(ModelChangeFormProcessorView):

    model = Booking
    common_sitemodel = BookingSiteModel
    common_site = bookings_site

    def process_data(self, booking, inlines):

        pax_list = inlines[0]
        cost, cost_msg, price, price_msg = BookingServices.find_booking_amounts(booking, pax_list)
        return JsonResponse({
            'cost': cost,
            'cost_message': cost_msg,
            'price': price,
            'price_message': price_msg,
        })


class BookingServiceAmountsView(ModelChangeFormProcessorView):
    common_site = bookings_site

    def verify(self, bookingservice, inlines):
        if not hasattr(bookingservice, 'booking') or not bookingservice.booking:
            return JsonResponse({
                'cost': None,
                'cost_message': 'Booking Id Missing',
                'price': None,
                'price_message': 'Booking Id Missing',
            }), None
        if not hasattr(bookingservice, 'service') or not bookingservice.service:
            return JsonResponse({
                'cost': None,
                'cost_message': 'Service Id Missing',
                'price': None,
                'price_message': 'Service Id Missing',
            }), None
        if hasattr(bookingservice, 'booking_package_id') and bookingservice.booking_package_id is not None:
            pax_list = list(BaseBookingServicePax.objects.filter(
                booking_service=bookingservice.booking_package_id).all())
            if not pax_list:
                return JsonResponse({
                    'cost': None,
                    'cost_message': 'Empty rooming',
                    'price': None,
                    'price_message': 'Empty rooming',
                }), pax_list
        else:
            pax_list = inlines[0]
            if not pax_list:
                return JsonResponse({
                    'cost': None,
                    'cost_message': 'Empty rooming',
                    'price': None,
                    'price_message': 'Empty rooming',
                }), pax_list

        return None, pax_list

    def process_data(self, bookingservice, inlines):

        response, pax_list = self.verify(bookingservice, inlines)
        if response:
            return response

        cost, cost_msg, price, price_msg = BookingServices.find_bookingservice_amounts(
            bookingservice, pax_list)
        return JsonResponse({
            'cost': cost,
            'cost_message': cost_msg,
            'price': price,
            'price_message': price_msg,
        })


class BookingExtraPackageAmountsView(BookingServiceAmountsView):
    model = BookingExtraPackage
    common_sitemodel = BookingExtraPackageSiteModel


class BookingProvidedAllotmentAmountsView(BookingServiceAmountsView):
    model = BookingProvidedAllotment
    common_sitemodel = BookingProvidedAllotmentSiteModel


class BookingProvidedTransferAmountsView(BookingServiceAmountsView):
    model = BookingProvidedTransfer
    common_sitemodel = BookingProvidedTransferSiteModel


class BookingProvidedExtraAmountsView(BookingServiceAmountsView):
    model = BookingProvidedExtra
    common_sitemodel = BookingProvidedExtraSiteModel


class BookingServiceDetailAmountsView(ModelChangeFormProcessorView):
    common_site = bookings_site

    def verify(self, bookingservicedetail):
        if not hasattr(bookingservicedetail, 'booking_service') or not bookingservicedetail.booking_service:
            return JsonResponse({
                'cost': None,
                'cost_message': 'Booking Service Id Missing',
                'price': None,
                'price_message': 'Booking Service Id Missing',
            }), None
        if not hasattr(bookingservicedetail, 'book_service') or not bookingservicedetail.book_service:
            return JsonResponse({
                'cost': None,
                'cost_message': 'Service Id Missing',
                'price': None,
                'price_message': 'Service Id Missing',
            }), None
        pax_list = list(BaseBookingServicePax.objects.filter(
            booking_service=bookingservicedetail.booking_service_id).all())
        if not pax_list:
            return JsonResponse({
                'cost': None,
                'cost_message': 'Paxes Missing',
                'price': None,
                'price_message': 'Paxes Missing',
            }), pax_list

        return None, pax_list

    def process_data(self, bookingservicedetail, inlines):

        response, pax_list = self.verify(bookingservicedetail)
        if response:
            return response

        cost, cost_msg, price, price_msg = BookingServices.find_bookingservice_amounts(
            bookingservicedetail, pax_list)
        return JsonResponse({
            'cost': cost,
            'cost_message': cost_msg,
            'price': price,
            'price_message': price_msg,
        })


class BookingDetailAllotmentAmountsView(BookingServiceDetailAmountsView):
    model = BookingBookDetailAllotment
    common_sitemodel = BookingBookDetailAllotmentSiteModel


class BookingDetailTransferAmountsView(BookingServiceDetailAmountsView):
    model = BookingBookDetailTransfer
    common_sitemodel = BookingBookDetailTransferSiteModel


class BookingDetailExtraAmountsView(BookingServiceDetailAmountsView):
    model = BookingBookDetailExtra
    common_sitemodel = BookingBookDetailExtraSiteModel


class BookingTransferTimeView(ModelChangeFormProcessorView):
    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):

        transfer_id = request.POST.get('service')
        schedule_from_id = request.POST.get('schedule_from')
        schedule_to_id = request.POST.get('schedule_to')
        location_from_id = request.POST.get('location_from')
        allotment_from_id = request.POST.get('pickup')
        location_to_id = request.POST.get('location_to')
        time_from = request.POST.get('schedule_time_from')
        time_to = request.POST.get('schedule_time_to')

        pickup_time, pickup_time_msg = ConfigServices.transfer_time(
            schedule_from_id, schedule_to_id, location_from_id, location_to_id, time_from, time_to,
            transfer_id, allotment_from_id)

        return JsonResponse({
            'time': pickup_time,
            'time_message': pickup_time_msg,
        })


class BookingTransferScheduleFromView(ModelChangeFormProcessorView):
    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):

        schedule_from_id = request.POST.get('schedule_from')
        if schedule_from_id:
            schedule = Schedule.objects.get(pk=schedule_from_id)
            return JsonResponse({
                'time': schedule.time,
            })
        return JsonResponse({})


class BookingTransferScheduleToView(ModelChangeFormProcessorView):
    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):

        schedule_to_id = request.POST.get('schedule_to')
        if schedule_to_id:
            schedule = Schedule.objects.get(pk=schedule_to_id)
            return JsonResponse({
                'time': schedule.time,
            })
        return JsonResponse({})


def booking_list(request, instance):
    """ a list of bookings with their services """
    context = {}
    context.update(instance.get_model_extra_context(request))
    return render(request, 'booking/booking_list.html', context)

# Just commenting the view below. if system doesn't explotes we are save
# def build_voucher(request, id):
#     # TODO we can probably remove this method and the corresponding URL
#     template = get_template("booking/pdf/voucher.html")
#     booking = Booking.objects.get(id=id)
#     services = BookingService.objects.filter(id__in=[2, 1, 3, 4, 9, 10])
#     objs = get_bookingservice_objects(services)
#     context = {'pagesize': 'Letter',
#                'booking': booking,
#                'office': Office.objects.get(id=1),
#                'services': objs}
#     html = template.render(context)
#     if PY2:
#         html = html.encode('UTF-8')
#     result = StringIO()
#     pdf = pisa.pisaDocument(StringIO(html), dest=result,
#                             link_callback=_fetch_resources)
#     if not pdf.err:
#         return HttpResponse(result.getvalue(),content_type='application/pdf')
#     else:
#         return HttpResponse('Errors')
#     # return render(request, 'booking/pdf/voucher.html', context)


# helper method for build_voucher view.
# TODO. move this method to utils file so it is imported here and at common_site
def _fetch_resources(uri, rel):
    path = os.path.join(settings.MEDIA_ROOT,
                        uri.replace(settings.MEDIA_URL, ""))
    return path


class BookingServiceUpdateView(View):
    """
    A view to render the list of bookingservices with catalogue numbers
    not matching the saved ones
    """

    def get(self, request, id, *args, **kwargs):
        context = dict()
        bk = Booking.objects.get(pk=id)
        services = BookingServices.find_bookingservices_with_different_amounts(bk)
        if services:
            context.update({'current': bk})
            context.update({'services': services})
            context.update(bookings_site.get_site_extra_context(request))
            request.current_app = bookings_site.name
            return render(request,
                          'booking/bookingservice_update_config.html', context)
        return redirect(reverse('common:booking_booking_change', args=[id]))

    def post(self, request, id, *args, **kwargs):
        services = request.POST.getlist('pk', None)
        if not services:
            messages.info(request, 'Booking Saved and no Service Updated')
        else:
            booking_services = BaseBookingService.objects.filter(pk__in=services)
            BookingServices.update_bookingservices_amounts(booking_services)
            messages.info(request, 'Booking Saved and %s services updated' % len(services))
        stay_on_booking = request.GET.get('stay_on_booking', False)
        if stay_on_booking:
            return redirect(reverse('common:booking_booking_change', args=[id]))
        return redirect(reverse('common:booking_booking_changelist'))


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
        bs = BookingProvidedService.objects.get(id=id)
        form = EmailProviderForm(
            request.user,
            initial={
                'from_address': default_requests_mail_from(request, bs.provider, bs.booking),
                'to_address': default_requests_mail_to(request, bs.provider, bs.booking),
                'bcc_address': default_requests_mail_bcc(request, bs.provider, bs.booking),
                'subject': default_requests_mail_subject(request, bs.provider, bs.booking),
                'body': default_requests_mail_body(request, bs.provider, bs.booking)
            })
        context = dict()
        context.update(bookings_site.get_site_extra_context(request))
        request.current_app = bookings_site.name
        context.update({'form': form})
        return render(request, 'booking/email_provider_form.html', context)

    def post(self, request, id, *args, **kwargs):
        booking_service = BookingProvidedService.objects.get(id=id)
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


class EmailProviderPackageServiceView(View):
    """
    A view to handle the email that will be sent to providers
    It allows to customice the default email
    """

    def get(self, request, id, *args, **kwargs):
        """
        This will render the default email for certain provider
        allowing it to be customiced
        """
        bps = BookingProvidedService.objects.get(id=id)
        provider = bps.provider
        if not provider:
            provider = bps.booking_package.provider
        form = EmailProviderForm(
            request.user,
            initial={
                'from_address': default_requests_mail_from(request, provider, bps.booking()),
                'to_address': default_requests_mail_to(request, provider, bps.booking()),
                'bcc_address': default_requests_mail_bcc(request, provider, bps.booking()),
                'subject': default_requests_mail_subject(request, provider, bps.booking()),
                'body': default_requests_mail_body(request, provider, bps.booking())
            })
        context = dict()
        context.update(bookings_site.get_site_extra_context(request))
        request.current_app = bookings_site.name
        context.update({'form': form})
        return render(request, 'booking/email_provider_form.html', context)

    def post(self, request, id, *args, **kwargs):
        bps = BookingProvidedService.objects.get(id=id)
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
            reverse('common:booking_bookingextrapackage_change', args=(bps.booking_package.id,)))


class EmailConfirmationView(View):
    """
    A view to handle the email that will be sent to Clients
    It allows to customice the default email
    """

    def get(self, request, id, *args, **kwargs):
        """
        This will render the default confirmation email for certain
        booking allowing it to be customiced
        """
        bk = Booking.objects.get(id=id)
        # pick all non-cancelled services
        services = BookingProvidedService.objects.filter(
            booking=bk.pk).exclude(status=SERVICE_STATUS_CANCELLED)
        # this is for the agency seller name (add also variable for email)
        client_name = ''
        if bk.agency_contact:
            client_name = bk.agency_contact.name
        elif bk.agency:
            client_name = 'customer'
        client_email = ''
        if bk.agency_contact:
            client_email = bk.agency_contact.email or ''
        rooming = bk.rooming_list.all()
        objs = get_bookingservice_objects(services)
        subj = 'Service Confirmation %s' % bk.name
        if bk.reference:
            subj += ' (%s)' % bk.reference
        initial = {
            'booking': bk,
            'services': objs,
            'client': client_name,
            'rooming': rooming,
            'user': request.user,
        }
        if request.user.email == settings.DEFAULT_BCC:
            bcc_list = settings.DEFAULT_BCC
        else:
            bcc_list = '%s, %s' % (request.user.email,
                                   settings.DEFAULT_BCC)
        t = get_template('booking/emails/confirmation_email.html')
        form = EmailProviderForm(request.user,
                                 {'from_address': request.user.email,
                                  'subject': subj,
                                  'to_address': client_email,
                                  'cc_address': default_mail_cc(request, bk),
                                  'bcc_address': bcc_list,
                                  'body': t.render(initial)})
        context = dict()
        context.update({'title': 'Confirmation Email'})
        context.update(bookings_site.get_site_extra_context(request))
        request.current_app = bookings_site.name
        context.update({'form': form})
        return render(request, 'booking/email_provider_form.html', context)

    def post(self, request, id, *args, **kwargs):
        booking_service = BaseBookingService.objects.get(id=id)
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
            message='Email sent successfully.',
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
    email.content_subtype = "html"
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
        if not self.request.user.is_authenticated:
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
        if not self.request.user.is_authenticated:
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
        if not self.request.user.is_authenticated:
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
        if not self.request.user.is_authenticated:
            return Schedule.objects.none()

        service = self.forwarded.get('service', None)
        if service is None:
            return Schedule.objects.none()

        transfer = Transfer.objects.get(pk=service)

        qs = Schedule.objects.all()

        if transfer.is_ticket:
            qs = qs.filter(is_arrival=False)
        else:
            qs = qs.filter(is_arrival=True)

        location = self.forwarded.get('location_from', None)

        if location:
            qs = qs.filter(
                location=location,
            )

        if self.q:
            qs = qs.filter(number__icontains=self.q)
        return qs[:20]


class ScheduleDepartureAutocompleteView(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        # Don't forget to filter out results depending on the visitor !
        if not self.request.user.is_authenticated:
            return Schedule.objects.none()
        qs = Schedule.objects.filter(is_arrival=False).all()

        location = self.forwarded.get('location_to', None)

        if location:
            qs = qs.filter(
                location=location,
            )

        if self.q:
            qs = qs.filter(number__icontains=self.q)
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


class SellerAutocompleteView(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        # Don't forget to filter out results depending on the visitor !
        if not self.request.user.is_authenticated:
            return User.objects.none()
        qs = User.objects.filter(
            is_staff=True,
            is_active=True)
        if self.q:
            qs = qs.filter(name__icontains=self.q)
        return qs[:20]


class PackageAutocompleteView(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        # Don't forget to filter out results depending on the visitor !
        if not self.request.user.is_authenticated:
            return Package.objects.none()
        qs = Package.objects.filter(enabled=True).all()
        if self.q:
            qs = qs.filter(name__icontains=self.q)
        return qs[:20]


class ProviderPackageAutocompleteView(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return Provider.objects.none()
        qs = Provider.objects.filter(enabled=True).all().distinct()

        service = self.forwarded.get('service', None)
        if service:
            qs = qs.filter(
                packageprovider__service=service,
            )

        if self.q:
            qs = qs.filter(name__icontains=self.q)
        return qs[:20]


class QuotePaxVariantAutocompleteView(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        # Don't forget to filter out results depending on the visitor !
        if not self.request.user.is_authenticated:
            return QuotePaxVariant.objects.none()
        qs = QuotePaxVariant.objects.all()

        quote_service_id = self.forwarded.get('quote_service', None)

        if quote_service_id:
            quote_service = QuoteService.objects.get(id=quote_service_id)

            quote_id = quote_service.quote_id
            if quote_id:
                qs = qs.filter(
                    quote=quote_id,
                )

        if self.q:
            qs = qs.filter(name__icontains=self.q)
        return qs[:20]


class BookingInvoiceView(View):
    """
    A view to handle the invoice for a booking
    """

    def get(self, request, id, *args, **kwargs):
        """
        This will render the booking invoice
        """
        booking = Booking.objects.get(id=id)
        if not booking.invoice:
            try:
                if not BookingServices.create_bookinginvoice(request.user, booking):
                    messages.add_message(request, messages.ERROR , "Failed Booking Invoice Creation")
                    return HttpResponseRedirect(reverse('common:booking_booking_change', args=[id]))
                messages.add_message(request, messages.SUCCESS , "Successful Booking Invoice Creation")
            except ValidationError as error:
                messages.add_message(request, messages.ERROR , error.message)
                return HttpResponseRedirect(reverse('common:booking_booking_change', args=[id]))
        return HttpResponseRedirect(reverse('common:booking_bookinginvoice_change', args=[booking.invoice_id]))


class BookingInvoicePDFView(View):
    """
    A view to handle the invoice PDF for a booking
    """
    def get(self, request, id, *args, **kwargs):
        booking = Booking.objects.get(id=id)
        if not booking.invoice:
            messages.add_message(request, messages.ERROR , "Failed Booking Invoice PDF")
            return HttpResponseRedirect(reverse('common:booking_booking_change', args=[id]))

        invoice = booking.invoice
        template = get_template("booking/pdf/invoice.html")
        details = BookingInvoiceDetail.objects.filter(invoice=invoice)
        lines = BookingInvoiceLine.objects.filter(invoice=invoice)
        partials = BookingInvoicePartial.objects.filter(invoice=invoice)
        context = {
            'pagesize': 'Letter',
            'invoice': invoice,
            'details': details,
            'lines': lines,
            'partials': partials,
        }
        html = template.render(context)
        html = html.encode('UTF-8')
        result = StringIO()
        pdf = pisa.pisaDocument(StringIO(html),
                                dest=result,
                                link_callback=_fetch_resources)
        if pdf.err:
            messages.add_message(request, messages.ERROR, "Failed Invoice PDF Generation")
            return HttpResponseRedirect(reverse('common:booking_booking_change', args=[id]))

        return HttpResponse(result.getvalue(), content_type='application/pdf')


class BookingInvoiceCancelView(View):
    """
    A view to handle the invoice cancellation for a booking
    """
    def get(self, request, id, *args, **kwargs):
        """
        This will cancel the booking invoice
        """
        booking = Booking.objects.get(id=id)
        try:
            BookingServices.cancel_bookinginvoice(request.user, booking)
            messages.add_message(request, messages.SUCCESS , "Successful Booking Invoice Cancellation")
        except ValidationError as error:
            messages.add_message(request, messages.ERROR , error.message)

        return HttpResponseRedirect(reverse('common:booking_booking_change', args=[id]))


class ServiceProvidersCostsView(ModelChangeFormProcessorView):
    common_site = bookings_site

    def process_data(self, booking_service, inlines):

        if hasattr(booking_service, 'service') and booking_service.service:
            service = booking_service.service
        elif hasattr(booking_service, 'book_service') and booking_service.book_service:
            service = booking_service.book_service
        else:
            return JsonResponse({
                'cost': None,
                'cost_message': 'Service Id Missing',
            })

        costs = BookingServices.find_service_providers_costs(booking_service, service)
        return JsonResponse({
            'costs': costs,
        })


class BookingProvidedAllotmentProvidersCostsView(ServiceProvidersCostsView):
    model = BookingProvidedAllotment
    common_sitemodel = BookingProvidedAllotmentSiteModel


class BookingProvidedTransferProvidersCostsView(ServiceProvidersCostsView):
    model = BookingProvidedTransfer
    common_sitemodel = BookingProvidedTransferSiteModel


class BookingProvidedExtraProvidersCostsView(ServiceProvidersCostsView):
    model = BookingProvidedExtra
    common_sitemodel = BookingProvidedExtraSiteModel


class BookingDetailAllotmentProvidersCostsView(ServiceProvidersCostsView):
    model = BookingBookDetailAllotment
    common_sitemodel = BookingBookDetailAllotmentSiteModel


class BookingDetailTransferProvidersCostsView(ServiceProvidersCostsView):
    model = BookingBookDetailTransfer
    common_sitemodel = BookingProvidedTransferSiteModel


class BookingDetailExtraProvidersCostsView(ServiceProvidersCostsView):
    model = BookingBookDetailExtra
    common_sitemodel = BookingBookDetailExtraSiteModel


class NewQuoteAllotmentProvidersCostsView(ServiceProvidersCostsView):
    model = NewQuoteAllotment
    common_sitemodel = NewQuoteAllotmentSiteModel


class NewQuoteTransferProvidersCostsView(ServiceProvidersCostsView):
    model = NewQuoteTransfer
    common_sitemodel = NewQuoteTransferSiteModel


class NewQuoteExtraProvidersCostsView(ServiceProvidersCostsView):
    model = NewQuoteExtra
    common_sitemodel = NewQuoteExtraSiteModel


class ServiceDetailsView(View):

    def post(self, request, *args, **kwargs):
        service_id = request.POST.get('service', None)
        return self.process_data(service_id)

    def process_data(self, service_id):
        return JsonResponse({
            'service_id': service_id,
        })


class ExtraServiceDetailsView(ServiceDetailsView):

    def process_data(self, service_id):
        if service_id:
            extra = Extra.objects.get(pk=service_id)
            return JsonResponse({
                'service_id': service_id,
                'car_rental': extra.car_rental is not None,
            })
        return JsonResponse({})


class TransferServiceDetailsView(View):

    def post(self, request, *args, **kwargs):
        service_id = request.POST.get('service', None)
        location_from_id = request.POST.get('location_from', None)
        location_to_id = request.POST.get('location_to', None)
        return self.process_data(service_id, location_from_id, location_to_id)

    def process_data(self, service_id, location_from_id, location_to_id):
        has_place_from = False
        if location_from_id:
            has_place_from = Place.objects.filter(location=location_from_id).count() > 0
        has_place_to = False
        if location_to_id:
            has_place_to = Place.objects.filter(location=location_to_id).count() > 0
        return JsonResponse({
            'service_id': service_id,
            'has_place_from': has_place_from,
            'has_place_to': has_place_to,
        })


class NewQuoteServiceBookDetailURLView(View):
    def post(self, request, *args, **kwargs):
        parent_id = request.POST.get('parent_id', None)
        service_id = request.POST.get('search_service', None)
        parent = QuoteService.objects.get(id=parent_id)
        if parent_id and service_id:
            service = Service.objects.get(id=service_id)
            querystring = urlencode({
                'quote_service': parent_id,
                'book_service': service_id,
            })
            if service.category == 'A':
                return redirect('{}?{}'.format(
                    reverse(
                        'common:booking_newquoteservicebookdetailallotment_add'),
                    querystring))
            elif service.category == 'T':
                return redirect('{}?{}'.format(
                    reverse(
                        'common:booking_newquoteservicebookdetailtransfer_add'),
                    querystring))
            elif service.category == 'E':
                return redirect('{}?{}'.format(
                    reverse(
                        'common:booking_newquoteservicebookdetailextra_add'),
                    querystring))
        # if here, there was a trouble. redirect to previous page
        if not service_id:
            messages.error(request, "You didn't choose any service")
        return redirect(parent)


class BookingBookDetailURLView(View):
    def post(self, request, *args, **kwargs):
        parent_id = request.POST.get('parent_id', None)
        service_id = request.POST.get('search_service', None)
        if parent_id and service_id:
            service = Service.objects.get(id=service_id)
            querystring = urlencode({
                'booking_service': parent_id,
                'book_service': service_id,
            })
            if service.category == 'A':
                return redirect('{}?{}'.format(
                    reverse(
                        'common:booking_bookingbookdetailallotment_add'),
                    querystring))
            elif service.category == 'T':
                return redirect('{}?{}'.format(
                    reverse(
                        'common:booking_bookingbookdetailtransfer_add'),
                    querystring))
            elif service.category == 'E':
                return redirect('{}?{}'.format(
                    reverse(
                        'common:booking_bookingbookdetailextra_add'),
                    querystring))
        # if here, there was a trouble. redirect to previous page
        if not service_id:
            messages.error(request, "You didn't choose any service")
        parent = BaseBookingService.objects.get(id=parent_id)
        return redirect(parent)


class BookingAddServiceView(View):
    def post(self, request, *args, **kwargs):
        parent_id = request.POST.get('parent_id', None)
        service_id = request.POST.get('search_service', None)
        if parent_id and service_id:
            service = Service.objects.get(id=service_id)
            querystring = self.build_querystring(parent_id, service_id)
            if service.category == 'A':
                return redirect('{}?{}'.format(
                    reverse(
                        'common:booking_bookingprovidedallotment_add'),
                    querystring))
            elif service.category == 'T':
                return redirect('{}?{}'.format(
                    reverse(
                        'common:booking_bookingprovidedtransfer_add'),
                    querystring))
            elif service.category == 'E':
                make_package = request.POST.get('make_package', False)
                if make_package == 'on':
                    return redirect('{}?{}'.format(
                        reverse(
                            'common:booking_bookingextrapackage_add'),
                        querystring))
                return redirect('{}?{}'.format(
                    reverse(
                        'common:booking_bookingprovidedextra_add'),
                    querystring))
        # if here, there was a trouble. redirect to previous page
        if not service_id:
            messages.error(request, "You didn't choose any service")
        parent = self.get_parent_obj(parent_id)
        return redirect(parent)

    def build_querystring(self, parent_id, service_id):
        return urlencode(
            {'booking': parent_id,
             'service': service_id})

    def get_parent_obj(self, parent_id):
        return Booking.objects.get(id=parent_id)


class QuoteAddServiceView(View):
    def post(self, request, *args, **kwargs):
        parent_id = request.POST.get('parent_id', None)
        service_id = request.POST.get('search_service', None)
        if parent_id and service_id:
            service = Service.objects.get(id=service_id)
            querystring = self.build_querystring(parent_id, service_id)
            if service.category == 'A':
                return redirect('{}?{}'.format(
                    reverse(
                        'common:booking_newquoteallotment_add'),
                    querystring))
            elif service.category == 'T':
                return redirect('{}?{}'.format(
                    reverse(
                        'common:booking_newquotetransfer_add'),
                    querystring))
            elif service.category == 'E':
                make_package = request.POST.get('make_package', False)
                if make_package == 'on':
                    return redirect('{}?{}'.format(
                        reverse(
                            'common:booking_quoteextrapackage_add'),
                        querystring))
                return redirect('{}?{}'.format(
                    reverse(
                        'common:booking_newquoteextra_add'),
                    querystring))
        # if here, there was a trouble. redirect to previous page
        if not service_id:
            messages.error(request, "You didn't choose any service")
        parent = self.get_parent_obj(parent_id)
        return redirect(parent)

    def build_querystring(self, parent_id, service_id):
        return urlencode(
            {'quote': parent_id,
             'service': service_id})

    def get_parent_obj(self, parent_id):
        return Quote.objects.get(id=parent_id)


class QuoteAddPackageServiceView(QuoteAddServiceView):
    def build_querystring(self, parent_id, service_id):
        qp = QuoteExtraPackage.objects.get(id=parent_id)
        quote = qp.quote_id
        return urlencode(
            {'quote': quote,
             'service': service_id,
             'quote_package': parent_id})

    def get_parent_obj(self, parent_id):
        return QuoteExtraPackage.objects.get(id=parent_id)


class BookingAddPackageServiceView(BookingAddServiceView):
    def build_querystring(self, parent_id, service_id):
        bp = BookingExtraPackage.objects.get(id=parent_id)
        booking = bp.booking_id
        return urlencode(
            {'booking': booking,
             'service': service_id,
             'booking_package': parent_id})

    def get_parent_obj(self, parent_id):
        return BookingExtraPackage.objects.get(id=parent_id)


def findBooked(form):
    # quote
    quote_id = form.forwarded.get('quote', None)
    if quote_id:
        quote = Quote.objects.get(pk=quote_id)
        return quote.booked

    quote_service_id = form.forwarded.get('quote_service', None)
    if quote_service_id:
        quote_service = QuoteService.objects.get(pk=quote_service_id)
        if quote_service:
            return quote_service.quote.booked
    # booking
    booking_id = form.forwarded.get('booking', None)
    if booking_id:
        booking = Booking.objects.get(pk=booking_id)
        return booking.booked

    booking_service_id = form.forwarded.get('booking_service', None)
    if booking_service_id:
        booking_service = BaseBookingService.objects.get(pk=booking_service_id)
        if booking_service:
            return booking_service.booking.booked
    return None


def findService(form):
    service = form.forwarded.get('service', None)
    if service:
        return service
    return form.forwarded.get('book_service', None)


def contract_list(catalogs):
    contracts = set()
    for catalog in catalogs:
        contracts.add(catalog.contract_code)
    return contracts


def allotment_contract_list(
        booked, service, provider, date_from, date_to, contract_code, addon,
        room_type, board_type):

    qs = ProviderAllotmentService.objects.all().distinct().filter(
        service=service,
        provider__enabled=True).exclude(contract_code='')
    if provider:
        qs = qs.filter(provider=provider)
    if booked:
        qs = qs.filter(
            Q(booked_from__isnull=True)
            | Q(booked_from__lte=booked),
            Q(booked_to__isnull=True)
            | Q(booked_to__gte=booked))
    if contract_code:
        qs = qs.filter(contract_code__icontains=contract_code)
    if date_from:
        qs = qs.filter(
            date_to__gte=date_from)
    if date_to:
        qs = qs.filter(date_from__lte=date_to)
    # filters on details
    if addon:
        if room_type:
            if board_type:
                qs = qs.filter(
                    providerallotmentdetail__addon=addon,
                    providerallotmentdetail__room_type=room_type,
                    providerallotmentdetail__board_type=board_type)
            else:
                qs = qs.filter(
                    providerallotmentdetail__addon=addon,
                    providerallotmentdetail__room_type=room_type)
        else:
            if board_type:
                qs = qs.filter(
                    providerallotmentdetail__addon=addon,
                    providerallotmentdetail__board_type=board_type)
            else:
                qs = qs.filter(
                    providerallotmentdetail__addon=addon)
    else:
        if room_type:
            if board_type:
                qs = qs.filter(
                    providerallotmentdetail__addon=ADDON_FOR_NO_ADDON,
                    providerallotmentdetail__room_type=room_type,
                    providerallotmentdetail__board_type=board_type)
            else:
                qs = qs.filter(
                    providerallotmentdetail__addon=ADDON_FOR_NO_ADDON,
                    providerallotmentdetail__room_type=room_type)
        else:
            if board_type:
                qs = qs.filter(
                    providerallotmentdetail__addon=ADDON_FOR_NO_ADDON,
                    providerallotmentdetail__board_type=board_type)
            else:
                qs = qs.filter(
                    providerallotmentdetail__addon=ADDON_FOR_NO_ADDON)

    return contract_list(list(qs))


class AllotmentContractAutocompleteView(autocomplete.Select2ListView):
    def get_list(self):
        if not self.request.user.is_authenticated:
            return []

        booked = findBooked(self)
        service = findService(self)
        provider = self.forwarded.get('provider', None)
        date_from = self.forwarded.get('date_from', None)
        date_to = self.forwarded.get('date_to', None)
        addon = self.forwarded.get('service_addon', None)
        room_type = self.forwarded.get('room_type', None)
        board_type = self.forwarded.get('board_type', None)

        return allotment_contract_list(
            booked, service, provider, date_from, date_to, self.q, addon,
            room_type, board_type)


def transfer_contract_list(
        booked, service, provider, date_from, date_to, contract_code, addon,
        location_from, location_to):

    qs = ProviderTransferService.objects.all().distinct().filter(
        service=service,
        provider__enabled=True).exclude(contract_code='')

    if provider:
        qs = qs.filter(provider=provider)
    if booked:
        qs = qs.filter(
            Q(booked_from__isnull=True)
            | Q(booked_from__lte=booked))
        qs = qs.filter(
            Q(booked_to__isnull=True)
            | Q(booked_to__gte=booked))
    if contract_code:
        qs = qs.filter(contract_code__icontains=contract_code)
    if date_from:
        qs = qs.filter(
            date_to__gte=date_from)
    if date_to:
        qs = qs.filter(date_from__lte=date_to)
    # filters on details
    if addon:
        if location_from:
            if location_to:
                qs = qs.filter(
                    providertransferdetail__addon=addon,
                    providertransferdetail__location_from=location_from,
                    providertransferdetail__location_to=location_to)
            else:
                qs = qs.filter(
                    providertransferdetail__addon=addon,
                    providertransferdetail__location_from=location_from)
        else:
            if location_to:
                qs = qs.filter(
                    providertransferdetail__addon=addon,
                    providertransferdetail__location_to=location_to)
            else:
                qs = qs.filter(
                    providertransferdetail__addon=addon)
    else:
        if location_from:
            if location_to:
                qs = qs.filter(
                    providertransferdetail__addon=ADDON_FOR_NO_ADDON,
                    providertransferdetail__location_from=location_from,
                    providertransferdetail__location_to=location_to)
            else:
                qs = qs.filter(
                    providertransferdetail__addon=ADDON_FOR_NO_ADDON,
                    providertransferdetail__location_from=location_from)
        else:
            if location_to:
                qs = qs.filter(
                    providertransferdetail__addon=ADDON_FOR_NO_ADDON,
                    providertransferdetail__location_to=location_to)
            else:
                qs = qs.filter(
                    providertransferdetail__addon=ADDON_FOR_NO_ADDON)

    return contract_list(list(qs))


class TransferContractAutocompleteView(autocomplete.Select2ListView):
    def get_list(self):
        if not self.request.user.is_authenticated:
            return []

        booked = findBooked(self)
        service = findService(self)
        provider = self.forwarded.get('provider', None)
        date_from = self.forwarded.get('date_from', None)
        date_to = self.forwarded.get('date_to', None)
        addon = self.forwarded.get('service_addon', None)
        location_from = self.forwarded.get('location_from', None)
        location_to = self.forwarded.get('location_to', None)

        return transfer_contract_list(
            booked, service, provider, date_from, date_to, self.q, addon,
            location_from, location_to)


def extra_contract_list(
        booked, service, provider, date_from, date_to, contract_code, addon):

    qs = ProviderExtraService.objects.all().distinct().filter(
        service=service,
        provider__enabled=True).exclude(contract_code='')

    if provider:
        qs = qs.filter(provider=provider)
    if booked:
        qs = qs.filter(
            Q(booked_from__isnull=True)
            | Q(booked_from__lte=booked))
        qs = qs.filter(
            Q(booked_to__isnull=True)
            | Q(booked_to__gte=booked))
    if contract_code:
        qs = qs.filter(contract_code__icontains=contract_code)
    if date_from:
        qs = qs.filter(
            date_to__gte=date_from)
    if date_to:
        qs = qs.filter(date_from__lte=date_to)
    # filters on details
    if addon:
        qs = qs.filter(providerextradetail__addon=addon)
    else:
        qs = qs.filter(providerextradetail__addon=ADDON_FOR_NO_ADDON)

    return contract_list(list(qs))


class ExtraContractAutocompleteView(autocomplete.Select2ListView):
    def get_list(self):
        if not self.request.user.is_authenticated:
            return []

        booked = findBooked(self)
        service = findService(self)
        provider = self.forwarded.get('provider', None)
        date_from = self.forwarded.get('date_from', None)
        date_to = self.forwarded.get('date_to', None)
        addon = self.forwarded.get('service_addon', None)

        return extra_contract_list(
            booked, service, provider, date_from, date_to, self.q, addon)
