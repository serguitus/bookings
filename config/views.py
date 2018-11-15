from dal import autocomplete

from django.db.models import Exists, OuterRef, Subquery, Q, F, Value, DecimalField
from django.utils.encoding import force_text
from django.utils.translation import ugettext

from config.models import Location, RoomType, Allotment, Transfer, Extra


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


class AllotmentAutocompleteView(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        # Don't forget to filter out results depending on the visitor !
        if not self.request.user.is_authenticated():
            return Allotment.objects.none()
        qs = Allotment.objects.filter(enabled=True).all()
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


class ExtraAutocompleteView(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        # Don't forget to filter out results depending on the visitor !
        if not self.request.user.is_authenticated():
            return Allotment.objects.none()
        qs = Extra.objects.filter(enabled=True).all()
        if self.q:
            qs = qs.filter(name__icontains=self.q)
        return qs[:20]


