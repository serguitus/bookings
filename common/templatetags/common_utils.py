from __future__ import unicode_literals
import datetime
import warnings

from django import template
from django.contrib.admin.templatetags.admin_list import (
    _coerce_field_name, result_headers, result_hidden_fields)
from django.contrib.admin.utils import (
    display_for_field, display_for_value, get_fields_from_path,
    label_for_field, lookup_field)
from django.contrib.admin.views.main import ALL_VAR, SEARCH_VAR
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.template.context import Context
from django.urls import NoReverseMatch, Resolver404, get_script_prefix, resolve
from django.utils.deprecation import RemovedInDjango20Warning
from django.utils.encoding import force_text
from django.utils.html import format_html
from django.utils.http import urlencode
from django.utils.safestring import mark_safe
from django.utils.six.moves.urllib.parse import parse_qsl, urlparse, urlunparse


register = template.Library()

DOT = '.'

@register.filter
def substract_days(value, arg):
    return value - datetime.timedelta(days=arg)

@register.filter
def substract(value, arg):
    return value - arg

@register.assignment_tag
def setvar(val=None):
    return val

@register.inclusion_tag('common/pagination.html')
def common_pagination(cl):
    """
    Generates the series of links to the pages in a paginated list.
    """
    paginator, page_num = cl.paginator, cl.page_num

    pagination_required = (not cl.show_all or not cl.can_show_all) and cl.multi_page
    if not pagination_required:
        page_range = []
    else:
        ON_EACH_SIDE = 3
        ON_ENDS = 2

        # If there are 10 or fewer pages, display links to every page.
        # Otherwise, do some fancy
        if paginator.num_pages <= 10:
            page_range = range(paginator.num_pages)
        else:
            # Insert "smart" pagination links, so that there are always ON_ENDS
            # links at either end of the list of pages, and there are always
            # ON_EACH_SIDE links at either end of the "current page" link.
            page_range = []
            if page_num > (ON_EACH_SIDE + ON_ENDS):
                page_range.extend(range(0, ON_ENDS))
                page_range.append(DOT)
                page_range.extend(range(page_num - ON_EACH_SIDE, page_num + 1))
            else:
                page_range.extend(range(0, page_num + 1))
            if page_num < (paginator.num_pages - ON_EACH_SIDE - ON_ENDS - 1):
                page_range.extend(range(page_num + 1, page_num + ON_EACH_SIDE + 1))
                page_range.append(DOT)
                page_range.extend(range(paginator.num_pages - ON_ENDS, paginator.num_pages))
            else:
                page_range.extend(range(page_num + 1, paginator.num_pages))

    need_show_all_link = cl.can_show_all and not cl.show_all and cl.multi_page
    return {
        'cl': cl,
        'pagination_required': pagination_required,
        'show_all_url': need_show_all_link and cl.get_query_string({ALL_VAR: ''}),
        'page_range': page_range,
        'ALL_VAR': ALL_VAR,
        '1': 1,
    }


@register.simple_tag(takes_context=True)
def common_add_preserved_filters(context, url, popup=False, to_field=None):
    opts = context.get('opts')
    preserved_filters = context.get('preserved_filters')

    parsed_url = list(urlparse(url))
    parsed_qs = dict(parse_qsl(parsed_url[4]))
    merged_qs = dict()

    if opts and preserved_filters:
        preserved_filters = dict(parse_qsl(preserved_filters))

        match_url = '/%s' % url.partition(get_script_prefix())[2]
        try:
            match = resolve(match_url)
        except Resolver404:
            pass
        else:
            current_url = '%s:%s' % (match.app_name, match.url_name)
            namespace = 'common'
            if context.get('site_namespace'):
                namespace = context.get('site_namespace')
            changelist_url = '%s:%s_%s_changelist' % (namespace, opts.app_label, opts.model_name)
            if changelist_url == current_url and '_changelist_filters' in preserved_filters:
                preserved_filters = dict(parse_qsl(preserved_filters['_changelist_filters']))

        merged_qs.update(preserved_filters)

    if popup:
        from django.contrib.admin.options import IS_POPUP_VAR
        merged_qs[IS_POPUP_VAR] = 1
    if to_field:
        from django.contrib.admin.options import TO_FIELD_VAR
        merged_qs[TO_FIELD_VAR] = to_field

    merged_qs.update(parsed_qs)

    parsed_url[4] = urlencode(merged_qs)
    return urlunparse(parsed_url)

