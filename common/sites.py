# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import copy
import datetime
import json
import string
import sys

from functools import update_wrapper
from totalsum.admin import TotalsumAdmin

from django.contrib import messages
from django.contrib.admin import helpers
from django.contrib.admin.exceptions import DisallowedModelAdminLookup, DisallowedModelAdminToField
from django.contrib.admin.options import (
    InlineModelAdmin, csrf_protect_m, TO_FIELD_VAR, IS_POPUP_VAR, #ModelAdmin,
    IncorrectLookupParameters,)
from django.contrib.admin.sites import AdminSite
from django.contrib.admin.templatetags.admin_list import _coerce_field_name, result_headers
from django.contrib.admin.utils import (
    quote, unquote, get_deleted_objects, get_fields_from_path,
    lookup_field, lookup_needs_distinct, label_for_field,
    prepare_lookup_value, display_for_field, display_for_value)
from django.contrib.admin.views.main import SEARCH_VAR, IGNORED_PARAMS, ChangeList
from django.contrib.admin.widgets import RelatedFieldWidgetWrapper
from django.contrib.auth import get_permission_codename, logout as auth_logout
from django.core.exceptions import (
    ValidationError, PermissionDenied, ObjectDoesNotExist,
    SuspiciousOperation, ImproperlyConfigured, FieldDoesNotExist)
from django.db import router, transaction, models
from django.db.utils import IntegrityError
from django.forms import fields_for_model
from django.forms.formsets import all_valid, DELETION_FIELD_NAME
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.template.response import TemplateResponse, SimpleTemplateResponse
from django.utils.html import format_html
from django.utils.http import urlencode, urlquote
from django.utils.encoding import force_text
from django.utils import six, timezone
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _, ungettext, ugettext_lazy
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views.generic import RedirectView, View

from common.filters import PARAM_PREFIX, TopFilter
from common.models import RecentLink
from common.templatetags.common_utils import common_add_preserved_filters, result_hidden_fields


class CommonSite(AdminSite):

    site_namespace = 'common'

    site_title = ugettext_lazy('Common Site')
    current_model = None

    index_template = 'common/index.html'
    password_change_template = 'registration/password_change.html'
    password_change_done_template = 'registration/password_change_done.html'

    def get_urls(self):
        from django.conf.urls import url, include
        # Since this module gets imported in the application's root package,
        # it cannot import models from other applications at the module level,
        # and django.contrib.contenttypes.views imports ContentType.
        from django.contrib.contenttypes import views as contenttype_views

        def wrap(view, cacheable=False):
            def wrapper(*args, **kwargs):
                return self.admin_view(view, cacheable)(*args, **kwargs)
            wrapper.admin_site = self
            return update_wrapper(wrapper, view)

        # Admin-site-wide views.
        urlpatterns = [
            url(r'^$', wrap(self.index), name='index'),
            url(r'^login/$', self.login, name='login'),
            url(r'^logout/$', wrap(self.logout), name='logout'),
            url(
                r'^password_change/$',
                wrap(self.password_change, cacheable=True),
                name='password_change'),
            url(
                r'^password_change/done/$',
                wrap(self.password_change_done, cacheable=True),
                name='password_change_done'),
            url(r'^jsi18n/$', wrap(self.i18n_javascript, cacheable=True), name='jsi18n'),
        ]

        # Add in each model's views, and create a list of valid URLS for the
        # app_index
        for model, model_admin in self._registry.items():
            urlpatterns += [
                url(
                    r'^%s/%s/' % (model._meta.app_label, model._meta.model_name),
                    include(model_admin.urls)),
            ]

        return urlpatterns

    @property
    def urls(self):
        return self.get_urls(), self.site_namespace, self.name

    def index_url(self):
        return '%s:index' % self.site_namespace

    def login_url(self):
        return '%s:login' % self.site_namespace

    def logout_url(self):
        return '%s:logout' % self.site_namespace

    def model_action_url_format(self, action):
        return '%s:%%s_%%s_%s' % (self.site_namespace, action)

    def admin_view(self, view, cacheable=False):
        def inner(request, *args, **kwargs):
            if not self.has_permission(request):
                if request.path == reverse(self.logout_url(), current_app=self.name):
                    index_path = reverse(self.index_url(), current_app=self.name)
                    return HttpResponseRedirect(index_path)
                # Inner import to prevent django.contrib.admin (app) from
                # importing django.contrib.auth.models.User (unrelated model).
                from django.contrib.auth.views import redirect_to_login
                return redirect_to_login(
                    request.get_full_path(),
                    reverse(self.login_url(), current_app=self.name)
                )
            return view(request, *args, **kwargs)
        if not cacheable:
            inner = never_cache(inner)
        # We add csrf_protect here so this function can be used as a utility
        # function for any view, without having to repeat 'csrf_protect'.
        if not getattr(view, 'csrf_exempt', False):
            inner = csrf_protect(inner)
        return update_wrapper(inner, view)

    def _build_menu_dict(self, request, current_app=None, current_model=None):
        """
        Builds the menu dictionary.
        """
        menu_dict = {}

        models = self._registry

        for model, site_model in models.items():
            menu_label = site_model.menu_label

            if menu_label is None:
                continue

            has_module_perms = site_model.has_module_permission(request)
            if not has_module_perms:
                continue

            perms = site_model.get_model_perms(request)

            # Check whether user has any perm for this module.
            # If so, add the module to the model_list.
            if True not in perms.values():
                continue

            label = site_model.menu_option
            if not label:
                label = model._meta.verbose_name_plural

            model_index_action = site_model.model_index_action

            index_url = None
            if model_index_action:
                try:
                    index_url = reverse(
                        self.model_action_url_format(model_index_action) % (model._meta.app_label, model._meta.model_name),
                        current_app=self.name)
                except Exception as ex:
                    print(ex)
                    index_url = None
            if not index_url:
                try:
                    index_url = reverse(
                        self.model_action_url_format('changelist') % (model._meta.app_label, model._meta.model_name),
                        current_app=self.name)
                except Exception as ex:
                    print(ex)
                    index_url = None

            model_dict = {
                'order': site_model.model_order,
                'app_label': model._meta.app_label,
                'name': model._meta.model_name,
                'label': label,
                'group': site_model.menu_group,
                'index_url': index_url,
                'perms': perms,
                'actions': site_model.get_model_actions(request),
            }

            if menu_label in menu_dict:
                if site_model.model_order < menu_dict[menu_label]['order']:
                    menu_dict[menu_label]['order'] = site_model.model_order
                menu_dict[menu_label]['model_list'].append(model_dict)
            else:
                menu_dict[menu_label] = {
                    'order': site_model.model_order,
                    'label': menu_label,
                    'has_module_perms': has_module_perms,
                    'model_list': [model_dict],
                }
        return menu_dict

    def get_app_list(self, request):
        """
        Returns a sorted list of menu options from registered models in this site
        available to current user.
        """
        menu_dict = self._build_menu_dict(request)

        # Sort the menus by their order.
        menu_list = sorted(menu_dict.values(), key=lambda x: x['order'])

        # Sort the submenus alphabetically within each menu.
        for menu in menu_list:
            menu['model_list'].sort(key=lambda x: x['order'])

        return menu_list

    def find_recents(self, request, limit=20):
        if request.user:
            return RecentLink.objects.filter(user__pk=request.user.pk)[:int(limit)]
        return None

    def get_site_extra_context(self, request):
        app_list = self.get_app_list(request)
        context = dict(
            app_list=app_list,
            site_namespace=self.site_namespace,
            recent_links=self.find_recents(request),
        )
        return context

    @never_cache
    def index(self, request, extra_context=None):
        """
        Displays the main admin index page, which lists all of the installed
        apps that have been registered in this site.
        """
        context = dict(
            self.each_context(request),
        )
        context.update(self.get_site_extra_context(request))
        context.update(extra_context or {})
        request.current_app = self.name
        return TemplateResponse(request, self.index_template, context)

    def password_change(self, request, extra_context=None):
        """
        Handles the "change password" task -- both form display and validation.
        """
        from django.contrib.admin.forms import AdminPasswordChangeForm
        from django.contrib.auth.views import PasswordChangeView

        site_context = self.get_site_extra_context(request)
        site_context.update(extra_context or {})

        url = reverse('%s:password_change_done' % self.site_namespace, current_app=self.name)
        defaults = {
            'form_class': AdminPasswordChangeForm,
            'success_url': url,
            'extra_context': dict(self.each_context(request), **(site_context)),
        }
        if self.password_change_template is not None:
            defaults['template_name'] = self.password_change_template
        request.current_app = self.name
        return PasswordChangeView.as_view(**defaults)(request)

    @never_cache
    def logout(self, request, extra_context=None):
        """
        Logs out the user for the given HttpRequest.

        This should *not* assume the user is already logged in.
        """
        auth_logout(request)
        index_path = reverse('%s:index' % self.site_namespace, current_app=self.name)

        from django.contrib.auth.views import redirect_to_login

        return redirect_to_login(
            index_path,
            reverse('%s:login' % self.site_namespace, current_app=self.name)
        )


