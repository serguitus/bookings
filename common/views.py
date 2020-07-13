from django.forms.formsets import DELETION_FIELD_NAME
from django.views import View


class ModelChangeFormProcessorView(View):

    model = None
    common_sitemodel = None
    common_site = None

    def post(self, request, *args, **kwargs):
        ModelForm = self.common_sitemodel.form
        form = ModelForm(request.POST, request.FILES, instance=None)
        id = request.POST.get('id')
        if id:
            form.instance.id = id
        if form.is_valid():
            new_object = form.save(commit=False)
        else:
            new_object = form.instance
        inlines = self.build_inlines(request, new_object)
        return self.process_data(new_object, inlines)

    def build_inlines(self, request, obj):
        formsets = self._create_formsets(request, obj)
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

    def process_data(self, obj, inlines):
        pass

    def _create_formsets(self, request, obj):
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

    def get_formsets_with_inlines(self, request, obj=None):
        """
        Yields formsets and the corresponding inlines.
        """
        for inline in self.get_inline_instances(request, obj):
            yield inline.get_formset(request, obj), inline

    def get_inline_instances(self, request, obj=None):
        inline_instances = []
        for inline_class in self.common_sitemodel.inlines:
            inline = inline_class(self.model, self.common_site)
            if request:
                if not (inline.has_add_permission(request) or
                        inline.has_change_permission(request, obj) or
                        inline.has_delete_permission(request, obj)):
                    continue
                if not inline.has_add_permission(request):
                    inline.max_num = 0
            inline_instances.append(inline)

        return inline_instances
