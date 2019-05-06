# -*- coding: utf-8 -*-
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
    QuoteAllotmentSiteModel, QuoteTransferSiteModel, QuoteExtraSiteModel, QuotePackageSiteModel,
    QuotePackageAllotmentSiteModel, QuotePackageTransferSiteModel, QuotePackageExtraSiteModel,
    BookingAllotmentSiteModel,
    BookingTransferSiteModel,
    BookingExtraSiteModel,
    BookingPackageSiteModel,
    BookingPackageAllotmentSiteModel,
    BookingPackageTransferSiteModel,
    BookingPackageExtraSiteModel,
)
from booking.constants import ACTIONS
from booking.models import (
    Package,
    Quote, QuotePaxVariant, QuoteService,
    QuoteAllotment, QuoteTransfer, QuoteExtra, QuotePackage,
    QuotePackageAllotment, QuotePackageTransfer, QuotePackageExtra,
    Booking, BookingService,
    BookingPax, BookingServicePax,
    BookingAllotment, BookingTransfer, BookingExtra, BookingPackage,
    BookingPackageAllotment, BookingPackageTransfer, BookingPackageExtra
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

        # allotment_list = inlines[1]
        # transfer_list = inlines[2]
        # extra_list = inlines[3]
        # package_list = inlines[4]
        # if (
        #        (not allotment_list) and
        #        (not transfer_list) and
        #        (not extra_list) and
        #        (not package_list)):
        #    return JsonResponse({
        #        'code': 3,
        #        'message': 'Services Missing',
        #        'results': None,
        #    })
        # code, message, results = BookingServices.find_quote_amounts(
        #    quote.agency, variant_list, allotment_list, transfer_list, extra_list, package_list)


        code, message, results = BookingServices.find_quote_amounts(
            quote, variant_list)

        return JsonResponse({
            'code': code,
            'message': message,
            'results': results,
        })


class QuoteAllotmentAmountsView(ModelChangeFormProcessorView):
    
    model = QuoteAllotment
    common_sitemodel = QuoteAllotmentSiteModel
    common_site = bookings_site

    def process_data(self, quoteallotment, inlines):

        variant_list = inlines[0]
        if not variant_list:
            return JsonResponse({
                'code': 3,
                'message': 'Pax Variants Missing',
                'results': None,
            })

        code, message, results = BookingServices.find_quoteallotment_amounts(
            quoteallotment, variant_list)

        return JsonResponse({
            'code': code,
            'message': message,
            'results': results,
        })


class QuoteTransferAmountsView(ModelChangeFormProcessorView):
    
    model = QuoteTransfer
    common_sitemodel = QuoteTransferSiteModel
    common_site = bookings_site

    def process_data(self, quotetransfer, inlines):

        variant_list = inlines[0]
        if not variant_list:
            return JsonResponse({
                'code': 3,
                'message': 'Pax Variants Missing',
                'results': None,
            })

        code, message, results = BookingServices.find_quotetransfer_amounts(
            quotetransfer, variant_list)

        return JsonResponse({
            'code': code,
            'message': message,
            'results': results,
        })


class QuoteExtraAmountsView(ModelChangeFormProcessorView):
    
    model = QuoteExtra
    common_sitemodel = QuoteExtraSiteModel
    common_site = bookings_site

    def process_data(self, quoteextra, inlines):

        variant_list = inlines[0]
        if not variant_list:
            return JsonResponse({
                'code': 3,
                'message': 'Pax Variants Missing',
                'results': None,
            })

        code, message, results = BookingServices.find_quoteextra_amounts(
            quoteextra, variant_list)

        return JsonResponse({
            'code': code,
            'message': message,
            'results': results,
        })


class QuotePackageAmountsView(ModelChangeFormProcessorView):
    
    model = QuotePackage
    common_sitemodel = QuotePackageSiteModel
    common_site = bookings_site

    def process_data(self, quotepackage, inlines):

        variant_list = inlines[0]
        if not variant_list:
            return JsonResponse({
                'code': 3,
                'message': 'Pax Variants Missing',
                'results': None,
            })

        code, message, results = BookingServices.find_quotepackage_amounts(
            quotepackage, variant_list)

        return JsonResponse({
            'code': code,
            'message': message,
            'results': results,
        })


class QuotePackageAllotmentAmountsView(ModelChangeFormProcessorView):
    
    model = QuotePackageAllotment
    common_sitemodel = QuotePackageAllotmentSiteModel
    common_site = bookings_site

    def process_data(self, quotepackageallotment, inlines):

        variant_list = inlines[0]
        if not variant_list:
            return JsonResponse({
                'code': 3,
                'message': 'Pax Variants Missing',
                'results': None,
            })

        code, message, results = BookingServices.find_quotepackageallotment_amounts(
            quotepackageallotment, variant_list)

        return JsonResponse({
            'code': code,
            'message': message,
            'results': results,
        })


class QuotePackageTransferAmountsView(ModelChangeFormProcessorView):
    
    model = QuotePackageTransfer
    common_sitemodel = QuotePackageTransferSiteModel
    common_site = bookings_site

    def process_data(self, quotepackagetransfer, inlines):

        variant_list = inlines[0]
        if not variant_list:
            return JsonResponse({
                'code': 3,
                'message': 'Pax Variants Missing',
                'results': None,
            })

        code, message, results = BookingServices.find_quotepackagetransfer_amounts(
            quotepackagetransfer, variant_list)

        return JsonResponse({
            'code': code,
            'message': message,
            'results': results,
        })


class QuotePackageExtraAmountsView(ModelChangeFormProcessorView):
    
    model = QuotePackageExtra
    common_sitemodel = QuotePackageExtraSiteModel
    common_site = bookings_site

    def process_data(self, quotepackageextra, inlines):

        variant_list = inlines[0]
        if not variant_list:
            return JsonResponse({
                'code': 3,
                'message': 'Pax Variants Missing',
                'results': None,
            })

        code, message, results = BookingServices.find_quotepackageextra_amounts(
            quotepackageextra, variant_list)

        return JsonResponse({
            'code': code,
            'message': message,
            'results': results,
        })


class BookingServiceAmountsView(ModelChangeFormProcessorView):
    common_site = bookings_site

    def verify(self, bookingservice, inlines):
        if not bookingservice.booking:
            return JsonResponse({
                'code': 3,
                'message': 'Booking Id Missing',
                'cost': None,
                'cost_message': 'Booking Id Missing',
                'price': None,
                'price_message': 'Booking Id Missing',
            }), None
        if not bookingservice.service:
            return JsonResponse({
                'code': 3,
                'message': 'Service Id Missing',
                'cost': None,
                'cost_message': 'Service Id Missing',
                'price': None,
                'price_message': 'Service Id Missing',
            }), None
        pax_list = inlines[0]
        if not pax_list:
            return JsonResponse({
                'code': 3,
                'message': 'Paxes Missing',
                'cost': None,
                'cost_message': 'Paxes Missing',
                'price': None,
                'price_message': 'Paxes Missing',
            }), pax_list
        return None, pax_list


class BookingPackageServiceAmountsView(ModelChangeFormProcessorView):
    common_site = bookings_site

    def verify(self, bookingpackageservice):
        if not bookingpackageservice.booking_package:
            return JsonResponse({
                'code': 3,
                'message': 'BookingPackage Id Missing',
                'cost': None,
                'cost_message': 'BookingPackage Id Missing',
                'price': None,
                'price_message': 'BookingPackage Id Missing',
            }), None
        if not bookingpackageservice.service:
            return JsonResponse({
                'code': 3,
                'message': 'Service Id Missing',
                'cost': None,
                'cost_message': 'Service Id Missing',
                'price': None,
                'price_message': 'Service Id Missing',
            }), None
        pax_list = list(BookingServicePax.objects.filter(
            booking_service=bookingpackageservice.booking_package_id).all())
        if not pax_list:
            return JsonResponse({
                'code': 3,
                'message': 'Paxes Missing',
                'cost': None,
                'cost_message': 'Paxes Missing',
                'price': None,
                'price_message': 'Paxes Missing',
            }), pax_list
        return None, pax_list


class BookingAllotmentAmountsView(BookingServiceAmountsView):
    model = BookingAllotment
    common_sitemodel = BookingAllotmentSiteModel

    def process_data(self, bookingallotment, inlines):

        response, pax_list = self.verify(bookingallotment, inlines)
        if response:
            return response
        cost_groups = BookingServices.find_paxes_groups(pax_list, bookingallotment.service, True)
        price_groups = BookingServices.find_paxes_groups(pax_list, bookingallotment.service, False)

        code, message, cost, cost_msg, price, price_msg = ConfigServices.allotment_amounts(
            bookingallotment.service_id,
            bookingallotment.datetime_from, bookingallotment.datetime_to,
            cost_groups, price_groups,
            bookingallotment.provider, bookingallotment.booking.agency,
            bookingallotment.board_type, bookingallotment.room_type_id,
        )
        return JsonResponse({
            'code': code,
            'message': message,
            'cost': cost,
            'cost_message': cost_msg,
            'price': price,
            'price_message': price_msg,
        })


class BookingTransferAmountsView(BookingServiceAmountsView):
    model = BookingTransfer
    common_sitemodel = BookingTransferSiteModel

    def process_data(self, bookingtransfer, inlines):

        response, pax_list = self.verify(bookingtransfer, inlines)
        if response:
            return response
        cost_groups = BookingServices.find_paxes_groups(pax_list, bookingtransfer.service, True)
        price_groups = BookingServices.find_paxes_groups(pax_list, bookingtransfer.service, False)

        code, message, cost, cost_msg, price, price_msg = ConfigServices.transfer_amounts(
            bookingtransfer.service_id,
            bookingtransfer.datetime_from, bookingtransfer.datetime_to,
            cost_groups, price_groups,
            bookingtransfer.provider, bookingtransfer.booking.agency,
            bookingtransfer.location_from, bookingtransfer.location_to,
        )
        return JsonResponse({
            'code': code,
            'message': message,
            'cost': cost,
            'cost_message': cost_msg,
            'price': price,
            'price_message': price_msg,
        })


class BookingExtraAmountsView(BookingServiceAmountsView):
    model = BookingExtra
    common_sitemodel = BookingExtraSiteModel

    def process_data(self, bookingextra, inlines):

        response, pax_list = self.verify(bookingextra, inlines)
        if response:
            return response
        cost_groups = BookingServices.find_paxes_groups(pax_list, bookingextra.service, True)
        price_groups = BookingServices.find_paxes_groups(pax_list, bookingextra.service, False)

        addon_id = bookingextra.addon
        if addon_id == '':
            addon_id = None

        code, message, cost, cost_msg, price, price_msg = ConfigServices.extra_amounts(
            bookingextra.service_id,
            bookingextra.datetime_from, bookingextra.datetime_to,
            cost_groups, price_groups,
            bookingextra.provider, bookingextra.booking.agency,
            addon_id, int(bookingextra.quantity), int(bookingextra.parameter),
        )

        return JsonResponse({
            'code': code,
            'message': message,
            'cost': cost,
            'cost_message': cost_msg,
            'price': price,
            'price_message': price_msg,
        })


class BookingPackageAmountsView(BookingServiceAmountsView):
    model = BookingPackage
    common_sitemodel = BookingPackageSiteModel

    def process_data(self, bookingpackage, inlines):

        response, pax_list = self.verify(bookingpackage, inlines)
        if response:
            return response

        code, message, cost, cost_msg, price, price_msg = BookingServices.bookingpackage_amounts(
            bookingpackage, pax_list)

        return JsonResponse({
            'code': code,
            'message': message,
            'cost': cost,
            'cost_message': cost_msg,
            'price': price,
            'price_message': price_msg,
        })


class BookingPackageAllotmentAmountsView(BookingPackageServiceAmountsView):
    model = BookingPackageAllotment
    common_sitemodel = BookingPackageAllotmentSiteModel

    def process_data(self, bookingpackageallotment, inlines=None):

        response, pax_list = self.verify(bookingpackageallotment)
        if response:
            return response
        cost_groups = BookingServices.find_paxes_groups(pax_list, bookingpackageallotment.service, True)
        price_groups = BookingServices.find_paxes_groups(pax_list, bookingpackageallotment.service, False)

        provider = bookingpackageallotment.booking_package.provider
        if provider is None:
            provider = bookingpackageallotment.provider

        code, message, cost, cost_msg, price, price_msg = ConfigServices.allotment_amounts(
            bookingpackageallotment.service_id,
            bookingpackageallotment.datetime_from, bookingpackageallotment.datetime_to,
            cost_groups, price_groups,
            provider, bookingpackageallotment.booking_package.booking.agency,
            bookingpackageallotment.board_type, bookingpackageallotment.room_type_id,
        )
        return JsonResponse({
            'code': code,
            'message': message,
            'cost': cost,
            'cost_message': cost_msg,
            'price': price,
            'price_message': price_msg,
        })


class BookingPackageTransferAmountsView(BookingPackageServiceAmountsView):
    model = BookingPackageTransfer
    common_sitemodel = BookingPackageTransferSiteModel

    def process_data(self, bookingpackagetransfer, inlines):

        response, pax_list = self.verify(bookingpackagetransfer)
        if response:
            return response
        cost_groups = BookingServices.find_paxes_groups(pax_list, bookingpackagetransfer.service, True)
        price_groups = BookingServices.find_paxes_groups(pax_list, bookingpackagetransfer.service, False)

        provider = bookingpackagetransfer.booking_package.provider
        if provider is None:
            provider = bookingpackagetransfer.provider

        code, message, cost, cost_msg, price, price_msg = ConfigServices.transfer_amounts(
            bookingpackagetransfer.service_id,
            bookingpackagetransfer.datetime_from, bookingpackagetransfer.datetime_to,
            cost_groups, price_groups,
            provider, bookingpackagetransfer.booking_package.booking.agency,
            bookingpackagetransfer.location_from, bookingpackagetransfer.location_to,
        )
        return JsonResponse({
            'code': code,
            'message': message,
            'cost': cost,
            'cost_message': cost_msg,
            'price': price,
            'price_message': price_msg,
        })


class BookingPackageExtraAmountsView(BookingPackageServiceAmountsView):
    model = BookingPackageExtra
    common_sitemodel = BookingPackageExtraSiteModel

    def process_data(self, bookingpackageextra, inlines):

        response, pax_list = self.verify(bookingpackageextra)
        if response:
            return response
        cost_groups = BookingServices.find_paxes_groups(pax_list, bookingpackageextra.service, True)
        price_groups = BookingServices.find_paxes_groups(pax_list, bookingpackageextra.service, False)

        provider = bookingpackageextra.booking_package.provider
        if provider is None:
            provider = bookingpackageextra.provider

        addon_id = bookingpackageextra.addon
        if addon_id == '':
            addon_id = None

        code, message, cost, cost_msg, price, price_msg = ConfigServices.extra_amounts(
            bookingpackageextra.service_id,
            bookingpackageextra.datetime_from, bookingpackageextra.datetime_to,
            cost_groups, price_groups,
            provider, bookingpackageextra.booking_package.booking.agency,
            addon_id, int(bookingpackageextra.quantity), int(bookingpackageextra.parameter),
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
    # template = get_template("booking/pdf/voucher.html")
    booking = Booking.objects.get(id=id)
    services = BookingService.objects.filter(id__in=[2, 1])
    type_map = {
        'E': BookingExtra,
        'A': BookingAllotment,
        'T': BookingTransfer,
    }
    objs = []
    for service in services:
        obj = type_map[service.service_type].objects.get(id=service.id)
        objs.append(obj)
    context = {'pagesize': 'Letter',
               'booking': booking,
               'office': Office.objects.get(id=1),
               'services': objs}
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
            provider_name = bs.provider.alias or bs.provider.name
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
                                     'subject': 'Solicitud de Reserva',
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
        services = BookingService.objects.filter(
            booking=bk.pk).exclude(status='CN')
        # this is for the agency seller name (add also variable for email)
        client_name = ''
        if bk.agency:
            client_name = bk.agency.name
        rooming = bk.rooming_list.all()
        initial = {
            'booking': bk,
            'services': services,
            'client': client_name,
            'rooming': rooming,
            'user': request.user,
        }
        t = get_template('booking/emails/confirmation_email.html')
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


class QuotePaxVariantAutocompleteView(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        # Don't forget to filter out results depending on the visitor !
        if not self.request.user.is_authenticated():
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