class CommonRelatedFieldWidgetWrapper(RelatedFieldWidgetWrapper):

    def get_related_url(self, info, action, *args):
        return reverse(
            "common:%s_%s_%s" % (info + (action,)),
            current_app=self.admin_site.name,
            args=args)


class SiteModel(TotalsumAdmin):
    save_on_top = True
    site_actions = []
    add_readonly_fields = ()
    change_readonly_fields = ()
    top_filters = ()
    details_template = None
    readonly_model = False
    delete_allowed = True
    self_inlines = []
    list_view = None

    model_actions = []
    model_order = -1
    menu_label = None
    menu_group = None
    menu_option = None
    model_index_action = 'changelist'

    """
    actions are dict with name, label
    """
    change_actions = []

    add_form_template = 'common/change_form.html'
    change_form_template = 'common/change_form.html'
    change_list_template = 'common/change_list.html'
    delete_confirmation_template = 'common/delete_confirmation.html'
    delete_selected_confirmation_template = 'common/delete_selected_confirmation.html'
    object_history_template = 'common/object_history.html'
    popup_response_template = None

    recent_allowed = False


    class Media:
        pass

    def related_field_widget_wrapper_class(self):
        return CommonRelatedFieldWidgetWrapper

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        """
        Hook for specifying the form Field instance for a given database Field
        instance.

        If kwargs are given, they're passed to the form Field's constructor.
        """
        # If the field specifies choices, we don't need to look for special
        # admin widgets - we just need to use a select widget of some kind.
        if db_field.choices:
            return self.formfield_for_choice_field(db_field, request, **kwargs)

        # ForeignKey or ManyToManyFields
        if isinstance(db_field, models.ManyToManyField) or isinstance(db_field, models.ForeignKey):
            # Combine the field kwargs with any options for formfield_overrides.
            # Make sure the passed in **kwargs override anything in
            # formfield_overrides because **kwargs is more specific, and should
            # always win.
            if db_field.__class__ in self.formfield_overrides:
                kwargs = dict(self.formfield_overrides[db_field.__class__], **kwargs)

            # Get the correct formfield.
            if isinstance(db_field, models.ForeignKey):
                formfield = self.formfield_for_foreignkey(db_field, request, **kwargs)
            elif isinstance(db_field, models.ManyToManyField):
                formfield = self.formfield_for_manytomany(db_field, request, **kwargs)

            # For non-raw_id fields, wrap the widget with a wrapper that adds
            # extra HTML -- the "add other" interface -- to the end of the
            # rendered output. formfield can be None if it came from a
            # OneToOneField with parent_link=True or a M2M intermediary.
            if formfield and db_field.name not in self.raw_id_fields:
                related_modeladmin = self.admin_site._registry.get(db_field.remote_field.model)
                wrapper_kwargs = {}
                if related_modeladmin:
                    wrapper_kwargs.update(
                        can_add_related=related_modeladmin.has_add_permission(request),
                        can_change_related=related_modeladmin.has_change_permission(request),
                        can_delete_related=related_modeladmin.has_delete_permission(request),
                    )
                widget_wrapper_class = self.related_field_widget_wrapper_class()
                formfield.widget = widget_wrapper_class(
                    formfield.widget, db_field.remote_field, self.admin_site, **wrapper_kwargs
                )

            return formfield

        # If we've got overrides for the formfield defined, use 'em. **kwargs
        # passed to formfield_for_dbfield override the defaults.
        for klass in db_field.__class__.mro():
            if klass in self.formfield_overrides:
                kwargs = dict(copy.deepcopy(self.formfield_overrides[klass]), **kwargs)
                return db_field.formfield(**kwargs)

        # For any other type of field, just call its formfield() method.
        return db_field.formfield(**kwargs)

    def has_add_permission(self, request):
        return (not self.readonly_model) \
            and super(SiteModel, self).has_add_permission(request)

    def has_delete_permission(self, request, obj=None):
        return self.delete_allowed \
            and (not self.readonly_model) \
            and super(SiteModel, self).has_delete_permission(request, obj)

    def get_readonly_fields(self, request, obj=None):
        """
        Hook for specifying custom readonly fields.
        """
        if self.readonly_model:
            return fields_for_model(model=self.model)
        if obj is None:
            return list(self.add_readonly_fields) + list(self.readonly_fields)
        else:
            return list(self.change_readonly_fields) + list(self.readonly_fields)

    @property
    def change_tools(self):
        """
        tools are iterable of dicts with name, label and view_def
        """
        return self.get_change_tools()

    def get_change_tools(self):
        """
        tools are dict with name, label and view_def
        """
        return []

    def has_permission(self, request, action, obj=None):
        """
        Returns True if the given request has permission to change the given
        Django model instance, the default implementation doesn't examine the
        `obj` parameter.

        Can be overridden by the user in subclasses. In such case it should
        return True if the given request has permission to change the `obj`
        model instance. If `obj` is None, this should return True if the given
        request has permission to change *any* object of the given type.
        """
        opts = self.opts
        codename = get_permission_codename(action, opts)
        return request.user.has_perm("%s.%s" % (opts.app_label, codename))

    def view_wrapper(self, view):
        def wrapper(*args, **kwargs):
            return self.admin_site.admin_view(view)(*args, **kwargs)
        wrapper.model_admin = self
        return update_wrapper(wrapper, view)

    def build_url(self, url_pattern, view_def, view_name=None):
        from django.conf.urls import url

        return url(url_pattern, self.view_wrapper(view_def), name=view_name)

    def get_urls(self):
        from django.conf.urls import url

        info = self.model._meta.app_label, self.model._meta.model_name

        urlpatterns = []
        if self.list_view is None or not issubclass(self.list_view, View):
            urlpatterns += [self.build_url(r'^$', self.changelist_view, '%s_%s_changelist' % info),]
        else:
            urlpatterns += [self.build_url(r'^$', self.list_view.as_view(), '%s_%s_changelist' % info),]

        urlpatterns += [
            self.build_url(r'^add/$', self.add_view, '%s_%s_add' % info),
            self.build_url(r'^(.+)/history/$', self.history_view, '%s_%s_history' % info),
            self.build_url(r'^(.+)/delete/$', self.delete_view, '%s_%s_delete' % info),
            self.build_url(r'^(.+)/change/$', self.change_view, '%s_%s_change' % info),
        ]
        if self.change_tools:
            for tool in self.change_tools:
                if tool:
                    urlpatterns += [
                        self.build_url(r'^(.+)/%s/$' % tool['name'], tool['view_def'], '%s_%s_%s' % (
                            self.model._meta.app_label,
                            self.model._meta.model_name,
                            tool['name'],
                        )),
                    ]
        urlpatterns += [
            # For backwards compatibility (was the change url before 1.9)
            self.build_url(r'^(.+)/$', RedirectView.as_view(
                pattern_name='%s:%s_%s_change' % ((self.admin_site.name,) + info))),
        ]
        
        return urlpatterns

    def index_url_format(self):
        return '%s:%%s_%%s' % self.admin_site.site_namespace

    def add_url_format(self):
        return '%s:%%s_%%s_add' % self.admin_site.site_namespace

    def change_url_format(self):
        return '%s:%%s_%%s_change' % self.admin_site.site_namespace

    def changelist_url_format(self):
        return '%s:%%s_%%s_changelist' % self.admin_site.site_namespace

    def get_model_actions(self, request):
        actions = []
        perms = self.get_model_perms(request)
        if perms.get('change'):
            actions.append(
                {
                    'name': 'change',
                    'label': 'List %s' % (self.model._meta.verbose_name_plural),
                    'url': self.changelist_url_format() % (
                        self.model._meta.app_label, self.model._meta.model_name),
                }
            )
        if perms.get('add'):
            actions.append(
                {
                    'name': 'add',
                    'label': 'Add %s' % (self.model._meta.verbose_name),
                    'url': self.add_url_format() % (
                        self.model._meta.app_label, self.model._meta.model_name),
                }
            )
        return actions

    def get_model_permissions(self, request):
        perms = self.get_model_perms(request)
        for action in self.model._meta.permissions:
            if self.has_permission(request, action[0]):
                perms.update({action[0]: True})
        return perms

    def get_model_extra_context(self, request, extra_context=None):
        context = dict(
            module_name=force_text(self.model._meta.verbose_name_plural),
            current_model_actions=self.get_model_actions(request),
        )
        context.update(self.admin_site.get_site_extra_context(request))
        return context

    def recent_link(self, request, model_object):
        """
        for adding recent link for user and url
        """
        try:
            if self.recent_allowed and model_object and model_object.pk:
                opts = model_object._meta
                url = reverse(
                    self.change_url_format() % (opts.app_label, opts.model_name),
                    args=(quote(model_object.pk),),
                    current_app=self.admin_site.name)
                label = model_object.__str__()
                icon = '%s%s' % (self.model._meta.app_label, self.model._meta.model_name)
                # TODO add url from request is useless
                #if self.is_add_url(url):
                #    url = reverse(self.change_url_format() % (
                #        self.model._meta.app_label, self.model._meta.model_name),
                #    kwargs={'object_id': model_object.pk})

                RecentLink.objects.update_or_create(
                    user_id=request.user.pk,
                    link_url=url,
                    defaults={
                        'user_id': request.user.pk,
                        'link_time': timezone.now,
                        'link_label': label,
                        'link_url': url,
                        'link_icon': icon,},)
        except Exception as ex:
            print(ex)

    def is_add_url(self, url):
        if url.find('/add') < 0:
            return False
        return True

    def delete_recent(self, request, object_id):
        """
        for removing registered recent links for user and url
        """
        qs = RecentLink.objects.filter(user=request.user)
        qs.filter(link_url__iendswith='/%s/%s/%s' % (
            self.model._meta.app_label,
            self.model._meta.model_name,
            object_id)).delete()
        qs.filter(link_url__icontains='/%s/%s/%s/' % (
            self.model._meta.app_label,
            self.model._meta.model_name,
            object_id)).delete()
        qs.filter(link_url__icontains='/%s/%s/%s?' % (
            self.model._meta.app_label,
            self.model._meta.model_name,
            object_id)).delete()

    def changeform_context(
            self, request, form, obj, formsets, inline_instances,
            add, opts, object_id, to_field, form_validated=None):

        adminForm = helpers.AdminForm(
            form,
            list(self.get_fieldsets(request, obj)),
            self.get_prepopulated_fields(request, obj),
            self.get_readonly_fields(request, obj),
            model_admin=self)
        media = self.media + adminForm.media

        inline_formsets = self.get_inline_formsets(request, formsets, inline_instances, obj)
        for inline_formset in inline_formsets:
            media = media + inline_formset.media

        context = dict(
            self.admin_site.each_context(request),
            title=(_('Add %s') if add else _('Change %s')) % force_text(opts.verbose_name),
            adminform=adminForm,
            object_id=object_id,
            original=obj,
            is_popup=(IS_POPUP_VAR in request.POST or IS_POPUP_VAR in request.GET),
            to_field=to_field,
            media=media,
            inline_admin_formsets=inline_formsets,
            errors=helpers.AdminErrorList(form, formsets),
            preserved_filters=self.get_preserved_filters(request),
            change_actions=self.change_actions,
            change_tools=self.change_tools,
        )
        context.update(self.get_model_extra_context(request))

        # Hide the "Save" and "Save and continue" buttons if "Save as New" was
        # previously chosen to prevent the interface from getting confusing.
        if (self.readonly_model or (
                request.method == 'POST' and not form_validated and "_saveasnew" in request.POST)):
            context['show_save'] = False
            context['show_save_and_continue'] = False
            # Use the change template instead of the add template.
            add = False

        return context

    def get_obj_does_not_exist_redirect(self, request, opts, object_id):
        """
        Create a message informing the user that the object doesn't exist
        and return a redirect to the admin index page.
        """
        msg = _("""%(name)s with ID "%(key)s" doesn't exist. Perhaps it was deleted?""") % {
            'name': force_text(opts.verbose_name),
            'key': unquote(object_id),
        }
        self.message_user(request, msg, messages.WARNING)
        url = reverse(self.changelist_url_format() % (opts.app_label, opts.model_name), current_app=self.admin_site.name)
        self.delete_recent(request, object_id)
        return HttpResponseRedirect(url)

    def get_preserved_filters(self, request):
        """
        Returns the preserved filters querystring.
        """
        match = request.resolver_match
        if self.preserve_filters and match:
            opts = self.model._meta
            current_url = '%s:%s' % (match.app_name, match.url_name)
            changelist_url = self.changelist_url_format() % (opts.app_label, opts.model_name)
            if current_url == changelist_url:
                preserved_filters = request.GET.urlencode()
            else:
                preserved_filters = request.GET.get('_changelist_filters')

            if preserved_filters:
                return urlencode({'_changelist_filters': preserved_filters})
        return ''

    def response_add(self, request, obj, post_url_continue=None):
        """
        Determines the HttpResponse for the add_view stage.
        """
        opts = obj._meta
        pk_value = obj._get_pk_val()
        preserved_filters = self.get_preserved_filters(request)
        obj_url = reverse(
            self.change_url_format() % (opts.app_label, opts.model_name),
            args=(quote(pk_value),),
            current_app=self.admin_site.name,
        )
        # Add a link to the object's change form if the user can edit the obj.
        if self.has_change_permission(request, obj):
            obj_repr = format_html('<a href="{}">{}</a>', urlquote(obj_url), obj)
        else:
            obj_repr = force_text(obj)
        msg_dict = {
            'name': force_text(opts.verbose_name),
            'obj': obj_repr,
        }
        # Here, we distinguish between different save types by checking for
        # the presence of keys in request.POST.

        if IS_POPUP_VAR in request.POST:
            to_field = request.POST.get(TO_FIELD_VAR)
            if to_field:
                attr = str(to_field)
            else:
                attr = obj._meta.pk.attname
            value = obj.serializable_value(attr)
            popup_response_data = json.dumps({
                'value': six.text_type(value),
                'obj': six.text_type(obj),
            })
            return TemplateResponse(request, self.popup_response_template or [
                'admin/%s/%s/popup_response.html' % (opts.app_label, opts.model_name),
                'admin/%s/popup_response.html' % opts.app_label,
                'admin/popup_response.html',
            ], {
                'popup_response_data': popup_response_data,
            })

        elif "_continue" in request.POST or (
                # Redirecting after "Save as new".
                "_saveasnew" in request.POST and self.save_as_continue and
                self.has_change_permission(request, obj)
        ):
            msg = format_html(
                _('The {name} "{obj}" was added successfully. You may edit it again below.'),
                **msg_dict
            )
            self.message_user(request, msg, messages.SUCCESS)
            if post_url_continue is None:
                post_url_continue = obj_url
            post_url_continue = common_add_preserved_filters(
                {'preserved_filters': preserved_filters, 'opts': opts},
                post_url_continue
            )
            return HttpResponseRedirect(post_url_continue)

        elif "_addanother" in request.POST:
            msg = format_html(
                _('The {name} "{obj}" was added successfully. You may add another {name} below.'),
                **msg_dict
            )
            self.message_user(request, msg, messages.SUCCESS)
            redirect_url = request.path
            redirect_url = common_add_preserved_filters({'preserved_filters': preserved_filters, 'opts': opts}, redirect_url)
            return HttpResponseRedirect(redirect_url)

        else:
            msg = format_html(
                _('The {name} "{obj}" was added successfully.'),
                **msg_dict
            )
            self.message_user(request, msg, messages.SUCCESS)
            return self.response_post_save_add(request, obj)

    def response_change(self, request, obj):
        """
        Determines the HttpResponse for the change_view stage.
        """

        if IS_POPUP_VAR in request.POST:
            opts = obj._meta
            to_field = request.POST.get(TO_FIELD_VAR)
            attr = str(to_field) if to_field else opts.pk.attname
            # Retrieve the `object_id` from the resolved pattern arguments.
            value = request.resolver_match.args[0]
            new_value = obj.serializable_value(attr)
            popup_response_data = json.dumps({
                'action': 'change',
                'value': six.text_type(value),
                'obj': six.text_type(obj),
                'new_value': six.text_type(new_value),
            })
            return TemplateResponse(request, self.popup_response_template or [
                'admin/%s/%s/popup_response.html' % (opts.app_label, opts.model_name),
                'admin/%s/popup_response.html' % opts.app_label,
                'admin/popup_response.html',
            ], {
                'popup_response_data': popup_response_data,
            })

        opts = self.model._meta
        pk_value = obj._get_pk_val()
        preserved_filters = self.get_preserved_filters(request)

        msg_dict = {
            'name': force_text(opts.verbose_name),
            'obj': format_html('<a href="{}">{}</a>', urlquote(request.path), obj),
        }
        if "_continue" in request.POST:
            msg = format_html(
                _('The {name} "{obj}" was changed successfully. You may edit it again below.'),
                **msg_dict
            )
            self.message_user(request, msg, messages.SUCCESS)
            redirect_url = request.path
            redirect_url = common_add_preserved_filters({'preserved_filters': preserved_filters, 'opts': opts}, redirect_url)
            return HttpResponseRedirect(redirect_url)

        elif "_saveasnew" in request.POST:
            msg = format_html(
                _('The {name} "{obj}" was added successfully. You may edit it again below.'),
                **msg_dict
            )
            self.message_user(request, msg, messages.SUCCESS)
            redirect_url = reverse(self.change_url_format() %
                                   (opts.app_label, opts.model_name),
                                   args=(pk_value,),
                                   current_app=self.admin_site.name)
            redirect_url = common_add_preserved_filters({'preserved_filters': preserved_filters, 'opts': opts}, redirect_url)
            return HttpResponseRedirect(redirect_url)

        elif "_addanother" in request.POST:
            msg = format_html(
                _('The {name} "{obj}" was changed successfully. You may add another {name} below.'),
                **msg_dict
            )
            self.message_user(request, msg, messages.SUCCESS)
            redirect_url = reverse(self.add_url_format() %
                                   (opts.app_label, opts.model_name),
                                   current_app=self.admin_site.name)
            redirect_url = common_add_preserved_filters({'preserved_filters': preserved_filters, 'opts': opts}, redirect_url)
            return HttpResponseRedirect(redirect_url)

        else:
            msg = format_html(
                _('The {name} "{obj}" was changed successfully.'),
                **msg_dict
            )
            self.message_user(request, msg, messages.SUCCESS)
            return self.response_post_save_change(request, obj)

    def response_cancel(self, request, obj, add):
        """
        Figure out where to redirect after the 'Cancel' button has been pressed.
        """
        if add:
            return self.response_post_save_add(request, obj)
        else:
            return self.response_post_save_change(request, obj)

    def response_post_delete(self, request, obj):
        """
        Figure out where to redirect after the 'Delete'.
        """
        opts = self.model._meta

        if self.has_change_permission(request, None):
            post_url = reverse(
                self.changelist_url_format() % (opts.app_label, opts.model_name),
                current_app=self.admin_site.name,
            )
            preserved_filters = self.get_preserved_filters(request)
            post_url = common_add_preserved_filters(
                {'preserved_filters': preserved_filters, 'opts': opts}, post_url
            )
        else:
            post_url = reverse(self.admin_site.index_url(), current_app=self.admin_site.name)
        return HttpResponseRedirect(post_url)

    def response_post_save_add(self, request, obj):
        """
        Figure out where to redirect after the 'Save' button has been pressed
        when adding a new object.
        """
        opts = self.model._meta
        if self.has_change_permission(request, None):
            post_url = reverse(self.changelist_url_format() %
                               (opts.app_label, opts.model_name),
                               current_app=self.admin_site.name)
            preserved_filters = self.get_preserved_filters(request)
            post_url = common_add_preserved_filters({'preserved_filters': preserved_filters, 'opts': opts}, post_url)
        else:
            post_url = reverse(self.admin_site.index_url(),
                               current_app=self.admin_site.name)
        return HttpResponseRedirect(post_url)

    def response_post_save_change(self, request, obj):
        """
        Figure out where to redirect after the 'Save' button has been pressed
        when editing an existing object.
        """
        opts = self.model._meta

        if self.has_change_permission(request, None):
            post_url = reverse(self.changelist_url_format() %
                               (opts.app_label, opts.model_name),
                               current_app=self.admin_site.name)
            preserved_filters = self.get_preserved_filters(request)
            post_url = common_add_preserved_filters({'preserved_filters': preserved_filters, 'opts': opts}, post_url)
        else:
            post_url = reverse(self.admin_site.index_url(),
                               current_app=self.admin_site.name)
        return HttpResponseRedirect(post_url)

    def response_delete(self, request, obj, obj_display, obj_id):
        """
        Determines the HttpResponse for the delete_view stage.
        """

        opts = self.model._meta

        if IS_POPUP_VAR in request.POST:
            popup_response_data = json.dumps({
                'action': 'delete',
                'value': str(obj_id),
            })
            return TemplateResponse(request, self.popup_response_template or [
                'admin/%s/%s/popup_response.html' % (opts.app_label, opts.model_name),
                'admin/%s/popup_response.html' % opts.app_label,
                'admin/popup_response.html',
            ], {
                'popup_response_data': popup_response_data,
            })

        self.message_user(
            request,
            _('The %(name)s "%(obj)s" was deleted successfully.') % {
                'name': force_text(opts.verbose_name),
                'obj': force_text(obj_display),
            },
            messages.SUCCESS,
        )

        return self.response_post_delete(request, obj)

    def changeform_do_saving(self, request, new_object, form, formsets, add, inlines):
        """
        Hook for custom saving actions.
        """
        try:
            with transaction.atomic(savepoint=False):
                self.save_model(request, new_object, form, not add)
                self.save_related(request, form, formsets, not add)
                self.recent_link(request, model_object=new_object)
                change_message = self.construct_change_message(request, form, formsets, add)
                if add:
                    self.log_addition(request, new_object, change_message)
                    return self.response_add(request, new_object)
                else:
                    self.log_change(request, new_object, change_message)
                    return self.response_change(request, new_object)
        except ValidationError as ex:
            for message in ex.messages:
                self.message_user(request, message, messages.ERROR)
            return False
        except IntegrityError as ex:
            self.message_user(request, ex, messages.ERROR)
            return False

    @csrf_protect_m
    def changeform_view(self, request, object_id=None, form_url='', extra_context=None):
        """
        Recoding for allowing custom saving.
        """
        with transaction.atomic(using=router.db_for_write(self.model)):
            to_field = request.POST.get(TO_FIELD_VAR, request.GET.get(TO_FIELD_VAR))
            if to_field and not self.to_field_allowed(request, to_field):
                raise DisallowedModelAdminToField("The field %s cannot be referenced." % to_field)

            model = self.model
            opts = model._meta
            opts.details_template = self.details_template

            if request.method == 'POST' and '_saveasnew' in request.POST:
                object_id = None

            add = object_id is None

            if add:
                if not self.has_add_permission(request):
                    raise PermissionDenied
                obj = None

            else:
                obj = self.get_object(request, unquote(object_id), to_field)

                if (
                        (not self.has_module_permission(request))
                        and (not self.has_change_permission(request, obj))):
                    raise PermissionDenied

                if obj is None:
                    return self.get_obj_does_not_exist_redirect(request, opts, object_id)

            if obj:
                self.recent_link(request, model_object=obj)
            ModelForm = self.get_form(request, obj)
            if request.method == 'POST':
                form = ModelForm(request.POST, request.FILES, instance=obj)
                if '_cancel' in request.POST:
                    form_validated = False
                    new_object = form.instance
                    formsets, inline_instances = self._create_formsets(
                        request, new_object, change=not add)
                    return self.response_cancel(request, new_object, add)
                else:
                    if form.is_valid():
                        form_validated = True
                        new_object = self.save_form(request, form, change=not add)
                    else:
                        form_validated = False
                        new_object = form.instance
                    formsets, inline_instances = self._create_formsets(
                        request, new_object, change=not add)
                    if all_valid(formsets) and form_validated:
                        response = self.changeform_do_saving(
                            request=request, new_object=new_object, form=form, formsets=formsets,
                            add=add, inlines=inline_instances)
                        if response:
                            return response
                        else:
                            form_validated = False
                    else:
                        form_validated = False
            else:
                if add:
                    initial = self.get_changeform_initial_data(request)
                    form = ModelForm(initial=initial)
                    formsets, inline_instances = self._create_formsets(
                        request, form.instance, change=False)
                    #self_formsets, self_inline_instances = self._create_self_formsets(
                    #    request, form.instance, change=False)
                else:
                    form = ModelForm(instance=obj)
                    formsets, inline_instances = self._create_formsets(request, obj, change=True)
                    #self_formsets, self_inline_instances = self._create_self_formsets(
                    #    request, obj, change=True)

            if request.method == 'POST':
                context = self.changeform_context(
                    request, form, obj, formsets, inline_instances, add, opts, object_id, to_field,
                    form_validated)
            else:
                context = self.changeform_context(
                    request, form, obj, formsets, inline_instances, add, opts, object_id, to_field)
            context.update(extra_context or {})

            return self.render_change_form(
                request, context, add=add, change=not add, obj=obj, form_url=form_url)

    def do_deleting(self, request, obj, obj_display, obj_id):
        """
        Hook for custom deleting actions.
        """
        try:
            with transaction.atomic(savepoint=False):
                self.log_deletion(request, obj, obj_display)
                self.delete_model(request, obj)
                self.delete_recent(request, obj_id)

                return self.response_delete(request, obj, obj_display, obj_id)
        except ValidationError as ex:
            for message in ex.messages:
                self.message_user(request, message, messages.ERROR)
            return False

    @csrf_protect_m
    def delete_view(self, request, object_id, extra_context=None):
        """
        Recoding for allowing custom deleting.
        """
        with transaction.atomic(using=router.db_for_write(self.model)):
            opts = self.model._meta
            app_label = opts.app_label

            to_field = request.POST.get(TO_FIELD_VAR, request.GET.get(TO_FIELD_VAR))
            if to_field and not self.to_field_allowed(request, to_field):
                raise DisallowedModelAdminToField("The field %s cannot be referenced." % to_field)

            obj = self.get_object(request, unquote(object_id), to_field)

            if not self.has_delete_permission(request, obj):
                raise PermissionDenied

            if obj is None:
                return self.get_obj_does_not_exist_redirect(request, opts, object_id)

            using = router.db_for_write(self.model)

            # Populate deleted_objects, a data structure of all related objects that
            # will also be deleted.
            (deleted_objects, model_count, perms_needed, protected) = get_deleted_objects(
                [obj], opts, request.user, self.admin_site, using)

            if request.POST and not protected:  # The user has confirmed the deletion.
                if perms_needed:
                    raise PermissionDenied
                obj_display = force_text(obj)
                attr = str(to_field) if to_field else opts.pk.attname
                obj_id = obj.serializable_value(attr)

                response = self.do_deleting(request, obj, obj_display, obj_id)
                if response:
                    return response

                model_form = self.get_form(request, obj)

                form = model_form(instance=obj)
                formsets, inline_instances = self._create_formsets(request, obj, change=True)

                admin_form = helpers.AdminForm(
                    form,
                    list(self.get_fieldsets(request, obj)),
                    self.get_prepopulated_fields(request, obj),
                    self.get_readonly_fields(request, obj),
                    model_admin=self)
                media = self.media + admin_form.media

                inline_formsets = self.get_inline_formsets(request, formsets, inline_instances, obj)
                for inline_formset in inline_formsets:
                    media = media + inline_formset.media

                context = dict(
                    self.admin_site.each_context(request),
                    title=(_('Change %s')) % force_text(opts.verbose_name),
                    adminform=admin_form,
                    object_id=object_id,
                    original=obj,
                    is_popup=(IS_POPUP_VAR in request.POST or IS_POPUP_VAR in request.GET),
                    to_field=to_field,
                    media=media,
                    inline_admin_formsets=inline_formsets,
                    errors=helpers.AdminErrorList(form, formsets),
                    preserved_filters=self.get_preserved_filters(request),
                )
                return self.render_change_form(
                    request, context, add=False, change=True, obj=obj, form_url='')

            object_name = force_text(opts.verbose_name)

            if perms_needed or protected:
                title = _("Cannot delete %(name)s") % {"name": object_name}
            else:
                title = _("Are you sure?")

            context = dict(
                self.admin_site.each_context(request),
                title=title,
                object_name=object_name,
                object=obj,
                deleted_objects=deleted_objects,
                model_count=dict(model_count).items(),
                perms_lacking=perms_needed,
                protected=protected,
                opts=opts,
                app_label=app_label,
                preserved_filters=self.get_preserved_filters(request),
                is_popup=(IS_POPUP_VAR in request.POST or IS_POPUP_VAR in request.GET),
                to_field=to_field,
            )
            context.update(extra_context or {})

            return self.render_delete_form(request, context)

    def get_changelist(self, request, **kwargs):
        """
        Returns the ChangeList class for use on the changelist page.
        """
        return CommonChangeList

    def details_button(self, obj):
        """
        A list_display column containing a button widget.
        """
        return mark_safe('<button type="button" class="btn btn-default btn-xs collapsed" data-toggle="collapse" data-target="#div_' + str(obj.pk) +  '" aria-expanded="false"><span class="glyphicon"></span></button>')

    def get_top_filters(self, request):
        return self.top_filters

    @csrf_protect_m
    def changelist_view(self, request, extra_context=None):
        """
        The 'change list' admin view for this model.
        """
        from django.contrib.admin.views.main import ERROR_FLAG
        opts = self.model._meta
        app_label = opts.app_label
        if not self.has_change_permission(request, None):
            raise PermissionDenied

        list_display = self.get_list_display(request)
        list_display_links = self.get_list_display_links(request, list_display)
        list_filter = self.get_list_filter(request)
        top_filters = self.get_top_filters(request)
        search_fields = self.get_search_fields(request)
        list_select_related = self.get_list_select_related(request)

        # Check details to see if any are available on this changelist
        if self.details_template:
            # Add the details expand/collapse button.
            list_display = ['details_button'] + list(list_display)

        # Check actions to see if any are available on this changelist
        actions = self.get_actions(request)
        if actions:
            # Add the action checkboxes if there are any actions available.
            list_display = ['action_checkbox'] + list(list_display)

        ChangeListClass = self.get_changelist(request)
        try:
            cl = ChangeListClass(
                request, self.model, list_display,
                list_display_links, list_filter, top_filters, self.date_hierarchy,
                search_fields, list_select_related, self.list_per_page,
                self.list_max_show_all, self.list_editable, self
            )
            cl.details_template = self.details_template

        except IncorrectLookupParameters:
            # Wacky lookup parameters were given, so redirect to the main
            # changelist page, without parameters, and pass an 'invalid=1'
            # parameter via the query string. If wacky parameters were given
            # and the 'invalid=1' parameter was already in the query string,
            # something is screwed up with the database, so display an error
            # page.
            if ERROR_FLAG in request.GET.keys():
                return SimpleTemplateResponse('admin/invalid_setup.html', {
                    'title': _('Database error'),
                })
            return HttpResponseRedirect(request.path + '?' + ERROR_FLAG + '=1')

        # If the request was POSTed, this might be a bulk action or a bulk
        # edit. Try to look up an action or confirmation first, but if this
        # isn't an action the POST will fall through to the bulk edit check,
        # below.
        action_failed = False
        selected = request.POST.getlist(helpers.ACTION_CHECKBOX_NAME)

        # Actions with no confirmation
        if (actions and request.method == 'POST' and
                'index' in request.POST and '_save' not in request.POST):
            if selected:
                response = self.response_action(request, queryset=cl.get_queryset(request))
                if response:
                    return response
                else:
                    action_failed = True
            else:
                msg = _("Items must be selected in order to perform "
                        "actions on them. No items have been changed.")
                self.message_user(request, msg, messages.WARNING)
                action_failed = True

        # Actions with confirmation
        if (actions and request.method == 'POST' and
                helpers.ACTION_CHECKBOX_NAME in request.POST and
                'index' not in request.POST and '_save' not in request.POST):
            if selected:
                response = self.response_action(request, queryset=cl.get_queryset(request))
                if response:
                    return response
                else:
                    action_failed = True

        if action_failed:
            # Redirect back to the changelist page to avoid resubmitting the
            # form if the user refreshes the browser or uses the "No, take
            # me back" button on the action confirmation page.
            return HttpResponseRedirect(request.get_full_path())

        # If we're allowing changelist editing, we need to construct a formset
        # for the changelist given all the fields to be edited. Then we'll
        # use the formset to validate/process POSTed data.
        formset = cl.formset = None

        # Handle POSTed bulk-edit data.
        if request.method == 'POST' and cl.list_editable and '_save' in request.POST:
            FormSet = self.get_changelist_formset(request)
            formset = cl.formset = FormSet(request.POST, request.FILES, queryset=self.get_queryset(request))
            if formset.is_valid():
                changecount = 0
                for form in formset.forms:
                    if form.has_changed():
                        obj = self.save_form(request, form, change=True)
                        self.save_model(request, obj, form, change=True)
                        self.save_related(request, form, formsets=[], change=True)
                        change_msg = self.construct_change_message(request, form, None)
                        self.log_change(request, obj, change_msg)
                        changecount += 1

                if changecount:
                    if changecount == 1:
                        name = force_text(opts.verbose_name)
                    else:
                        name = force_text(opts.verbose_name_plural)
                    msg = ungettext(
                        "%(count)s %(name)s was changed successfully.",
                        "%(count)s %(name)s were changed successfully.",
                        changecount
                    ) % {
                        'count': changecount,
                        'name': name,
                        'obj': force_text(obj),
                    }
                    self.message_user(request, msg, messages.SUCCESS)

                return HttpResponseRedirect(request.get_full_path())

        # Handle GET -- construct a formset for display.
        elif cl.list_editable:
            FormSet = self.get_changelist_formset(request)
            formset = cl.formset = FormSet(queryset=cl.result_list)

        # Build the list of media to be used by the formset.
        if formset:
            media = self.media + formset.media
        else:
            media = self.media

        # Build the action form and populate it with available actions.
        if actions:
            action_form = self.action_form(auto_id=None)
            action_form.fields['action'].choices = self.get_action_choices(request)
            media += action_form.media
        else:
            action_form = None

        selection_note_all = ungettext(
            '%(total_count)s selected',
            'All %(total_count)s selected',
            cl.result_count
        )

        context = dict(
            self.admin_site.each_context(request),
            module_name=force_text(opts.verbose_name_plural),
            selection_note=_('0 of %(cnt)s selected') % {'cnt': len(cl.result_list)},
            selection_note_all=selection_note_all % {'total_count': cl.result_count},
            title=cl.title,
            is_popup=cl.is_popup,
            to_field=cl.to_field,
            cl=cl,
            media=media,
            has_add_permission=self.has_add_permission(request),
            opts=cl.opts,
            action_form=action_form,
            actions_on_top=self.actions_on_top,
            actions_on_bottom=self.actions_on_bottom,
            actions_selection_counter=self.actions_selection_counter,
            preserved_filters=self.get_preserved_filters(request),
        )

        site_context = self.get_model_extra_context(request, extra_context)
        context.update(site_context)

        context.update(extra_context or {})

        request.current_app = self.admin_site.name

        # taken from totalsum package to add totals...
        filtered_query_set = cl.queryset
        extra_context = extra_context or {}
        extra_context['totals'] = {}
        extra_context['unit_of_measure'] = self.unit_of_measure

        for elem in self.totalsum_list:
            try:
                self.model._meta.get_field(elem)  # Checking if elem is a field
                total = filtered_query_set.aggregate(totalsum_field=models.Sum(elem))['totalsum_field']
                if total is not None:
                    extra_context['totals'][label_for_field(elem, self.model, self)] = round(
                        total, self.totalsum_decimal_places)
            except FieldDoesNotExist:  # maybe it's a property
                if hasattr(self.model, elem):
                    total = 0
                    for f in filtered_query_set:
                        total += getattr(f, elem, 0)
                    extra_context['totals'][label_for_field(elem, self.model, self)] = round(
                        total, self.totalsum_decimal_places)
        context.update(extra_context)

        return TemplateResponse(request, self.change_list_template or [
            'common/%s/%s/change_list.html' % (app_label, opts.model_name),
            'common/%s/change_list.html' % app_label,
            'common/change_list.html'
        ], context)

    def build_inlines(self, request, obj):
        formsets = self._build_formsets(request, obj)
        inlines = []
        for formset in formsets:
            items = []
            forms_to_delete = formset.deleted_forms
            for form in formset.initial_forms:
                if form in forms_to_delete:
                    continue
                if form.cleaned_data.get(DELETION_FIELD_NAME, False):
                    continue
                item = form.instance
                items.append(item)
            for form in formset.extra_forms:
                if form.cleaned_data.get(DELETION_FIELD_NAME, False):
                    continue
                item = form.instance
                items.append(item)
            inlines.append(items)
        return inlines

    def _build_formsets(self, request, obj):
        "Helper function to generate formsets for add/change_view."
        formsets = []
        prefixes = {}
        get_formsets_args = [request]
        for FormSet, inline in self.get_formsets_with_inlines(*get_formsets_args):
            prefix = FormSet.get_default_prefix()
            prefixes[prefix] = prefixes.get(prefix, 0) + 1
            if prefixes[prefix] != 1 or not prefix:
                prefix = "%s-%s" % (prefix, prefixes[prefix])
            formset_params = {
                'instance': obj,
                'prefix': prefix,
                'queryset': inline.get_queryset(request),
            }
            if request.method == 'POST':
                formset_params.update({
                    'data': request.POST.copy(),
                    'files': request.FILES,
                    'save_as_new': '_saveasnew' in request.POST
                })
            formsets.append(FormSet(**formset_params))
        return formsets


