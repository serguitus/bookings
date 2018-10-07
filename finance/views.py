from dal import autocomplete

from common.sites import CommonChangeList
from django.db.models import Exists, OuterRef, Subquery, Q, F, Value, DecimalField
from django.utils.encoding import force_text
from django.utils.translation import ugettext

from finance.models import Account, LoanEntity, LoanAccount, Provider
from finance.constants import STATUS_READY


class AccountAutocompleteView(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        # Don't forget to filter out results depending on the visitor !
        if not self.request.user.is_authenticated():
            return Account.objects.none()
        qs = Account.objects.filter(enabled=True).all()
        if self.q:
            qs = qs.filter(name__icontains=self.q)
        return qs


class LoanEntityAutocompleteView(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        # Don't forget to filter out results depending on the visitor !
        if not self.request.user.is_authenticated():
            return LoanEntity.objects.none()
        qs = LoanEntity.objects.filter(enabled=True).all()
        if self.q:
            qs = qs.filter(name__istartswith=self.q)
        return qs


class LoanAccountAutocompleteView(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        # Don't forget to filter out results depending on the visitor !
        if not self.request.user.is_authenticated():
            return LoanAccount.objects.none()
        qs = LoanAccount.objects.filter(account__enabled=True).all()
        if self.q:
            qs = qs.filter(name__istartswith=self.q)
        return qs


class ProviderAutocompleteView(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        # Don't forget to filter out results depending on the visitor !
        if not self.request.user.is_authenticated():
            return Provider.objects.none()
        qs = Provider.objects.all()
        if self.q:
            qs = qs.filter(name__icontains=self.q)
        return qs


class IncorrectLookupParameters(Exception):
    pass


class MatchList(CommonChangeList):
    """
    A custom class to build
    Match lists
    It adds 3 new attributes to class:
    - match_fields: a list of fields to filter the queryset
    - base_class: the class name of the object invoking the match list
    - obj_id: the id of the object to get related match list
    """

    def __init__(self, request, list_display, list_display_links,
                 list_filter, date_hierarchy, search_fields,
                 list_select_related, list_per_page, list_max_show_all,
                 list_editable, match_sitemodel, object_id, match_child_sitemodel):
        self.obj_id = object_id
        self.match_sitemodel = match_sitemodel
        self.match_child_sitemodel = match_child_sitemodel
        super(MatchList, self).__init__(
            request, self.match_child_sitemodel.model, list_display, list_display_links,
            list_filter, date_hierarchy, search_fields, list_select_related,
            list_per_page, list_max_show_all, list_editable, self.match_child_sitemodel)
        self.title = ugettext(
            'Select %s to match') % force_text(self.opts.verbose_name)

    def get_queryset(self, request):
        """ customizing queryset for matched objects"""
        try:
            parent_model = self.match_sitemodel.model
            parent_obj = parent_model.objects.get(pk=self.obj_id)
        except parent_model.DoesNotExist:
            raise IncorrectLookupParameters("Base object does not exist")

        f_exp = "{0}__exact".format(self.match_sitemodel.match_model_parent_field)
        sq_filter = {f_exp: self.obj_id}
        matches = self.match_sitemodel.match_model.objects.filter(**sq_filter)

        f_exp = "{0}__exact".format(self.match_sitemodel.match_model_child_field)
        sq_filter = {f_exp: OuterRef('pk')}
        matches = matches.filter(**sq_filter)

        filters = {}
        filters.update({"status__exact": STATUS_READY})
        for field in self.match_sitemodel.match_related_fields:
            nk = "%s__exact" % field
            nv = getattr(parent_obj, field)
            filters.update({nk: nv})

        unmatched = parent_obj.amount - parent_obj.matched_amount
        qs = self.model.objects.filter(**filters)
        qs = qs.annotate(parent_unmatched=Value(unmatched, DecimalField(max_digits=10, decimal_places=2)))
        qs = qs.annotate(match_id=Subquery(matches.values('id')))
        qs = qs.annotate(match_matched_amount=Subquery(matches.values('matched_amount')))
        qs = qs.filter(
            Q(match_id__isnull=False) | Q(amount__gt=F('matched_amount'))
        )
        # Set ordering.
        return qs.order_by('date')
