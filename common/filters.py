from django.db import models
from django.contrib.admin.filters import FieldListFilter, DateFieldListFilter


class TopFilter(object):
    _top_filters = []
    _take_priority_index = 0
    template = 'common/filters/top_filter.html'

    def __init__(self, field, request, params, model, model_admin, field_path):
        self.field = field
        self.field_path = field_path
        self.title = getattr(field, 'verbose_name', field_path)

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
    def create(cls, field, request, params, model, model_admin, field_path):
        for test, top_filter_class in cls._top_filters:
            if not test(field):
                continue
            return top_filter_class(field, request, params, model, model_admin, field_path=field_path)
        return TopFilter(field, request, params, model, model_admin, field_path=field_path)


class TextFilter(TopFilter):
    parameter_name = None
    template = 'common/filters/text_top_filter.html'

    def __init__(self, field, request, params, model, model_admin, field_path):
        super().__init__(field, request, params, model, model_admin, field_path)
        if self.parameter_name is None:
            self.parameter_name = self.field.name
        if self.parameter_name in params:
            value = params.pop(self.parameter_name)
            self.used_parameters[self.parameter_name] = value

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(**self.used_parameters)

    def value(self):
        """
        Returns the value (in string format) provided in the request's
        query string for this filter, if any. If the value wasn't provided then
        returns None.
        """
        return self.used_parameters.get(self.parameter_name, None)
        
    def has_output(self):
        return True

    def expected_parameters(self):
        """
        Returns the list of parameter names that are expected from the
        request's query string and that will be used by this filter.
        """
        return ['%s__icontains' % self.parameter_name]

    def choices(self, cl):
        return ({
            'parameter_name': self.parameter_name,
            'current_value': self.value(),
            'get_query': cl.params,
        }, )
