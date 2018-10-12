from dal import autocomplete

from django import forms
from django.contrib.admin.filters import FieldListFilter, DateFieldListFilter
from django.contrib.admin.utils import lookup_needs_distinct
from django.contrib.admin.widgets import AdminDateWidget
from django.core.exceptions import ImproperlyConfigured
from django.db import models
from django.forms.widgets import Media, MEDIA_TYPES
from django.utils.text import capfirst

PARAM_PREFIX = 'srch_'

class TopFilter(object):
    _top_filters = []
    _take_priority_index = 0
    _support_array = False
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
                if self._support_array:
                    if '' in value:
                        value.remove('')
                else:
                    value = value[0]
            else:
                value = []
                if not self._support_array:
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
        if search_terms and search_terms != '':
            lookup = '%s__icontains' % self.field_path
            if lookup_needs_distinct(self.model._meta, lookup):
                queryset = queryset.distinct()
            for bit in search_terms.split():
                if bit.startswith('!'):
                    queryset = queryset.exclude(**{lookup: bit[1:]})
                else:
                    queryset = queryset.filter(**{lookup: bit})
        return queryset


TopFilter.register(lambda f: isinstance(f, (models.CharField,)) and not bool(f.choices), TextFilter)


class BooleanFilter(TopFilter):
    template = 'common/filters/boolean_top_filter.html'

    def queryset(self, request, queryset):
        search_option = self._values[0]
        if search_option and search_option != '':
            lookup = '%s__exact' % self.field_path
            if lookup_needs_distinct(self.model._meta, lookup):
                queryset = queryset.distinct()
            if search_option == "True":
                queryset = queryset.filter(**{lookup: True})
            if search_option == "False":
                queryset = queryset.filter(**{lookup: False})
        return queryset


TopFilter.register(lambda f: isinstance(f, (models.BooleanField,)), BooleanFilter)

class ChoicesFilter(TopFilter):
    _support_array = True
    template = 'common/filters/choices_top_filter.html'
    widget_attrs = {}
    choices = None

    def __init__(self, field, request, params, hidden_params, model, model_admin, field_path):
    
        super(ChoicesFilter, self).__init__(
            field, request, params, hidden_params, model, model_admin, field_path)

        choices = self.choices
        if choices is None:
            choices = self.field.choices

        field = forms.MultipleChoiceField(
            choices=choices,
            required=False,
            widget=autocomplete.Select2Multiple()
        )

        self._add_media(model_admin)

        attrs = self.widget_attrs.copy()
        attrs['id'] = 'id-%s-dal-filter' % self.field_path
        attrs['data-placeholder'] = self.title

        rendered_widget = field.widget.render(
            name=self._parameters[0],
            value=self._values[0],
            attrs=attrs
        )

        self.context.update({'rendered_widget': rendered_widget})

    def _add_media(self, model_admin):

        if not hasattr(model_admin, 'Media'):
            raise ImproperlyConfigured('Add empty Media class to %s. Sorry about this bug.' % model_admin)

        def _get_media(obj):
            return Media(media=getattr(obj, 'Media', None))

        media = _get_media(model_admin) + _get_media(autocomplete.Select2Multiple) + _get_media(self)

        for name in MEDIA_TYPES:
            setattr(model_admin.Media, name, getattr(media, "_" + name))

    def queryset(self, request, queryset):
        search_option = self._values[0]
        if search_option and search_option != []:
            lookup = '%s__in' % self.field_path
            if lookup_needs_distinct(self.model._meta, lookup):
                queryset = queryset.distinct()
            queryset = queryset.filter(**{lookup: search_option})
        return queryset


TopFilter.register(lambda f: isinstance(f, (models.CharField,)) and bool(f.choices), ChoicesFilter)


