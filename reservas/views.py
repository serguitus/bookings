
"""
Views of general use
"""

from dal import autocomplete

from django.db.models import Manager
from django.shortcuts import render
from django.views import View

class DisabledAutocompleteView(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        return Manager().none()


class AngularAppView(View):
    def get(self):
        return render('angular_index.html')
