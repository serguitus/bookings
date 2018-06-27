# from django.contrib import admin
from django.contrib import admin, messages
from django.contrib.admin import helpers
from django.contrib.admin.exceptions import DisallowedModelAdminToField
from django.contrib.admin.options import csrf_protect_m, TO_FIELD_VAR, IS_POPUP_VAR
from django.contrib.admin.utils import flatten_fieldsets, unquote, get_deleted_objects
from django.core.exceptions import ValidationError, PermissionDenied
from django.db import router, transaction
from django.forms.formsets import all_valid
from django.forms.models import fields_for_model
from django.utils.encoding import force_text
from django.utils.translation import ugettext as _


class ReservasAdmin(admin.sites.AdminSite):
    # Anything we wish to add or override
    site_title = 'Reservas'
    site_header = 'Reservas'
    index_title = 'Main Menu'
    index_template = 'index.html'

    def has_permission(self, request):
        """
        Removed check for is_staff.
        """
        return request.user.is_active


reservas_admin = ReservasAdmin(name='reservas')
# Run user_admin_site.register() for each model we wish to register
# for our admin interface for users

# Run admin.site.register() for each model we wish to register
# with the REAL django admin!


class ExtendedModelAdmin(admin.ModelAdmin):
    save_on_top = True
    site_actions = []
    add_readonly_fields = ()
    change_readonly_fields = ()
    readonly_model = False
    delete_allowed = True

    def has_add_permission(self, request):
        return (not self.readonly_model) \
            and super(ExtendedModelAdmin, self).has_add_permission(request)

    def has_delete_permission(self, request, obj=None):
        return self.delete_allowed \
            and (not self.readonly_model) \
            and super(ExtendedModelAdmin, self).has_delete_permission(request, obj)

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

    def do_saving(self, request, new_object, form, formsets, add):
        """
        Hook for custom saving actions.
        """
        try:
            with transaction.atomic(savepoint=False):
                self.save_model(request, new_object, form, not add)
                self.save_related(request, form, formsets, not add)
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

    def do_deleting(self, request, obj, obj_display, obj_id):
        """
        Hook for custom deleting actions.
        """
        try:
            with transaction.atomic(savepoint=False):
                self.log_deletion(request, obj, obj_display)
                self.delete_model(request, obj)

                return self.response_delete(request, obj_display, obj_id)
        except ValidationError as ex:
            for message in ex.messages:
                self.message_user(request, message, messages.ERROR)
            return False

    def _changeform_view(self, request, object_id, form_url, extra_context):
        """
        Recoding for allowing custom saving.
        """
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

        ModelForm = self.get_form(request, obj)
        if request.method == 'POST':
            form = ModelForm(request.POST, request.FILES, instance=obj)
            if form.is_valid():
                form_validated = True
                new_object = self.save_form(request, form, change=not add)
            else:
                form_validated = False
                new_object = form.instance
            formsets, inline_instances = self._create_formsets(request, new_object, change=not add)
            if all_valid(formsets) and form_validated:
                response = self.do_saving(
                    request=request, new_object=new_object, form=form, formsets=formsets, add=add)
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
                formsets, inline_instances = self._create_formsets(request, form.instance, change=False)
            else:
                form = ModelForm(instance=obj)
                formsets, inline_instances = self._create_formsets(request, obj, change=True)

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
            is_popup=(IS_POPUP_VAR in request.POST or
                      IS_POPUP_VAR in request.GET),
            to_field=to_field,
            media=media,
            inline_admin_formsets=inline_formsets,
            errors=helpers.AdminErrorList(form, formsets),
            preserved_filters=self.get_preserved_filters(request),
        )

        # Hide the "Save" and "Save and continue" buttons if "Save as New" was
        # previously chosen to prevent the interface from getting confusing.
        if (self.readonly_model or (
                request.method == 'POST' and not form_validated and "_saveasnew" in request.POST)):
            context['show_save'] = False
            context['show_save_and_continue'] = False
            # Use the change template instead of the add template.
            add = False

        context.update(extra_context or {})

        return self.render_change_form(
            request, context, add=add, change=not add, obj=obj, form_url=form_url)

    def _delete_view(self, request, object_id, extra_context):
        "The 'delete' admin view for this model."
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
            is_popup=(IS_POPUP_VAR in request.POST or
                      IS_POPUP_VAR in request.GET),
            to_field=to_field,
        )
        context.update(extra_context or {})

        return self.render_delete_form(request, context)
