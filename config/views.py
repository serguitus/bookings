from dal import autocomplete

from django.db.models import Exists, OuterRef, Subquery, Q, F, Value, DecimalField
from django.utils.encoding import force_text
from django.utils.translation import ugettext

from config.models import (
    Location, RoomType,
    Allotment, AllotmentBoardType, Transfer, Extra
)

from finance.models import (
    Provider
)


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
        room_type = self.forwarded.get('room_type', None)
        board_type = self.forwarded.get('board_type', None)

        if service:
            if room_type:
                if board_type:
                    qs = qs.filter(
                        providerallotmentservice__service=service,
                        providerallotmentservice__providerallotmentdetail__room_type=room_type,
                        providerallotmentservice__providerallotmentdetail__board_type=board_type,
                    )
                else:
                    qs = qs.filter(
                        providerallotmentservice__service=service,
                        providerallotmentservice__providerallotmentdetail__room_type=room_type,
                    )
            elif board_type:
                qs = qs.filter(
                    providerallotmentservice__service=service,
                    providerallotmentservice__providerallotmentdetail__board_type=board_type,
                )
            else:
                qs = qs.filter(
                    providerallotmentservice__service=service,
                )
        elif room_type:
            if board_type:
                qs = qs.filter(
                    providerallotmentservice__providerallotmentdetail__room_type=room_type,
                    providerallotmentservice__providerallotmentdetail__board_type=board_type,
                )
            else:
                qs = qs.filter(
                    providerallotmentservice__providerallotmentdetail__room_type=room_type,
                )
        elif board_type:
            qs = qs.filter(
                providerallotmentservice__providerallotmentdetail__board_type=board_type,
            )

        if self.q:
            qs = qs.filter(name__icontains=self.q)
        return qs[:20]


class TransferAutocompleteView(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        # Don't forget to filter out results depending on the visitor !
        if not self.request.user.is_authenticated():
            return Allotment.objects.none()
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
        location_from = self.forwarded.get('location_from', None)
        location_to = self.forwarded.get('location_to', None)

        if service:
            if location_from:
                if location_to:
                    qs = qs.filter(
                        providertransferservice__service=service,
                        providertransferservice__providertransferdetail__p_location_from=location_from,
                        providertransferservice__providertransferdetail__p_location_to=location_to,
                    )
                else:
                    qs = qs.filter(
                        providertransferservice__service=service,
                        providertransferservice__providertransferdetail__p_location_from=location_from,
                    )
            elif location_to:
                qs = qs.filter(
                    providertransferservice__service=service,
                    providertransferservice__providertransferdetail__p_location_to=location_to,
                )
            else:
                qs = qs.filter(
                    providertransferservice__service=service,
                )
        elif location_from:
            if location_to:
                qs = qs.filter(
                    providertransferservice__providertransferdetail__p_location_from=location_from,
                    providertransferservice__providertransferdetail__p_location_to=location_to
                )
            else:
                qs = qs.filter(
                    providertransferservice__providertransferdetail__p_location_from=location_from,
                )
        elif location_to:
            qs = qs.filter(
                providertransferservice__providertransferdetail__p_location_to=location_to,
            )

        if self.q:
            qs = qs.filter(name__icontains=self.q)
        return qs[:20]


class ExtraAutocompleteView(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        # Don't forget to filter out results depending on the visitor !
        if not self.request.user.is_authenticated():
            return Allotment.objects.none()
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

        if service:
            qs = qs.filter(
                providerextraservice__service=service,
            )

        if self.q:
            qs = qs.filter(name__icontains=self.q)
        return qs[:20]


