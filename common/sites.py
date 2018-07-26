import json

from functools import update_wrapper

from django.contrib import messages
from django.contrib.admin import helpers
from django.contrib.admin.exceptions import DisallowedModelAdminToField
from django.contrib.admin.options import csrf_protect_m, TO_FIELD_VAR, IS_POPUP_VAR, ModelAdmin
from django.contrib.admin.sites import AdminSite
from django.contrib.admin.templatetags.admin_urls import add_preserved_filters
from django.contrib.admin.utils import quote, unquote, get_deleted_objects
from django.contrib.auth import logout as auth_logout
from django.core.exceptions import ValidationError, PermissionDenied
from django.db import router, transaction
from django.forms.formsets import all_valid
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.template.response import TemplateResponse
from django.utils.html import format_html
from django.utils.http import urlquote
from django.utils.encoding import force_text
from django.utils import six
from django.utils.translation import ugettext as _, ugettext_lazy
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect

from common.models import RecentLink


class CommonSite(AdminSite):

    index_template = 'common/index.html'
    password_change_template = 'common/password_change.html'
    logout_template = 'common/logout.html'
    title = ugettext_lazy('Common Site')
    site_title = ugettext_lazy('Common Site')
    current_model = None
    password_change_url = None
    logout_url = None


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
        return self.get_urls(), 'common', self.name

    def admin_view(self, view, cacheable=False):
        def inner(request, *args, **kwargs):
            if not self.has_permission(request):
                if request.path == reverse('common:logout', current_app=self.name):
                    index_path = reverse('common:index', current_app=self.name)
                    return HttpResponseRedirect(index_path)
                # Inner import to prevent django.contrib.admin (app) from
                # importing django.contrib.auth.models.User (unrelated model).
                from django.contrib.auth.views import redirect_to_login
                return redirect_to_login(
                    request.get_full_path(),
                    reverse('common:login', current_app=self.name)
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

            index_url = site_model.index_url

            if not index_url:
                index_url = reverse(
                    'common:%s_%s_changelist' % (model._meta.app_label, model._meta.model_name),
                    current_app=self.name)

            model_dict = {
                'order': site_model.model_order,
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
            title=self.index_title,
            app_list=app_list,
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
        site_context = self.get_site_extra_context(request)
        site_context.update(extra_context or {})
        return super(CommonSite, self).password_change(request, site_context)

    @never_cache
    def logout(self, request, extra_context=None):
        """
        Logs out the user for the given HttpRequest.

        This should *not* assume the user is already logged in.
        """
        auth_logout(request)
        index_path = reverse('common:index', current_app=self.name)

        from django.contrib.auth.views import redirect_to_login

        return redirect_to_login(
            index_path,
            reverse('common:login', current_app=self.name)
        )


class SiteModel(ModelAdmin):
    save_on_top = True
    site_actions = []
    add_readonly_fields = ()
    change_readonly_fields = ()
    readonly_model = False
    delete_allowed = True
    self_inlines = []

    model_actions = []
    model_order = -1
    menu_label = None
    menu_group = None
    menu_option = None
    index_url = None
    add_form_template = 'common/change_form.html'
    change_form_template = 'common/change_form.html'
    change_list_template = 'common/change_list.html'

    def add_url_format(self):
        return 'common:%s_%s_add'

    def change_url_format(self):
        return 'common:%s_%s_change'

    def changelist_url_format(self):
        return 'common:%s_%s_changelist'

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

    def get_model_extra_context(self, request, extra_context=None):
        context = dict(
            module_name=force_text(self.model._meta.verbose_name_plural),
            current_model_actions=self.get_model_actions(request)
        )
        context.update(self.admin_site.get_site_extra_context(request))
        return context

    def recent_link(self, request, model_object, url=None, label=None, icon=None):
        """
        for adding recent link for user and url
        """
        if not url:
            url = request.get_full_path()
        if not label:
            label = model_object.__str__()
        if not icon:
            icon = model_object._meta.model_name
        return RecentLink.register_link(
            user=request.user,
            url=url,
            label=label,
            icon=icon,
        )

    def delete_recent(self, request, model_object):
        """
        for removing registered recent links for user and url
        """
        qs = RecentLink.objects.filter(user=request.user)
        qs.filter(link_url__iendswith='/%s/%s/%s' % (
            model_object.meta.app_name,
            model_object.meta.model_name,
            model_object.pk)).delete()
        qs.filter(link_url__icontains='/%s/%s/%s/' % (
            model_object.meta.app_name,
            model_object.meta.model_name,
            model_object.pk)).delete()
        qs.filter(link_url__icontains='/%s/%s/%s?' % (
            model_object.meta.app_name,
            model_object.meta.model_name,
            model_object.pk)).delete()

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
            post_url_continue = add_preserved_filters(
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
            redirect_url = add_preserved_filters({'preserved_filters': preserved_filters, 'opts': opts}, redirect_url)
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
            redirect_url = add_preserved_filters({'preserved_filters': preserved_filters, 'opts': opts}, redirect_url)
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
            redirect_url = add_preserved_filters({'preserved_filters': preserved_filters, 'opts': opts}, redirect_url)
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
            redirect_url = add_preserved_filters({'preserved_filters': preserved_filters, 'opts': opts}, redirect_url)
            return HttpResponseRedirect(redirect_url)

        else:
            msg = format_html(
                _('The {name} "{obj}" was changed successfully.'),
                **msg_dict
            )
            self.message_user(request, msg, messages.SUCCESS)
            return self.response_post_save_change(request, obj)

    def changeform_do_saving(self, request, new_object, form, formsets, add):
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
                    return self._get_obj_does_not_exist_redirect(request, opts, object_id)

            if obj:
                self.recent_link(request, model_object=obj)
            ModelForm = self.get_form(request, obj)
            if request.method == 'POST':
                form = ModelForm(request.POST, request.FILES, instance=obj)
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
                        add=add)
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

            print('FORM URL : ')
            print(form_url)

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
                self.delete_recent(request, obj)

                return self.response_delete(request, obj_display, obj_id)
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
                return self._get_obj_does_not_exist_redirect(request, opts, object_id)

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

    @csrf_protect_m
    def changelist_view(self, request, extra_context=None):
        site_context = self.get_model_extra_context(request, extra_context)
        return super(SiteModel, self).changelist_view(request, site_context)