def _items_for_result(cl, result, form, namespace='common'):
    """
    Generates the actual list of data.
    """

    def link_in_col(is_first, field_name, cl):
        if cl.list_display_links is None:
            return False
        if is_first and not cl.list_display_links:
            return True
        return field_name in cl.list_display_links

    first = True
    pk = cl.lookup_opts.pk.attname
    for field_index, field_name in enumerate(cl.list_display):
        empty_value_display = cl.model_admin.get_empty_value_display()
        row_classes = ['field-%s' % _coerce_field_name(field_name, field_index)]
        try:
            f, attr, value = lookup_field(field_name, result, cl.model_admin)
        except ObjectDoesNotExist:
            result_repr = empty_value_display
        else:
            empty_value_display = getattr(attr, 'empty_value_display', empty_value_display)
            if f is None or f.auto_created:
                if field_name == 'action_checkbox':
                    row_classes.append('action-checkbox')
                if field_name == 'details_button':
                    row_classes.append('details-button')
                allow_tags = getattr(attr, 'allow_tags', False)
                boolean = getattr(attr, 'boolean', False)
                result_repr = display_for_value(value, empty_value_display, boolean)
                if allow_tags:
                    warnings.warn(
                        "Deprecated allow_tags attribute used on field {}. "
                        "Use django.utils.html.format_html(), format_html_join(), "
                        "or django.utils.safestring.mark_safe() instead.".format(field_name),
                        RemovedInDjango20Warning
                    )
                    result_repr = mark_safe(result_repr)
                if isinstance(value, (datetime.date, datetime.time)):
                    row_classes.append('nowrap')
            else:
                if isinstance(f.remote_field, models.ManyToOneRel):
                    field_val = getattr(result, f.name)
                    if field_val is None:
                        result_repr = empty_value_display
                    else:
                        result_repr = field_val
                else:
                    result_repr = display_for_field(value, f, empty_value_display)
                if isinstance(f, (models.DateField, models.TimeField, models.ForeignKey)):
                    row_classes.append('nowrap')
        if force_text(result_repr) == '':
            result_repr = mark_safe('&nbsp;')
        row_class = mark_safe(' class="%s"' % ' '.join(row_classes))
        # If list_display_links not defined, add the link tag to the first field
        if link_in_col(first, field_name, cl):
            table_tag = 'th' if first else 'td'
            first = False

            # Display link to the result's change_view if the url exists, else
            # display just the result's representation.
            try:
                url = cl.url_for_result(result)
            except NoReverseMatch:
                link_or_text = result_repr
            else:
                url = common_add_preserved_filters({'preserved_filters': cl.preserved_filters, 'opts': cl.opts}, url)
                # Convert the pk to something that can be used in Javascript.
                # Problem cases are long ints (23L) and non-ASCII strings.
                if cl.to_field:
                    attr = str(cl.to_field)
                else:
                    attr = pk
                value = result.serializable_value(attr)
                link_or_text = format_html(
                    '<a href="{}"{}>{}</a>',
                    url,
                    format_html(
                        ' data-popup-opener="{}"', value
                    ) if cl.is_popup else '',
                    result_repr)

            yield format_html('<{}{}>{}</{}>',
                              table_tag,
                              row_class,
                              link_or_text,
                              table_tag)
        else:
            # By default the fields come from ModelAdmin.list_editable, but if we pull
            # the fields out of the form instead of list_editable custom admins
            # can provide fields on a per request basis
            if (form and field_name in form.fields and not (
                    field_name == cl.model._meta.pk.name and
                    form[cl.model._meta.pk.name].is_hidden)):
                bf = form[field_name]
                result_repr = mark_safe(force_text(bf.errors) + force_text(bf))
            yield format_html('<td{}>{}</td>', row_class, result_repr)
    if form and not form[cl.model._meta.pk.name].is_hidden:
        yield format_html('<td>{}</td>', force_text(form[cl.model._meta.pk.name]))


def _results(cl, namespace='common'):
    from common.sites import ResultList

    if cl.formset:
        for res, form in zip(cl.result_list, cl.formset.forms):
            res.row_classes = cl.row_classes_for_result(res)
            yield ResultList(form, res, _items_for_result(cl, res, form, namespace))
    else:
        for res in cl.result_list:
            res.row_classes = cl.row_classes_for_result(res)
            yield ResultList(None, res, _items_for_result(cl, res, None, namespace))


@register.inclusion_tag("common/change_list_results.html")
def common_result_list(cl, totals=None,
                       unit_of_measure='', namespace='common'):
    """
    Displays the headers and data list together
    totals: contains totals for certain columns
    unit_of_measure: just symbols for those totals
    """
    headers = list(result_headers(cl))
    num_sorted_fields = 0
    for h in headers:
        if h['sortable'] and h['sorted']:
            num_sorted_fields += 1
    return {'cl': cl,
            'result_hidden_fields': list(result_hidden_fields(cl)),
            'result_headers': headers,
            'num_sorted_fields': num_sorted_fields,
            'totals': totals,
            'unit_of_measure': unit_of_measure,
            'results': list(_results(cl, namespace))}


@register.inclusion_tag('common/submit_line.html', takes_context=True)
def common_submit_row(context):
    """
    Displays the row of buttons for delete and save.
    """
    change = context['change']
    is_popup = context['is_popup']
    save_as = context['save_as']
    show_save = context.get('show_save', True)
    show_save_and_continue = context.get('show_save_and_continue', True)
    show_cancel = context.get('show_cancel', True)
    ctx = Context(context)
    ctx.update({
        'change_actions': context['change_actions'],
        'show_delete_link': (
            not is_popup and context['has_delete_permission'] and
            change and context.get('show_delete', True)
        ),
        'show_save_as_new': not is_popup and change and save_as,
        'show_save_and_add_another': (
            context['has_add_permission'] and not is_popup and context['add']
        ),
        'show_save_and_continue': not is_popup and context['has_change_permission'] and show_save_and_continue,
        'show_save': show_save,
        'show_cancel': show_cancel,
    })
    return ctx

@register.inclusion_tag('common/search_form.html')
def common_search_form(cl):
    """
    Displays a search form for searching the list.
    """
    return {
        'cl': cl,
        'show_result_count': cl.result_count != cl.full_result_count,
        'search_var': SEARCH_VAR
    }
