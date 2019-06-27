# -*- coding: utf-8 -*-
from __future__ import unicode_literals
"""
Config Views
"""

from dal import autocomplete

from config.models import (
    Location, RoomType, Addon, AllotmentBoardType,
    Allotment, Transfer, Extra
)

from django.db.models import Q

from finance.models import (
    Provider
)

from reservas.custom_settings import ADDON_FOR_NO_ADDON


class LocationAutocompleteView(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        # Don't forget to filter out results depending on the visitor !
        if not self.request.user.is_authenticated():
            return Location.objects.none()
        qs = Location.objects.filter(enabled=True).all()
        if self.q:
            qs = qs.filter(name__icontains=self.q)
        return qs[:20]


class RoomTypeAutocompleteView(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        # Don't forget to filter out results depending on the visitor !
        if not self.request.user.is_authenticated():
            return RoomType.objects.none()
        qs = RoomType.objects.filter(enabled=True).all().distinct()

        service = self.forwarded.get('service', None)

        if service:
            qs = qs.filter(allotmentroomtype__allotment=service)

        if self.q:
            qs = qs.filter(name__icontains=self.q)
        return qs[:20]


class BoardTypeAutocompleteView(autocomplete.Select2ListView):
    def get_list(self):
        result = []
        service = self.forwarded.get('service', None)
        if not service is None:
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


class ProviderAllotmentAutocompleteView(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        if not self.request.user.is_authenticated():
            return Provider.objects.none()
        qs = Provider.objects.filter(enabled=True).all().distinct()

        service = self.forwarded.get('service', None)
        if not service:
            return Provider.objects.none()

        room_type = self.forwarded.get('room_type', None)
        board_type = self.forwarded.get('board_type', None)
        addon = self.forwarded.get('service_addon', None)

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

        if self.q:
            qs = qs.filter(name__icontains=self.q)
        return qs[:20]


class TransferAutocompleteView(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        # Don't forget to filter out results depending on the visitor !
        if not self.request.user.is_authenticated():
            return Transfer.objects.none()
        qs = Transfer.objects.filter(enabled=True).all()
        if self.q:
            qs = qs.filter(name__icontains=self.q)
        return qs[:20]


class ProviderTransferAutocompleteView(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        if not self.request.user.is_authenticated():
            return Provider.objects.none()
        qs = Provider.objects.filter(enabled=True).all().distinct()

        service = self.forwarded.get('service', None)
        if not service:
            return Provider.objects.none()

        location_from = self.forwarded.get('location_from', None)
        location_to = self.forwarded.get('location_to', None)
        addon = self.forwarded.get('service_addon', None)

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

        if self.q:
            qs = qs.filter(name__icontains=self.q)
        return qs[:20]


class ExtraAutocompleteView(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        # Don't forget to filter out results depending on the visitor !
        if not self.request.user.is_authenticated():
            return Extra.objects.none()
        qs = Extra.objects.filter(enabled=True).all()
        if self.q:
            qs = qs.filter(name__icontains=self.q)
        return qs[:20]


class ProviderExtraAutocompleteView(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        if not self.request.user.is_authenticated():
            return Provider.objects.none()
        qs = Provider.objects.filter(enabled=True).all().distinct()

        service = self.forwarded.get('service', None)
        if not service:
            return Provider.objects.none()

        addon = self.forwarded.get('service_addon', None)

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

        if self.q:
            qs = qs.filter(name__icontains=self.q)
        return qs[:20]
