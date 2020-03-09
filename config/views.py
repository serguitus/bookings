# -*- coding: utf-8 -*-
from __future__ import unicode_literals
"""
Config Views
"""

import os
from django.conf import settings

from dal import autocomplete

from config.models import (
    Location, TransferZone, ServiceCategory, RoomType, Addon, AllotmentBoardType,
    Service,
    Allotment, Transfer, Extra, CarRental, CarRentalOffice,
)

from django.contrib import messages
from django.db.models import Q
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import redirect
from django.template.loader import get_template
from django.urls import reverse
from django.views import View

from finance.models import Agency, Provider

from reservas.custom_settings import ADDON_FOR_NO_ADDON

try:
    from cStringIO import StringIO
except ImportError:
    from _io import StringIO

from xhtml2pdf import pisa


class LocationAutocompleteView(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        # Don't forget to filter out results depending on the visitor !
        if not self.request.user.is_authenticated():
            return Location.objects.none()
        qs = Location.objects.filter(enabled=True).all()
        if self.q:
            qs = qs.filter(name__icontains=self.q)
        return qs[:20]


class ZoneTransferAutocompleteView(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        # Don't forget to filter out results depending on the visitor !
        if not self.request.user.is_authenticated():
            return Transfer.objects.none()
        qs = Transfer.objects.filter(has_pickup_time=True)
        if self.q:
            qs = qs.filter(name__icontains=self.q)
        return qs[:20]


class ServiceCategoryAutocompleteView(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        # Don't forget to filter out results depending on the visitor !
        if not self.request.user.is_authenticated():
            return ServiceCategory.objects.none()
        qs = ServiceCategory.objects.all()
        if self.q:
            qs = qs.filter(name__icontains=self.q)
        return qs[:20]


class RoomTypeAutocompleteView(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        # Don't forget to filter out results depending on the visitor !
        if not self.request.user.is_authenticated():
            return RoomType.objects.none()
        qs = RoomType.objects.filter(enabled=True).all().distinct()

        detail_service = self.forwarded.get('detail_service', None)

        if detail_service:
            qs = qs.filter(allotmentroomtype__allotment=detail_service)
        else:
            service = self.forwarded.get('service', None)

            if service:
                qs = qs.filter(allotmentroomtype__allotment=service)

        if self.q:
            qs = qs.filter(name__icontains=self.q)
        return qs[:20]


class BoardTypeAutocompleteView(autocomplete.Select2ListView):
    def get_list(self):
        result = []
        detail_service = self.forwarded.get('detail_service', None)
        if detail_service:
            allotment_boards = AllotmentBoardType.objects.filter(allotment=detail_service).distinct().all()
            for allotment_board in allotment_boards:
                result.append(allotment_board.board_type)
        else:
            service = self.forwarded.get('service', None)
            if service is not None:
                allotment_boards = AllotmentBoardType.objects.filter(allotment=service).distinct().all()
                for allotment_board in allotment_boards:
                    result.append(allotment_board.board_type)

        return result


class AddonAutocompleteView(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        # Don't forget to filter out results depending on the visitor !
        if not self.request.user.is_authenticated():
            return Addon.objects.none()
        qs = Addon.objects.filter(enabled=True).all().distinct()

        detail_service = self.forwarded.get('detail_service', None)

        if detail_service:
            qs = qs.filter(serviceaddon__service=detail_service)
        else:
            service = self.forwarded.get('service', None)

            if service:
                qs = qs.filter(serviceaddon__service=service)


        if self.q:
            qs = qs.filter(name__icontains=self.q)
        return qs[:20]


class AllotmentAutocompleteView(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        # Don't forget to filter out results depending on the visitor !
        if not self.request.user.is_authenticated():
            return Allotment.objects.none()
        qs = Allotment.objects.filter(enabled=True).all()
        if self.q:
            qs = qs.filter(name__icontains=self.q)
        return qs[:20]


def provider_allotment_queryset(
        service, room_type=None, board_type=None, addon=None, text=None):

    qs = Provider.objects.filter(enabled=True).all().distinct()

    if service:
        if room_type:
            if board_type:
                if addon:
                    qs = qs.filter(
                        providerallotmentservice__service=service,
                        providerallotmentservice__providerallotmentdetail__room_type=room_type,
                        providerallotmentservice__providerallotmentdetail__board_type=board_type,
                        providerallotmentservice__providerallotmentdetail__addon=addon,
                    )
                else:
                    qs = qs.filter(
                        providerallotmentservice__service=service,
                        providerallotmentservice__providerallotmentdetail__room_type=room_type,
                        providerallotmentservice__providerallotmentdetail__board_type=board_type,
                        providerallotmentservice__providerallotmentdetail__addon=ADDON_FOR_NO_ADDON,
                    )
            elif addon:
                qs = qs.filter(
                    providerallotmentservice__service=service,
                    providerallotmentservice__providerallotmentdetail__room_type=room_type,
                    providerallotmentservice__providerallotmentdetail__addon=addon,
                )
            else:
                qs = qs.filter(
                    providerallotmentservice__service=service,
                    providerallotmentservice__providerallotmentdetail__room_type=room_type,
                    providerallotmentservice__providerallotmentdetail__addon=ADDON_FOR_NO_ADDON,
                )
        elif board_type:
            if addon:
                qs = qs.filter(
                    providerallotmentservice__service=service,
                    providerallotmentservice__providerallotmentdetail__board_type=board_type,
                    providerallotmentservice__providerallotmentdetail__addon=addon,
                )
            else:
                qs = qs.filter(
                    providerallotmentservice__service=service,
                    providerallotmentservice__providerallotmentdetail__board_type=board_type,
                    providerallotmentservice__providerallotmentdetail__addon=ADDON_FOR_NO_ADDON,
                )
        elif addon:
            qs = qs.filter(
                providerallotmentservice__service=service,
                providerallotmentservice__providerallotmentdetail__addon=addon,
            )
        else:
            qs = qs.filter(
                providerallotmentservice__service=service,
                providerallotmentservice__providerallotmentdetail__addon=ADDON_FOR_NO_ADDON,
            )
    else:
        qs = qs.filter(
            providerallotmentservice__provider__isnull=False,
        )

    if text:
        qs = qs.filter(name__icontains=text)
    return qs[:20]


class ProviderAllotmentAutocompleteView(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        if not self.request.user.is_authenticated():
            return Provider.objects.none()

        service = self.forwarded.get('service', None)
        room_type = self.forwarded.get('room_type', None)
        board_type = self.forwarded.get('board_type', None)
        addon = self.forwarded.get('service_addon', None)

        return provider_allotment_queryset(service, room_type, board_type, addon, self.q)


class TransferAutocompleteView(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        # Don't forget to filter out results depending on the visitor !
        if not self.request.user.is_authenticated():
            return Transfer.objects.none()
        qs = Transfer.objects.filter(enabled=True).all()
        if self.q:
            qs = qs.filter(name__icontains=self.q)
        return qs[:20]


def provider_transfer_queryset(
        service, location_from=None, location_to=None, addon=None, text=None):

    qs = Provider.objects.filter(enabled=True).all().distinct()

    if service:
        if location_from:
            if location_to:
                if addon:
                    qs = qs.filter(
                        Q(providertransferservice__service=service)
                        &
                        Q(providertransferservice__providertransferdetail__addon=addon)
                        &
                        (
                            (
                                Q(providertransferservice__providertransferdetail__p_location_from=location_from)
                                & Q(providertransferservice__providertransferdetail__p_location_to=location_to)
                            )
                            |
                            (
                                Q(providertransferservice__providertransferdetail__p_location_from=location_to)
                                & Q(providertransferservice__providertransferdetail__p_location_to=location_from)
                            )
                        )
                    )
                else:
                    qs = qs.filter(
                        Q(providertransferservice__service=service)
                        &
                        Q(providertransferservice__providertransferdetail__addon=ADDON_FOR_NO_ADDON)
                        &
                        (
                            (
                                Q(providertransferservice__providertransferdetail__p_location_from=location_from)
                                & Q(providertransferservice__providertransferdetail__p_location_to=location_to)
                            )
                            |
                            (
                                Q(providertransferservice__providertransferdetail__p_location_from=location_to)
                                & Q(providertransferservice__providertransferdetail__p_location_to=location_from)
                            )
                        )
                    )
            elif addon:
                qs = qs.filter(
                    Q(providertransferservice__service=service)
                    &
                    Q(providertransferservice__providertransferdetail__addon=addon)
                    &
                    (
                        Q(providertransferservice__providertransferdetail__p_location_from=location_from)
                        |
                        Q(providertransferservice__providertransferdetail__p_location_to=location_from)
                    )
                )
            else:
                qs = qs.filter(
                    Q(providertransferservice__service=service)
                    &
                    Q(providertransferservice__providertransferdetail__addon=ADDON_FOR_NO_ADDON)
                    &
                    (
                        Q(providertransferservice__providertransferdetail__p_location_from=location_from)
                        |
                        Q(providertransferservice__providertransferdetail__p_location_to=location_from)
                    )
                )
        elif location_to:
            if addon:
                qs = qs.filter(
                    Q(providertransferservice__service=service)
                    &
                    Q(providertransferservice__providertransferdetail__addon=addon)
                    &
                    (
                        Q(providertransferservice__providertransferdetail__p_location_to=location_to)
                        |
                        Q(providertransferservice__providertransferdetail__p_location_from=location_to)
                    )
                )
            else:
                qs = qs.filter(
                    Q(providertransferservice__service=service)
                    &
                    Q(providertransferservice__providertransferdetail__addon=ADDON_FOR_NO_ADDON)
                    &
                    (
                        Q(providertransferservice__providertransferdetail__p_location_to=location_to)
                        |
                        Q(providertransferservice__providertransferdetail__p_location_from=location_to)
                    )
                )
        elif addon:
            qs = qs.filter(
                providertransferservice__service=service,
                providertransferservice__providertransferdetail__addon=addon
            )
        else:
            qs = qs.filter(
                providertransferservice__service=service,
                providertransferservice__providertransferdetail__addon=ADDON_FOR_NO_ADDON
            )
    else:
        qs = qs.filter(
            providertransferservice__provider__isnull=False,
        )

    if text:
        qs = qs.filter(name__icontains=text)
    return qs[:20]


class ProviderTransferAutocompleteView(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        if not self.request.user.is_authenticated():
            return Provider.objects.none()

        service = self.forwarded.get('service', None)
        location_from = self.forwarded.get('location_from', None)
        location_to = self.forwarded.get('location_to', None)
        addon = self.forwarded.get('service_addon', None)

        return provider_transfer_queryset(service, location_from, location_to, addon, self.q)


class ExtraAutocompleteView(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        # Don't forget to filter out results depending on the visitor !
        if not self.request.user.is_authenticated():
            return Extra.objects.none()
        qs = Extra.objects.filter(enabled=True).all()
        if self.q:
            qs = qs.filter(name__icontains=self.q)
        return qs[:20]


def provider_extra_queryset(service, addon=None, text=None):

    qs = Provider.objects.filter(enabled=True).all().distinct()

    if service:
        if addon:
            qs = qs.filter(
                providerextraservice__service=service,
                providerextraservice__providerextradetail__addon=addon,
            )
        else:
            qs = qs.filter(
                providerextraservice__service=service,
                providerextraservice__providerextradetail__addon=ADDON_FOR_NO_ADDON,
            )
    else:
        qs = qs.filter(
            providerextraservice__provider__isnull=False,
        )

    if text:
        qs = qs.filter(name__icontains=text)
    return qs[:20]


class ProviderExtraAutocompleteView(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        if not self.request.user.is_authenticated():
            return Provider.objects.none()
        qs = Provider.objects.filter(enabled=True).all().distinct()

        service = self.forwarded.get('service', None)
        addon = self.forwarded.get('service_addon', None)

        return provider_extra_queryset(service, addon, self.q)


# helper method for build_voucher view. Remove once removed that view
def _fetch_resources(uri, rel):
    path = os.path.join(settings.MEDIA_ROOT,
                        uri.replace(settings.MEDIA_URL, ""))
    return path


def render_prices_pdf(request, extra_context=None):
    """
    helper method
    given some extra context with services renders a pdf of prices
    requires a context with:
    - agency: an agency to search prices for
    - services: a list of services to include in list
    - date_from: the starting date to fetch prices
    - date_to: the ending date to fetch prices for
    """
    context = {}
    context.update(extra_context)
    if 'agency' not in context or 'services' not in context:
        # Missing data. no pdf can be rendered
        return redirect(reverse('common:config_service'))
    template = get_template("config/pdf/prices.html")
    context.update({
        'pagesize': 'Letter',
        # 'agency': agency,
        # 'services': services,
        # 'date_from': None,
        # 'date_to': None,
    })
    html = template.render(context)
    result = StringIO()
    pdf = pisa.pisaDocument(StringIO(html),
                            dest=result,
                            link_callback=_fetch_resources)
    if pdf.err:
        messages.add_message(request,
                             messages.ERROR,
                             "Failed Prices PDF Generation")
        return HttpResponseRedirect(reverse('common:config_service'))

    return HttpResponse(result.getvalue(), content_type='application/pdf')


class ServiceAutocompleteView(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        # Don't forget to filter out results depending on the visitor !
        if not self.request.user.is_authenticated():
            return Service.objects.none()
        current_service_id = self.forwarded.get('current_service_id', None)
        search_location = self.forwarded.get('search_location', None)
        qs = Service.objects.filter(enabled=True).distinct()
        if current_service_id:
            qs = qs.exclude(
                id=current_service_id,
            )
        if search_location:
            qs = qs.filter(
                location=search_location,
            )
        if self.q:
            qs = qs.filter(name__icontains=self.q)
        return qs[:20]


class ServiceAllotmentAutocompleteView(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        # Don't forget to filter out results depending on the visitor !
        if not self.request.user.is_authenticated():
            return Allotment.objects.none()
        provider = self.forwarded.get('provider', None)
        location = self.forwarded.get('search_location', None)
        qs = Allotment.objects.filter(enabled=True).distinct()
        if provider:
            qs = qs.filter(
                providerallotmentservice__provider=provider,
            )
        if location:
            qs = qs.filter(
                location=location,
            )
        if self.q:
            qs = qs.filter(name__icontains=self.q)
        return qs[:20]


class ServiceTransferAutocompleteView(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        # Don't forget to filter out results depending on the visitor !
        if not self.request.user.is_authenticated():
            return Transfer.objects.none()
        provider = self.forwarded.get('provider', None)
        location = self.forwarded.get('search_location', None)
        qs = Transfer.objects.filter(enabled=True).distinct()
        if provider:
            qs = qs.filter(
                providertransferservice__provider=provider,
            )
        if location:
            qs = qs.filter(
                location=location,
            )
        if self.q:
            qs = qs.filter(name__icontains=self.q)
        return qs[:20]


class ServiceExtraAutocompleteView(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        # Don't forget to filter out results depending on the visitor !
        if not self.request.user.is_authenticated():
            return Extra.objects.none()
        provider = self.forwarded.get('provider', None)
        location = self.forwarded.get('search_location', None)
        qs = Extra.objects.filter(enabled=True).distinct()
        if provider:
            qs = qs.filter(
                providerextraservice__provider=provider,
            )
        if location:
            qs = qs.filter(
                location=location,
            )
        if self.q:
            qs = qs.filter(name__icontains=self.q)
        return qs[:20]


class CarRentalAutocompleteView(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        # Don't forget to filter out results depending on the visitor !
        if not self.request.user.is_authenticated():
            return CarRental.objects.none()
        qs = CarRental.objects.all()
        if self.q:
            qs = qs.filter(name__icontains=self.q)
        return qs[:20]


class CarRentalOfficeAutocompleteView(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        # Don't forget to filter out results depending on the visitor !
        if not self.request.user.is_authenticated():
            return CarRentalOffice.objects.none()

        detail_service_id = self.forwarded.get('detail_service', None)
        if detail_service_id:
            extra = Extra.objects.get(pk=detail_service_id)
            if extra.car_rental is None:
                return CarRentalOffice.objects.none()
        else:
            service_id = self.forwarded.get('service', None)
            if service_id:
                extra = Extra.objects.get(pk=service_id)
                if extra.car_rental is None:
                    return CarRentalOffice.objects.none()
            else:
                return CarRentalOffice.objects.none()

        qs = CarRentalOffice.objects.filter(car_rental=extra.car_rental)
        if self.q:
            qs = qs.filter(office__icontains=self.q)
        return qs[:20]


class ServiceDetailURLView(View):
    def post(self, request, *args, **kwargs):
        parent_id = request.POST.get('parent_id', None)
        service_id = request.POST.get('service', None)
        if parent_id and service_id:
            service = Service.objects.get(id=service_id)
            if service.category == 'A':
                return JsonResponse({
                    'url': 'config/servicedetailallotment/add/?service=%s&detail_service=%s' % (
                        parent_id, service_id),
                })
            elif service.category == 'T':
                return JsonResponse({
                    'url': 'config/servicedetailtransfer/add/?service=%s&detail_service=%s' % (
                        parent_id, service_id),
                })
            elif service.category == 'E':
                return JsonResponse({
                    'url': 'config/servicedetailextra/add/?service=%s&detail_service=%s' % (
                        parent_id, service_id),
                })
        return JsonResponse({
            'error': 'Empty value Current: %s - Detail: %s' % (parent_id, service_id),
        })
