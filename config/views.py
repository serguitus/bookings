from dal import autocomplete

from django.db.models import Exists, OuterRef, Subquery, Q, F, Value, DecimalField
from django.utils.encoding import force_text
from django.utils.translation import ugettext

from config.models import Location, RoomType


class LocationAutocompleteView(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        # Don't forget to filter out results depending on the visitor !
        if not self.request.user.is_authenticated():
            return Location.objects.none()
        qs = Location.objects.filter(enabled=True).all()
        if self.q:
            qs = qs.filter(name__icontains=self.q)
        return qs


class RoomTypeAutocompleteView(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        # Don't forget to filter out results depending on the visitor !
        if not self.request.user.is_authenticated():
            return RoomType.objects.none()
        qs = RoomType.objects.filter(enabled=True).all()
        if self.q:
            qs = qs.filter(name__icontains=self.q)
        return qs
