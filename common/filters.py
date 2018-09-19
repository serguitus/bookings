from django.db import models
from django.contrib.admin.filters import FieldListFilter, DateFieldListFilter
from django.contrib.admin.utils import lookup_needs_distinct
from django.utils.text import capfirst

PARAM_PREFIX = 'srch_'

class TopFilter(object):
    _top_filters = []
    _take_priority_index = 0
    template = 'common/filters/top_filter.html'

    def __init__(self, field, request, params, hidden_params, model, model_admin, field_path):
        self.field = field
        self.model = model
        self.field_path = field_path
        self.title = capfirst(getattr(field, 'verbose_name', field_path))
        self._parameters = self.get_parameters(field, model, model_admin, field_path)
        self._values = self._extract_values(params, hidden_params)
        self.context = self.get_context()

    @classmethod
    def register(cls, test, top_filter_class, take_priority=False):
        if take_priority:
            # This is to allow overriding the default filters for certain types
            # of fields with some custom filters. The first found in the list
            # is used in priority.
            cls._top_filters.insert(
                cls._take_priority_index, (test, top_filter_class))
            cls._take_priority_index += 1
        else:
            cls._top_filters.append((test, top_filter_class))

    @classmethod
    def create(cls, field, request, params, hidden_params, model, model_admin, field_path):
        for test, top_filter_class in cls._top_filters:
            if not test(field):
                continue
            return top_filter_class(field, request, params, hidden_params, model, model_admin, field_path=field_path)
        return TopFilter(field, request, params, hidden_params, model, model_admin, field_path=field_path)

    def get_parameters(self, field, model, model_admin, field_path):
        return ('%s%s' % (PARAM_PREFIX, field_path),)

    def _extract_values(self, params, hidden_params):
        result = []
        for parameter in self._parameters:
            if parameter in hidden_params:
                hidden_params.pop(parameter)
            if parameter in params:
                value = params.pop(parameter)
            else:
                value = ''
            result.append(value)
        return result

    def get_context(self):
        return {
            'field': self.field,
            'field_path': self.field_path,
            'title': self.title,
            'parameters': self._parameters,
            'values': self._values,
        }

    def queryset(self, request, queryset):
        return queryset


class TextFilter(TopFilter):
    template = 'common/filters/text_top_filter.html'

    def queryset(self, request, queryset):
        search_terms = self._values[0]
        if search_terms:
            lookup = '%s__icontains' % self.field_path
            if lookup_needs_distinct(self.model._meta, lookup):
                queryset = queryset.distinct()
            for bit in search_terms.split():
                if bit.startswith('!'):
                    queryset = queryset.exclude(**{lookup: bit[1:]})
                else:
                    queryset = queryset.filter(**{lookup: bit})
        return queryset


TopFilter.register(lambda f: isinstance(f, (models.CharField,)), TextFilter)
