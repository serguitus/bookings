
"""
Views of general use
"""

from dal import autocomplete

from django.db.models import Manager


class DisabledAutocompleteView(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        return Manager().none()