class ForeignKeyFilter(TopFilter):
    _support_array = True
    template = 'common/filters/foreignkey_top_filter.html'
    widget_attrs = {}
    autocomplete_url = None

    def __init__(self, field, request, params, hidden_params, model, model_admin, field_path):

        super(ForeignKeyFilter, self).__init__(
            field, request, params, hidden_params, model, model_admin, field_path)

        field = forms.ModelChoiceField(
            queryset=getattr(model, self.field_path).get_queryset(),
            required=False,
            empty_label='',
            widget=autocomplete.ModelSelect2Multiple(
                url=self.autocomplete_url,
            )
        )

        self._add_media(model_admin)

        attrs = self.widget_attrs.copy()
        attrs['id'] = 'id-%s-dal-filter' % self.field_path
        attrs['data-placeholder'] = self.title

        rendered_widget = field.widget.render(
            name=self._parameters[0],
            value=self._values[0],
            attrs=attrs
        )

        self.context.update({'rendered_widget': rendered_widget})

    def _add_media(self, model_admin):

        if not hasattr(model_admin, 'Media'):
            raise ImproperlyConfigured('Add empty Media class to %s. Sorry about this bug.' % model_admin)

        def _get_media(obj):
            return Media(media=getattr(obj, 'Media', None))

        media = _get_media(model_admin) + _get_media(autocomplete.ModelSelect2Multiple) + _get_media(self)

        for name in MEDIA_TYPES:
            setattr(model_admin.Media, name, getattr(media, "_" + name))

    def queryset(self, request, queryset):
        search_option = self._values[0]
        if search_option and search_option != []:
            lookup = '%s%s__in' % (self.field_path, '_id')
            if lookup_needs_distinct(self.model._meta, lookup):
                queryset = queryset.distinct()
            queryset = queryset.filter(**{lookup: search_option})
        return queryset


TopFilter.register(lambda f: isinstance(f, (models.ForeignKey,)), ForeignKeyFilter)


class DateFilter(TopFilter):
    template = 'common/filters/date_top_filter.html'
    widget_attrs = {}

    def get_parameters(self, field, model, model_admin, field_path):
        return ('%s%s_from' % (PARAM_PREFIX, field_path),'%s%s_to' % (PARAM_PREFIX, field_path),)

    class Media:
        css = {
            'all': (
                'common/css/widgets.css',
            )
        }

    def __init__(self, field, request, params, hidden_params, model, model_admin, field_path):

        super(DateFilter, self).__init__(
            field, request, params, hidden_params, model, model_admin, field_path)

        widget = AdminDateWidget()

        self._add_media(model_admin, widget)

        from_widget = widget.render(
            name=self._parameters[0],
            value=self._values[0],
        )

        to_widget = widget.render(
            name=self._parameters[1],
            value=self._values[1],
        )

        self.context.update({
            'from_widget': from_widget,
            'to_widget': to_widget,
        })

    def _add_media(self, model_admin, widget):
    
        if not hasattr(model_admin, 'Media'):
            raise ImproperlyConfigured('Add empty Media class to %s. Sorry about this bug.' % model_admin)

        def _get_media(obj):
            return Media(media=getattr(obj, 'Media', None))

        media = _get_media(model_admin) + widget.media + _get_media(DateFilter) + _get_media(self)

        for name in MEDIA_TYPES:
            setattr(model_admin.Media, name, getattr(media, "_" + name))

    def queryset(self, request, queryset):
        from_option = self._values[0]
        if from_option and from_option != "" and from_option != "''":
            lookup = '%s__gte' % self.field_path
            if lookup_needs_distinct(self.model._meta, lookup):
                queryset = queryset.distinct()
            queryset = queryset.filter(**{lookup: from_option})

        to_option = self._values[1]
        if to_option and to_option != "" and to_option != "''":
            lookup = '%s__lte' % self.field_path
            if lookup_needs_distinct(self.model._meta, lookup):
                queryset = queryset.distinct()
            queryset = queryset.filter(**{lookup: to_option})

        return queryset


TopFilter.register(lambda f: isinstance(f, (models.DateField,)), DateFilter)