class CommonChangeList(ChangeList):
    details_template = None

    def __init__(self, request, model, list_display, list_display_links,
                 list_filter, top_filters, date_hierarchy, search_fields, list_select_related,
                 list_per_page, list_max_show_all, list_editable, model_admin):
        self.top_filters = top_filters
        self.hidden_params = dict(request.GET.items())
        if SEARCH_VAR in self.hidden_params:
            self.hidden_params.pop(SEARCH_VAR)

        super(CommonChangeList, self).__init__(
            request, model, list_display, list_display_links,
            list_filter, date_hierarchy, search_fields, list_select_related,
            list_per_page, list_max_show_all, list_editable, model_admin)


    def url_for_result(self, result):
        pk = getattr(result, self.pk_attname)
        return reverse(
            '%s:%s_%s_change' % (
                self.model_admin.admin_site.site_namespace,
                self.opts.app_label,
                self.opts.model_name),
            args=(quote(pk),),
            current_app=self.model_admin.admin_site.name)

    def get_filters_params(self, params=None):
        if not params:
            params = self.params
        lookup_params = params.copy()  # a dictionary of the query string
        # Remove all the parameters that are globally and systematically
        # ignored.
        for ignored in IGNORED_PARAMS:
            if ignored in lookup_params:
                del lookup_params[ignored]
        result = lookup_params.copy()
        for param in lookup_params:
            if param.startswith(PARAM_PREFIX):
                del result[param]
        return result

    def get_top_filters_params(self, request):
        result = {}
        params = request.GET.items()
        for param, value in params:
            if param.startswith(PARAM_PREFIX):
                result.update({param: request.GET.getlist(param)})
        return result

    def get_top_filters(self, request, params):
        lookup_params = self.get_top_filters_params(request)
        hidden_params = self.hidden_params
        use_distinct = False

        for key, value in lookup_params.items():
            if not self.model_admin.lookup_allowed(key, value):
                raise DisallowedModelAdminLookup("Filtering by %s not allowed" % key)

        filter_specs = []
        if self.top_filters:
            for top_filter in self.top_filters:
                if callable(top_filter):
                    # This is simply a custom top filter class.
                    spec = top_filter(
                        '', request, lookup_params, hidden_params, self.model, self.model_admin, '')
                else:
                    field_path = None
                    if isinstance(top_filter, (tuple, list)):
                        # This is a custom Filter class for a given field.
                        if isinstance(top_filter[1], six.text_type):
                            field, top_filter_class = top_filter, TopFilter.create
                        else:
                            field, top_filter_class = top_filter[0], top_filter[1]
                    else:
                        # This is simply a field name, so use the default
                        # TopFilter class that has been registered for
                        # the type of the given field.
                        field, top_filter_class = top_filter, TopFilter.create
                    if  isinstance(field, (list, tuple)):
                        if not isinstance(field[0], models.Field):
                            field_path = field[0]
                            field = list(
                                (get_fields_from_path(self.model, field_path)[-1], field[1]))
                    else:
                        if not isinstance(field, models.Field):
                            field_path = field
                            field = get_fields_from_path(self.model, field_path)[-1]

                    lookup_params_count = len(lookup_params)
                    spec = top_filter_class(
                        field, request, lookup_params, hidden_params,
                        self.model, self.model_admin, field_path=field_path
                    )
                    # field_list_filter_class removes any lookup_params it
                    # processes. If that happened, check if distinct() is
                    # needed to remove duplicate results.
                    if lookup_params_count > len(lookup_params):
                        use_distinct = use_distinct or lookup_needs_distinct(self.lookup_opts, field_path)
                if spec:
                    filter_specs.append(spec)

        # At this point, all the parameters used by the various ListFilters
        # have been removed from lookup_params, which now only contains other
        # parameters passed via the query string. We now loop through the
        # remaining parameters both to ensure that all the parameters are valid
        # fields and to determine if at least one of them needs distinct(). If
        # the lookup parameters aren't real fields, then bail out.
        try:
            for key, value in lookup_params.items():
                lookup_params[key] = prepare_lookup_value(key, value)
                use_distinct = use_distinct or lookup_needs_distinct(self.lookup_opts, key)
            return filter_specs, bool(filter_specs), lookup_params, use_distinct
        except FieldDoesNotExist as e:
            six.reraise(IncorrectLookupParameters, IncorrectLookupParameters(e), sys.exc_info()[2])

    def get_queryset(self, request):
        qs = self.model._default_manager.get_queryset()
        ordering = self.get_ordering(request, qs)
        if ordering:
            qs = qs.order_by(*ordering)

        # First, we collect all the declared list filters.
        (self.filter_specs, self.has_filters, remaining_lookup_params,
         filters_use_distinct) = self.get_filters(request)

        # Then, we let every list filter modify the queryset to its liking.
        for filter_spec in self.filter_specs:
            new_qs = filter_spec.queryset(request, qs)
            if new_qs is not None:
                qs = new_qs

        # Second, we collect all the declared top filters.
        (self.top_filter_specs, self.has_top_filters, remaining_lookup_params,
         filters_use_distinct) = self.get_top_filters(request, remaining_lookup_params)

        # Then, we let every top filter modify the queryset to its liking.
        for filter_spec in self.top_filter_specs:
            new_qs = filter_spec.queryset(request, qs)
            if new_qs is not None:
                qs = new_qs

        try:
            # Finally, we apply the remaining lookup parameters from the query
            # string (i.e. those that haven't already been processed by the
            # filters).
            qs = qs.filter(**remaining_lookup_params)
        except (SuspiciousOperation, ImproperlyConfigured):
            # Allow certain types of errors to be re-raised as-is so that the
            # caller can treat them in a special way.
            raise
        except Exception as e:
            # Every other error is caught with a naked except, because we don't
            # have any other way of validating lookup parameters. They might be
            # invalid if the keyword arguments are incorrect, or if the values
            # are not in the correct type, so we might get FieldError,
            # ValueError, ValidationError, or ?.
            raise IncorrectLookupParameters(e)

        if not qs.query.select_related:
            qs = self.apply_select_related(qs)

        # Remove duplicates from results, if necessary
        if filters_use_distinct:
            return qs.distinct()
        else:
            return qs


