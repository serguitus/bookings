from django.contrib.admin.views.main import ChangeList


class MatchList(ChangeList):
    """
    A custom admin.ChangeList class to build
    Match lists
    It adds 3 new attributes to class:
    - match_fields: a list of fields to filter the queryset
    - base_class: the class name of the object invoking the match list
    - obj_id: the id of the object to get related match list
    """

    def __init__(self, request, model, list_display, list_display_links,
                 list_filter, date_hierarchy, search_fields,
                 list_select_related, list_per_page,
                 list_max_show_all, list_editable, model_admin,
                 match_fields, base_class, obj_id):
        self.match_fields = match_fields
        self.base_class = base_class
        self.obj_id = obj_id
        super(MatchList, self).__init__(
            request, model, list_display, list_display_links,
            list_filter, date_hierarchy, search_fields, list_select_related,
            list_per_page, list_max_show_all, list_editable, model_admin)

    def get_queryset(self, request):
        """ customizing queryset to matched objects"""
        base_obj = self.base_class.objects.get(id=self.obj_id)
        if self.match_fields:
            filters = {}
            for field in self.match_fields:
                nk = "{0}__exact".format(field)
                nv = getattr(base_obj, field)
                filters.update({nk: nv})

        self.root_queryset = self.model.objects.filter(**filters)
        return super(MatchList, self).get_queryset(request)