class ResultList(list):

    def __init__(self, form, result, *items):
        self.form = form
        self.result = result
        super(ResultList, self).__init__(*items)


class CommonModelSiteTemplateResponse(TemplateResponse):
    
    def __init__(self, request, site_model, template, context=None, content_type=None,
                 status=None, charset=None, using=None):
        new_context = {}
        new_context.update(site_model.get_model_extra_context(request))
        new_context.update(context or {})

        super(CommonModelSiteTemplateResponse, self).__init__(
            template, new_context, content_type, status, charset, using)


class CommonInlineModelAdmin(InlineModelAdmin):
    def related_field_widget_wrapper_class(self):
        return CommonRelatedFieldWidgetWrapper

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        """
        Hook for specifying the form Field instance for a given database Field
        instance.

        If kwargs are given, they're passed to the form Field's constructor.
        """
        # If the field specifies choices, we don't need to look for special
        # admin widgets - we just need to use a select widget of some kind.
        if db_field.choices:
            return self.formfield_for_choice_field(db_field, request, **kwargs)

        # ForeignKey or ManyToManyFields
        if isinstance(db_field, models.ManyToManyField) or isinstance(db_field, models.ForeignKey):
            # Combine the field kwargs with any options for formfield_overrides.
            # Make sure the passed in **kwargs override anything in
            # formfield_overrides because **kwargs is more specific, and should
            # always win.
            if db_field.__class__ in self.formfield_overrides:
                kwargs = dict(self.formfield_overrides[db_field.__class__], **kwargs)

            # Get the correct formfield.
            if isinstance(db_field, models.ForeignKey):
                formfield = self.formfield_for_foreignkey(db_field, request, **kwargs)
            elif isinstance(db_field, models.ManyToManyField):
                formfield = self.formfield_for_manytomany(db_field, request, **kwargs)

            # For non-raw_id fields, wrap the widget with a wrapper that adds
            # extra HTML -- the "add other" interface -- to the end of the
            # rendered output. formfield can be None if it came from a
            # OneToOneField with parent_link=True or a M2M intermediary.
            if formfield and db_field.name not in self.raw_id_fields:
                related_modeladmin = self.admin_site._registry.get(db_field.remote_field.model)
                wrapper_kwargs = {}
                if related_modeladmin:
                    wrapper_kwargs.update(
                        can_add_related=related_modeladmin.has_add_permission(request),
                        can_change_related=related_modeladmin.has_change_permission(request),
                        can_delete_related=related_modeladmin.has_delete_permission(request),
                    )
                widget_wrapper_class = self.related_field_widget_wrapper_class()
                formfield.widget = widget_wrapper_class(
                    formfield.widget, db_field.remote_field, self.admin_site, **wrapper_kwargs
                )

            return formfield

        # If we've got overrides for the formfield defined, use 'em. **kwargs
        # passed to formfield_for_dbfield override the defaults.
        for klass in db_field.__class__.mro():
            if klass in self.formfield_overrides:
                kwargs = dict(copy.deepcopy(self.formfield_overrides[klass]), **kwargs)
                return db_field.formfield(**kwargs)

        # For any other type of field, just call its formfield() method.
        return db_field.formfield(**kwargs)


class CommonStackedInline(CommonInlineModelAdmin):
    template = 'common/edit_inline/stacked.html'


class CommonTabularInline(CommonInlineModelAdmin):
    template = 'common/edit_inline/tabular.html'
