from __future__ import unicode_literals
"""
config services
"""
from datetime import date, timedelta, time, datetime
from dateutil.relativedelta import relativedelta
from django.db import IntegrityError, transaction
from django.db.models import Q, Count
import math

from config.constants import (
    SERVICE_CATEGORY_EXTRA, SERVICE_CATEGORY_ALLOTMENT, SERVICE_CATEGORY_TRANSFER,
    AMOUNTS_FIXED, AMOUNTS_BY_PAX,
    EXTRA_PARAMETER_TYPE_HOURS, EXTRA_PARAMETER_TYPE_DAYS,
    EXTRA_PARAMETER_TYPE_NIGHTS, EXTRA_PARAMETER_TYPE_STAY,
    ERROR_INVALID_SERVICE_CATEGORY, ERROR_NO_COST_FOUND)
from config.models import (
    Allotment,
    ProviderAllotmentService, ProviderAllotmentDetail,
    AgencyAllotmentService, AgencyAllotmentDetail,
    Transfer,
    ProviderTransferService, ProviderTransferDetail,
    AgencyTransferService, AgencyTransferDetail,
    Extra,
    ProviderExtraService, ProviderExtraDetail,
    AgencyExtraService, AgencyExtraDetail,
    Schedule, TransferInterval, TransferPickupTime,
)
from finance.models import Agency
from reservas.custom_settings import ADDON_FOR_NO_ADDON


# helper function to compare Q objects until migration to Django2
# which actually implements __eq__ for Q objects
# once migrated, use normal comparison and remove this function
def compare_q(q1 , q2):
        return (
            q1.__class__ == q2.__class__ and
            (q1.connector, q1.negated) == (q2.connector, q2.negated) and
            q1.children == q2.children
        )


class ConfigServices(object):
    """
    ConfigServices
    """

    @classmethod
    def _copy_agency_amounts(cls, src_agency, dst_agency, is_update):
        cls._copy_allotments(src_agency, dst_agency, is_update)
        cls._copy_transfers(src_agency, dst_agency, is_update)
        cls._copy_extras(src_agency, dst_agency, is_update)


    @classmethod
    def _generate_agencies_amounts(cls, agencies, is_update):
        # load source agency

        from reservas.custom_settings import AGENCY_FOR_AMOUNTS

        try:
            src_agency = Agency.objects.get(id=AGENCY_FOR_AMOUNTS)
        except Agency.DoesNotExist as ex:
            print('EXCEPTION booking services - generate_agencies_amounts : ' + ex.__str__())
            # 'Source Agency not Found'
            return
        for dst_agency in agencies:
            if dst_agency.enabled:
                cls._copy_agency_amounts(src_agency, dst_agency, is_update)


    @classmethod
    def process_agencies_amounts(cls, agencies, is_update):
        cls._generate_agencies_amounts(agencies, is_update)
        return

        # from multiprocessing import Process
        # if __name__ == 'config.services':
        #    p = Process(target=cls.generate_agencies_amounts, args=(agencies))
        #    p.start()
        #    p.join()

    @classmethod
    def _copy_catalogue_services(cls, src_agency, dst_agency, is_update,
                                 service_model, detail_set_name, detail_model):
        """
        [Param] src_agency: id of the source agency to take prices from
        [Param] dst_agency: id of the destination agency to add prices to
        [Param] is_update: boolean. True if existing prices remain untouched
        [Param] service_model: the child model to get services from (ex. AgencyExtraService)
        [Param] detail_set_name: the queryset of related details. (ex. AgencyExtraService.agencyextradetail_set)
        [Param] detail_model: the child model to get price details from (ex. AgencyExtraDetail)
        """
        # find agencyservice list
        if is_update:
            # first get unique field sets for all services of those agencies
            src_services = service_model.objects.filter(
                agency__in=[src_agency, dst_agency]).values(
                    'date_from',
                    'date_to',
                    'contract_code',
                    'service')
            # now find those that are not present for both agencies
            src_not_dup_services = src_services.annotate(
                count=Count('service')).filter(count__lt=2)
            if not src_not_dup_services.count():
                # no service to update here. inform and exit
                return
            src_services_unique_fields = src_not_dup_services.values(
                'service', 'date_from', 'date_to', 'contract_code')
            # build the list of items to filter by
            filter_list = None
            for s in src_services_unique_fields:
                if filter_list:
                    filter_list |= Q(**s)
                else:
                    filter_list = Q(**s)
            # finally get the list of src services to generate from
            src_agency_services = service_model.objects.filter(
                agency=src_agency).filter(filter_list)
            for src_service in src_agency_services:
                dst_service = service_model.objects.create(
                    agency_id=dst_agency.id,
                    date_from=src_service.date_from,
                    date_to=src_service.date_to,
                    contract_code=src_service.contract_code,
                    booked_from=src_service.booked_from,
                    booked_to=src_service.booked_to,
                    service_id=src_service.service_id
                )
                for detail in getattr(src_service, detail_set_name).all():
                    detail.pk = None
                    detail.id = None
                    detail.agency_service = dst_service
                    detail.__dict__.update(cls.calculate_default_amounts(
                        detail, src_agency.gain_percent, dst_agency.gain_percent))
                    detail.save()
        return

    @classmethod
    def _copy_allotments(cls, src_agency, dst_agency, is_update):
        # find agencyservice list
        cls._copy_catalogue_services(src_agency, dst_agency, is_update,
                                 AgencyAllotmentService,
                                 "agencyallotmentdetail_set",
                                 AgencyAllotmentDetail)
        # done with the new AgencyAllotmentServices
        # now check for other pending AgencyAllotmentDetails
        if is_update:
            src_details = AgencyAllotmentDetail.objects.filter(
                agency_service__agency__in=[src_agency, dst_agency]).values(
                    'agency_service__service',
                    'agency_service__date_from',
                    'agency_service__date_to',
                    'agency_service__contract_code',
                    'room_type',
                    'board_type',
                    'addon',
                    'pax_range_min',
                    'pax_range_max'
                )
            src_not_dup_details = src_details.annotate(count=Count(
                'agency_service__service')).filter(count__lt=2)
            if not src_not_dup_details.count():
                # no detail to update here. inform and exit
                return
            src_details_unique_fields = src_not_dup_details.values(
                'agency_service__service',
                'agency_service__date_from',
                'agency_service__date_to',
                'agency_service__contract_code',
                'addon',
                'room_type',
                'board_type',
                'pax_range_min',
                'pax_range_max'
            )
            # build the list of items to filter by
            # default to filter None
            detail_filter_list = Q(pk__in=[])
            for s in src_details_unique_fields:
                if compare_q(detail_filter_list, Q(pk__in=[])):
                    detail_filter_list = Q(**s)
                else:
                    detail_filter_list |= Q(**s)
            src_agency_details = AgencyAllotmentDetail.objects.filter(
                agency_service__agency=src_agency).filter(
                    detail_filter_list).select_related('agency_service')
            for src_detail in src_agency_details:
                dst_service = AgencyAllotmentService.objects.get(
                    agency=dst_agency,
                    service=src_detail.agency_service.service,
                    date_from=src_detail.agency_service.date_from,
                    date_to=src_detail.agency_service.date_to,
                    contract_code=src_detail.agency_service.contract_code)
                # now drop ids to create a new detail refering dst_service
                src_detail.pk = None
                src_detail.id = None
                src_detail.agency_service = dst_service
                src_detail.__dict__.update(cls.calculate_default_amounts(
                        src_detail, src_agency.gain_percent, dst_agency.gain_percent))
                src_detail.save()
            return
        # Done with updating prices. if recreating all, proceed below
        # TODO. move this to an async task. Django-Q or Celery
        # for each agencyservice create agencyservice
        src_agency_services = AgencyAllotmentService.objects.filter(agency=src_agency.id)
        for src_agency_service in src_agency_services:
            dst_agency_service, created = AgencyAllotmentService.objects.get_or_create(
                agency_id=dst_agency.id,
                date_from=src_agency_service.date_from,
                date_to=src_agency_service.date_to,
                contract_code=src_agency_service.contract_code,
                service_id=src_agency_service.service_id
            )
            if created:
                dst_agency_service.booked_from = src_agency_service.booked_from
                dst_agency_service.booked_to = src_agency_service.booked_to

            # find details
            details = list(
                AgencyAllotmentDetail.objects.filter(agency_service=src_agency_service))
            # for each src agency detail create dst agency detail
            for detail in details:
                # rewrite - modify if exists
                agency_detail, created = AgencyAllotmentDetail.objects.update_or_create(
                    agency_service_id=dst_agency_service.id,
                    room_type_id=detail.room_type_id,
                    board_type=detail.board_type,
                    addon_id=detail.addon_id,
                    pax_range_min=detail.pax_range_min,
                    pax_range_max=detail.pax_range_max,
                    defaults=cls.calculate_default_amounts(
                        detail, src_agency.gain_percent, dst_agency.gain_percent)
                )


    @classmethod
    def _copy_transfers(cls, src_agency, dst_agency, is_update):
        cls._copy_catalogue_services(src_agency, dst_agency, is_update,
                                 AgencyTransferService,
                                 "agencytransferdetail_set",
                                 AgencyTransferDetail)
        # done with the new AgencyAllotmentServices
        # now check for other pending AgencyAllotmentDetails
        # find agencyservice list
        if is_update:
            src_details = AgencyTransferDetail.objects.filter(
                agency_service__agency__in=[src_agency, dst_agency]).values(
                    'agency_service__service',
                    'agency_service__date_from',
                    'agency_service__date_to',
                    'agency_service__contract_code',
                    'location_from',
                    'location_to',
                    'addon',
                    'pax_range_min',
                    'pax_range_max'
                )
            src_not_dup_details = src_details.annotate(count=Count(
                'agency_service__service')).filter(count__lt=2)
            if not src_not_dup_details.count():
                # no detail to update here. (TODO: notify user) and exit
                return
            src_details_unique_fields = src_not_dup_details.values(
                'agency_service__service',
                'agency_service__date_from',
                'agency_service__date_to',
                'agency_service__contract_code',
                'addon',
                'location_from',
                'location_to',
                'pax_range_min',
                'pax_range_max'
            )
            # build the list of items to filter by
            # default to filter None
            detail_filter_list = Q(pk__in=[])
            for s in src_details_unique_fields:
                if compare_q(detail_filter_list, Q(pk__in=[])):
                    detail_filter_list = Q(**s)
                else:
                    detail_filter_list |= Q(**s)
            src_agency_details = AgencyTransferDetail.objects.filter(
                agency_service__agency=src_agency).filter(
                    detail_filter_list).select_related('agency_service')
            for src_detail in src_agency_details:
                dst_service = AgencyTransferService.objects.get(
                    agency=dst_agency,
                    service=src_detail.agency_service.service,
                    date_from=src_detail.agency_service.date_from,
                    date_to=src_detail.agency_service.date_to,
                    contract_code=src_detail.agency_service.contract_code)
                # now drop ids to create a new detail refering dst_service
                src_detail.pk = None
                src_detail.id = None
                src_detail.agency_service = dst_service
                src_detail.__dict__.update(cls.calculate_default_amounts(
                        src_detail, src_agency.gain_percent, dst_agency.gain_percent))
                src_detail.save()
            return
        # Done with updating prices. if recreating all, proceed below
        # TODO. move this to an async task. Django-Q or Celery
        # find agencyservice list
        src_agency_services = list(AgencyTransferService.objects.filter(agency=src_agency.id))
        # for each agencyservice create agencyservice
        for src_agency_service in src_agency_services:
            dst_agency_service, created = AgencyTransferService.objects.get_or_create(
                agency_id=dst_agency.id,
                date_from=src_agency_service.date_from,
                date_to=src_agency_service.date_to,
                contract_code=src_agency_service.contract_code,
                service_id=src_agency_service.service_id
            )
            if created:
                dst_agency_service.booked_from = src_agency_service.booked_from
                dst_agency_service.booked_to = src_agency_service.booked_to

            # find details
            details = list(
                AgencyTransferDetail.objects.filter(agency_service=src_agency_service))
            # for each src agency detail create dst agency detail
            for detail in details:
                # rewrite - modify if exists
                agency_detail, created = AgencyTransferDetail.objects.update_or_create(
                    agency_service_id=dst_agency_service.id,
                    location_from_id=detail.location_from_id,
                    location_to_id=detail.location_to_id,
                    addon_id=detail.addon_id,
                    pax_range_min=detail.pax_range_min,
                    pax_range_max=detail.pax_range_max,
                    not_reversible=detail.not_reversible,
                    defaults=cls.calculate_default_amounts(
                        detail, src_agency.gain_percent, dst_agency.gain_percent)
                )


    @classmethod
    def _copy_extras(cls, src_agency, dst_agency, is_update):
        cls._copy_catalogue_services(src_agency, dst_agency, is_update,
                                 AgencyExtraService,
                                 "agencyextradetail_set",
                                 AgencyExtraDetail)
        # done with the new AgencyExtraServices
        # now check for other pending AgencyExtraDetails
        # find agencyservice list
        if is_update:
            src_details = AgencyExtraDetail.objects.filter(
                agency_service__agency__in=[src_agency, dst_agency]).values(
                    'agency_service__service',
                    'agency_service__date_from',
                    'agency_service__date_to',
                    'agency_service__contract_code',
                    'addon',
                    'pax_range_min',
                    'pax_range_max'
                )
            src_not_dup_details = src_details.annotate(count=Count(
                'agency_service__service')).filter(count__lt=2)
            src_details_unique_fields = src_not_dup_details.values(
                'agency_service__service',
                'agency_service__date_from',
                'agency_service__date_to',
                'agency_service__contract_code',
                'addon',
                'pax_range_min',
                'pax_range_max'
            )
            # build the list of items to filter by
            # default to filter None
            detail_filter_list = Q(pk__in=[])
            for s in src_details_unique_fields:
                if compare_q(detail_filter_list, Q(pk__in=[])):
                    detail_filter_list = Q(**s)
                else:
                    detail_filter_list |= Q(**s)
            src_agency_details = AgencyExtraDetail.objects.filter(
                agency_service__agency=src_agency).filter(
                    detail_filter_list).select_related('agency_service')
            for src_detail in src_agency_details:
                dst_service = AgencyExtraService.objects.get(
                    agency=dst_agency,
                    service=src_detail.agency_service.service,
                    date_from=src_detail.agency_service.date_from,
                    date_to=src_detail.agency_service.date_to,
                    contract_code=src_detail.agency_service.contract_code)
                # now drop ids to create a new detail refering dst_service
                src_detail.pk = None
                src_detail.id = None
                src_detail.agency_service = dst_service
                src_detail.__dict__.update(cls.calculate_default_amounts(
                        src_detail, src_agency.gain_percent, dst_agency.gain_percent))
                src_detail.save()
            return
        # Done with updating prices. if recreating all, proceed below
        # TODO. move this to an async task. Django-Q or Celery
        # find agencyservice list
        src_agency_services = list(AgencyExtraService.objects.filter(agency=src_agency.id))
        # for each agencyservice create agencyservice
        for src_agency_service in src_agency_services:
            dst_agency_service, created = AgencyExtraService.objects.get_or_create(
                agency_id=dst_agency.id,
                date_from=src_agency_service.date_from,
                date_to=src_agency_service.date_to,
                contract_code=src_agency_service.contract_code,
                service_id=src_agency_service.service_id
            )
            if created:
                dst_agency_service.booked_from = src_agency_service.booked_from
                dst_agency_service.booked_to = src_agency_service.booked_to

            # find details
            details = list(
                AgencyExtraDetail.objects.filter(agency_service=src_agency_service))
            # for each src agency detail create dst agency detail
            for detail in details:
                # rewrite - modify if exists
                agency_detail, created = AgencyExtraDetail.objects.update_or_create(
                    agency_service_id=dst_agency_service.id,
                    addon_id=detail.addon_id,
                    pax_range_min=detail.pax_range_min,
                    pax_range_max=detail.pax_range_max,
                    defaults=cls.calculate_default_amounts(
                        detail, src_agency.gain_percent, dst_agency.gain_percent)
                )


    @classmethod
    def process_agency_allotments_amounts(
            cls, agency, allotments_ids, gain_percent):
        """
        process_agency_allotments_amounts
        """

        from multiprocessing import Process

        if __name__ == '__main__':
            p = Process(
                target=cls.generate_agency_allotments_amounts,
                args=(agency, allotments_ids, gain_percent,))
            p.start()
            p.join()


    @classmethod
    def generate_agency_allotments_amounts(
            cls, agency_id, allotments_ids, gain_percent):
        """
        generate_agency_amounts
        """
        # for each service
        for service_id in allotments_ids:
            # find providerservice list
            provider_services = list(ProviderAllotmentService.objects.filter(service=service_id))
            # for each providerservice create agencyservice
            for provider_service in provider_services:
                agency_service, created = AgencyAllotmentService.objects.get_or_create(
                    agency_id=agency_id,
                    date_from=provider_service.date_from,
                    date_to=provider_service.date_to,
                    service=provider_service.service
                )
                # find details
                details = list(
                    ProviderAllotmentDetail.objects.filter(provider_service=provider_service))
                # for each providerdetail create agencydetail
                for detail in details:
                    agency_detail, created = AgencyAllotmentDetail.objects.get_or_create(
                        agency_service=agency_service,
                        room_type=detail.room_type,
                        board_type=detail.board_type,
                        addon_id=detail.addon_id,
                        pax_range_min=detail.pax_range_min,
                        pax_range_max=detail.pax_range_max,
                        # from provider src gain is 0
                        defaults=cls.calculate_default_amounts(detail, 0, gain_percent)
                    )
                    # if already exists ensure higher amounts
                    if not created:
                        cls._ensure_higher_amounts(agency_detail, detail)


    @classmethod
    def calculate_default_amounts(cls, detail, src_gain_percent, dst_gain_percent):
        return {
            'ad_1_amount': cls._calculate_price(
                detail.ad_1_amount, src_gain_percent, dst_gain_percent),
            'ad_2_amount': cls._calculate_price(
                detail.ad_2_amount, src_gain_percent, dst_gain_percent),
            'ad_3_amount': cls._calculate_price(
                detail.ad_3_amount, src_gain_percent, dst_gain_percent),
            'ad_4_amount': cls._calculate_price(
                detail.ad_4_amount, src_gain_percent, dst_gain_percent),
            'ch_1_ad_0_amount': cls._calculate_price(
                detail.ch_1_ad_0_amount, src_gain_percent, dst_gain_percent),
            'ch_1_ad_1_amount': cls._calculate_price(
                detail.ch_1_ad_1_amount, src_gain_percent, dst_gain_percent),
            'ch_1_ad_2_amount': cls._calculate_price(
                detail.ch_1_ad_2_amount, src_gain_percent, dst_gain_percent),
            'ch_1_ad_3_amount': cls._calculate_price(
                detail.ch_1_ad_3_amount, src_gain_percent, dst_gain_percent),
            'ch_1_ad_4_amount': cls._calculate_price(
                detail.ch_1_ad_4_amount, src_gain_percent, dst_gain_percent),
            'ch_2_ad_0_amount': cls._calculate_price(
                detail.ch_2_ad_0_amount, src_gain_percent, dst_gain_percent),
            'ch_2_ad_1_amount': cls._calculate_price(
                detail.ch_2_ad_1_amount, src_gain_percent, dst_gain_percent),
            'ch_2_ad_2_amount': cls._calculate_price(
                detail.ch_2_ad_2_amount, src_gain_percent, dst_gain_percent),
            'ch_2_ad_3_amount': cls._calculate_price(
                detail.ch_2_ad_3_amount, src_gain_percent, dst_gain_percent),
            'ch_2_ad_4_amount': cls._calculate_price(
                detail.ch_2_ad_4_amount, src_gain_percent, dst_gain_percent),
            'ch_3_ad_0_amount': cls._calculate_price(
                detail.ch_3_ad_0_amount, src_gain_percent, dst_gain_percent),
            'ch_3_ad_1_amount': cls._calculate_price(
                detail.ch_3_ad_1_amount, src_gain_percent, dst_gain_percent),
            'ch_3_ad_2_amount': cls._calculate_price(
                detail.ch_3_ad_2_amount, src_gain_percent, dst_gain_percent),
            'ch_3_ad_3_amount': cls._calculate_price(
                detail.ch_3_ad_3_amount, src_gain_percent, dst_gain_percent),
            'ch_3_ad_4_amount': cls._calculate_price(
                detail.ch_3_ad_4_amount, src_gain_percent, dst_gain_percent)
        }

    @classmethod
    def _ensure_higher_amounts(cls, agency_detail, detail):
        modified = False
        if cls._need_update(agency_detail.ad_1_amount, detail.ad_1_amount):
            agency_detail.ad_1_amount = detail.ad_1_amount
            modified = True
        if cls._need_update(agency_detail.ad_2_amount, detail.ad_2_amount):
            agency_detail.ad_2_amount = detail.ad_2_amount
            modified = True
        if cls._need_update(agency_detail.ad_3_amount, detail.ad_3_amount):
            agency_detail.ad_3_amount = detail.ad_3_amount
            modified = True
        if cls._need_update(agency_detail.ad_4_amount, detail.ad_4_amount):
            agency_detail.ad_4_amount = detail.ad_4_amount
            modified = True
        if cls._need_update(
                agency_detail.ch_1_ad_0_amount, detail.ch_1_ad_0_amount):
            agency_detail.ch_1_ad_0_amount = detail.ch_1_ad_0_amount
            modified = True
        if cls._need_update(
                agency_detail.ch_1_ad_1_amount, detail.ch_1_ad_1_amount):
            agency_detail.ch_1_ad_1_amount = detail.ch_1_ad_1_amount
            modified = True
        if cls._need_update(
                agency_detail.ch_1_ad_2_amount, detail.ch_1_ad_2_amount):
            agency_detail.ch_1_ad_2_amount = detail.ch_1_ad_2_amount
            modified = True
        if cls._need_update(
                agency_detail.ch_1_ad_3_amount, detail.ch_1_ad_3_amount):
            agency_detail.ch_1_ad_3_amount = detail.ch_1_ad_3_amount
            modified = True
        if cls._need_update(
                agency_detail.ch_1_ad_4_amount, detail.ch_1_ad_4_amount):
            agency_detail.ch_1_ad_4_amount = detail.ch_1_ad_4_amount
            modified = True
        if cls._need_update(
                agency_detail.ch_2_ad_0_amount, detail.ch_2_ad_0_amount):
            agency_detail.ch_2_ad_0_amount = detail.ch_2_ad_0_amount
            modified = True
        if cls._need_update(
                agency_detail.ch_2_ad_1_amount, detail.ch_2_ad_1_amount):
            agency_detail.ch_2_ad_1_amount = detail.ch_2_ad_1_amount
            modified = True
        if cls._need_update(
                agency_detail.ch_2_ad_2_amount, detail.ch_2_ad_2_amount):
            agency_detail.ch_2_ad_2_amount = detail.ch_2_ad_2_amount
            modified = True
        if cls._need_update(
                agency_detail.ch_2_ad_3_amount, detail.ch_2_ad_3_amount):
            agency_detail.ch_2_ad_3_amount = detail.ch_2_ad_3_amount
            modified = True
        if cls._need_update(
                agency_detail.ch_2_ad_4_amount, detail.ch_2_ad_4_amount):
            agency_detail.ch_2_ad_4_amount = detail.ch_2_ad_4_amount
            modified = True
        if cls._need_update(
                agency_detail.ch_3_ad_0_amount, detail.ch_3_ad_0_amount):
            agency_detail.ch_3_ad_0_amount = detail.ch_3_ad_0_amount
            modified = True
        if cls._need_update(
                agency_detail.ch_3_ad_1_amount, detail.ch_3_ad_1_amount):
            agency_detail.ch_3_ad_1_amount = detail.ch_3_ad_1_amount
            modified = True
        if cls._need_update(
                agency_detail.ch_3_ad_2_amount, detail.ch_3_ad_2_amount):
            agency_detail.ch_3_ad_2_amount = detail.ch_3_ad_2_amount
            modified = True
        if cls._need_update(
                agency_detail.ch_3_ad_3_amount, detail.ch_3_ad_3_amount):
            agency_detail.ch_3_ad_3_amount = detail.ch_3_ad_3_amount
            modified = True
        if cls._need_update(
                agency_detail.ch_3_ad_4_amount, detail.ch_3_ad_4_amount):
            agency_detail.ch_3_ad_4_amount = detail.ch_3_ad_4_amount
            modified = True
        if modified:
            agency_detail.save()

    @classmethod
    def _calculate_price(cls, src_price, src_gain_percent, dst_gain_percent):
        if src_price is None:
            return None
        if src_gain_percent is None or dst_gain_percent is None:
            return src_price
        return round(
            0.499999 + float(src_price) * (100.0 + float(dst_gain_percent)) / (100.0 + float(src_gain_percent)))

    @classmethod
    def _need_update(cls, old_value, new_value):
        return new_value is not None and (old_value is None or old_value < new_value)

    @classmethod
    def allotment_amounts(
            cls, service_id, date_from, date_to, cost_groups, price_groups,
            provider, booked, contract_code, agency,
            board_type, room_type_id, addon_id=None, quantity=None):
        if room_type_id is None or room_type_id == '':
            return None, 'Room Missing', None, 'Room Missing'
        if board_type is None or board_type == '':
            return None, 'Board Missing', None, 'Board Missing'
        if date_from is None:
            return None, 'Date from Missing', None, 'Date from Missing'
        if date_to is None:
            return None, 'Date to Missing', None, 'Date to Missing'

        # provider cost
        cost, cost_message = cls.allotment_costs(
            service_id, date_from, date_to, cost_groups,
            provider, booked, contract_code, board_type, room_type_id, addon_id, quantity)

        # agency price
        price, price_message = cls.allotment_prices(
            service_id, date_from, date_to, price_groups,
            agency, booked, contract_code, board_type, room_type_id, addon_id, quantity)

        return cost, cost_message, price, price_message

    @classmethod
    def allotment_costs(
            cls, service_id, date_from, date_to, cost_groups, provider, booked, contract_code,
            board_type, room_type_id, addon_id=None, quantity=None):
        if room_type_id is None or room_type_id == '':
            return None, 'Room Type Missing'
        if board_type is None or board_type == '':
            return None, 'Board Missing'
        if date_from is None:
            return None, 'Date from Missing'
        if date_to is None:
            return None, 'Date to Missing'

        # provider cost
        # obtain details order by date_from asc, date_to desc
        service = Allotment.objects.get(pk=service_id)

        if (cost_groups is None or not cost_groups) and service.cost_type == AMOUNTS_BY_PAX:
            cost = None
            cost_message = 'Empty rooming'
        elif provider is None:
            cost = None
            cost_message = 'Provider Not Found'
        else:
            if service.pax_range:
                cost = 0
                cost_message = ''
                # each group can have different details
                for group in cost_groups:
                    paxes = group[0] + group[1]
                    if paxes == 0:
                        continue
                    queryset = cls._get_provider_queryset(
                        ProviderAllotmentDetail.objects,
                        provider.id, service_id, date_from, date_to, booked, contract_code)
                    # pax range filtering
                    queryset = queryset.filter(
                        (Q(pax_range_min=0) & Q(pax_range_max__gte=paxes)) |
                        (Q(pax_range_min__lte=paxes) & Q(pax_range_max__gte=paxes)) |
                        (Q(pax_range_min__lte=paxes) & Q(pax_range_max=0)) |
                        (Q(pax_range_min=0) & Q(pax_range_max=0))
                    )
                    # addon filtering
                    if addon_id:
                        queryset = queryset.filter(addon_id=addon_id)
                    else:
                        queryset = queryset.filter(addon_id=ADDON_FOR_NO_ADDON)

                    detail_list = list(
                        queryset.filter(
                            board_type=board_type
                        ).filter(
                            room_type_id=room_type_id
                        )
                    )
                    if not detail_list:
                        return None, ERROR_NO_COST_FOUND % (service, provider, date_from)
                    group_cost, group_cost_message = cls.find_group_amount(
                        True, service, date_from, date_to, group,
                        quantity, None, detail_list
                    )
                    if group_cost:
                        cost += group_cost
                        cost_message = group_cost_message
                    else:
                        cost = None
                        cost_message = group_cost_message
                        break
            else:
                queryset = cls._get_provider_queryset(
                    ProviderAllotmentDetail.objects,
                    provider.id, service_id, date_from, date_to, booked, contract_code)
                # addon filtering
                if addon_id:
                    queryset = queryset.filter(addon_id=addon_id)
                else:
                    queryset = queryset.filter(addon_id=ADDON_FOR_NO_ADDON)
                detail_list = list(
                    queryset.filter(
                        board_type=board_type
                    ).filter(
                        room_type_id=room_type_id
                    )
                )
                if not detail_list:
                    return None, ERROR_NO_COST_FOUND % (service, provider, date_from)
                cost, cost_message = cls.find_groups_amount(
                    True, service, date_from, date_to, cost_groups,
                    quantity, None, detail_list
                )
        return cost, cost_message


    @classmethod
    def allotment_prices(
            cls, service_id, date_from, date_to, price_groups, agency, booked, contract_code,
            board_type, room_type_id, addon_id=None, quantity=None):
        if room_type_id is None or room_type_id == '':
            return None, 'Room Missing'
        if board_type is None or board_type == '':
            return None, 'Board Missing'
        if date_from is None:
            return None, 'Date from Missing'
        if date_to is None:
            return None, 'Date to Missing'

        # agency price
        # obtain details order by date_from asc, date_to desc
        service = Allotment.objects.get(pk=service_id)

        if (price_groups is None or not price_groups) and service.cost_type == AMOUNTS_BY_PAX:
            price = None
            price_message = 'Rooming Missing'
        elif agency is None:
            price = None
            price_message = 'Agency Not Found'
        else:
            if service.pax_range:
                price = 0
                price_message = ''
                # each group can have different details
                for group in price_groups:
                    paxes = group[0] + group[1]
                    if paxes == 0:
                        continue
                    queryset = cls._get_agency_queryset(
                        AgencyAllotmentDetail.objects,
                        agency.id, service_id, date_from, date_to, booked, contract_code)
                    # pax range filtering
                    queryset = queryset.filter(
                        (Q(pax_range_min=0) & Q(pax_range_max__gte=paxes)) |
                        (Q(pax_range_min__lte=paxes) & Q(pax_range_max__gte=paxes)) |
                        (Q(pax_range_min__lte=paxes) & Q(pax_range_max=0)) |
                        (Q(pax_range_min=0) & Q(pax_range_max=0))
                    )
                    # addon filtering
                    if addon_id:
                        queryset = queryset.filter(addon_id=addon_id)
                    else:
                        queryset = queryset.filter(addon_id=ADDON_FOR_NO_ADDON)

                    detail_list = list(
                        queryset.filter(
                            board_type=board_type
                        ).filter(
                            room_type_id=room_type_id
                        )
                    )
                    if not detail_list:
                        return None, "Price Not Found"
                    group_price, group_price_message = cls.find_group_amount(
                        False, service, date_from, date_to, group,
                        quantity, None, detail_list
                    )
                    if group_price:
                        price += group_price
                        price_message = group_price_message
                    else:
                        price = None
                        price_message = group_price_message
                        break
            else:
                queryset = cls._get_agency_queryset(
                    AgencyAllotmentDetail.objects,
                    agency.id, service_id, date_from, date_to, booked, contract_code)
                # addon filtering
                if addon_id:
                    queryset = queryset.filter(addon_id=addon_id)
                else:
                    queryset = queryset.filter(addon_id=ADDON_FOR_NO_ADDON)
                detail_list = list(
                    queryset.filter(
                        board_type=board_type
                    ).filter(
                        room_type_id=room_type_id
                    )
                )
                if not detail_list:
                    return None, "Price Not Found"
                price, price_message = cls.find_groups_amount(
                    False, service, date_from, date_to, price_groups,
                    quantity, None, detail_list
                )
        return price, price_message


    @classmethod
    def transfer_amounts(
            cls, service_id, date_from, date_to, cost_groups, price_groups,
            provider, booked, contract_code, agency,
            location_from_id, location_to_id, addon_id=None, quantity=None):
        if location_from_id is None or location_from_id == '':
            return None, 'Origin Location Missing', None, 'Origin Location Missing'
        if location_to_id is None or location_to_id == '':
            return None, 'Destination Location Missing', None, 'Destination Location Missing'
        if date_from is None and date_to is None:
            return None, 'Both Dates are Missing', None, 'Both Dates are Missing'
        if date_from is None:
            date_from = date_to
        if date_to is None:
            date_to = date_from

        # provider cost
        cost, cost_message = cls.transfer_costs(
            service_id, date_from, date_to, cost_groups,
            provider, booked, contract_code, location_from_id, location_to_id, addon_id, quantity)

        # agency price
        price, price_message = cls.transfer_prices(
            service_id, date_from, date_to, price_groups,
            agency, booked, contract_code, location_from_id, location_to_id, addon_id, quantity)

        return cost, cost_message, price, price_message


    @classmethod
    def transfer_costs(
            cls, service_id, date_from, date_to, cost_groups, provider, booked, contract_code,
            location_from_id, location_to_id, addon_id=None, quantity=None):
        if location_from_id is None or location_from_id == '':
            return None, 'Origin Location Missing'
        if location_to_id is None or location_to_id == '':
            return None, 'Destination Location Missing'
        if date_from is None and date_to is None:
            return None, 'Both Dates are Missing'
        if date_from is None:
            date_from = date_to
        if date_to is None:
            date_to = date_from

        # provider cost
        # obtain details order by date_from asc, date_to desc
        service = Transfer.objects.get(pk=service_id)

        if (cost_groups is None or not cost_groups) and service.cost_type == AMOUNTS_BY_PAX:
            cost = None
            cost_message = 'Rooming Missing'
        elif provider is None:
            cost = None
            cost_message = 'Provider Not Found'
        else:
            if service.pax_range:
                cost = 0
                cost_message = ''
                # each group can have different details
                for group in cost_groups:
                    paxes = group[0] + group[1]
                    if paxes == 0:
                        continue
                    queryset = cls._get_provider_queryset(
                        ProviderTransferDetail.objects,
                        provider.id, service_id, date_from, date_to, booked, contract_code)
                    # pax range filtering
                    queryset = queryset.filter(
                        (Q(pax_range_min=0) & Q(pax_range_max__gte=paxes)) |
                        (Q(pax_range_min__lte=paxes) & Q(pax_range_max__gte=paxes)) |
                        (Q(pax_range_min__lte=paxes) & Q(pax_range_max=0)) |
                        (Q(pax_range_min=0) & Q(pax_range_max=0))
                    )
                    # addon filtering
                    if addon_id:
                        queryset = queryset.filter(addon_id=addon_id)
                    else:
                        queryset = queryset.filter(addon_id=ADDON_FOR_NO_ADDON)

                    detail_list = list(
                        queryset.filter(
                            location_from_id=location_from_id,
                            location_to_id=location_to_id))
                    group_cost = None
                    if detail_list:
                        group_cost, group_cost_message = cls.find_groups_amount(
                            True, service, date_from, date_to, cost_groups,
                            quantity, None, detail_list
                        )
                    if group_cost is None:
                        detail_list = list(
                            queryset.filter(
                                location_to_id=location_from_id,
                                location_from_id=location_to_id))
                        if not detail_list:
                            return None, ERROR_NO_COST_FOUND % (service, provider, date_from)
                        group_cost, group_cost_message = cls.find_groups_amount(
                            True, service, date_from, date_to, cost_groups,
                            quantity, None, detail_list
                        )

                    if group_cost:
                        cost += group_cost
                        cost_message = group_cost_message
                    else:
                        cost = None
                        cost_message = group_cost_message
                        break
            else:
                queryset = cls._get_provider_queryset(
                    ProviderTransferDetail.objects,
                    provider.id, service_id, date_from, date_to, booked, contract_code)
                # addon filtering
                if addon_id:
                    queryset = queryset.filter(addon_id=addon_id)
                else:
                    queryset = queryset.filter(addon_id=ADDON_FOR_NO_ADDON)
                detail_list = list(
                    queryset.filter(
                        location_from_id=location_from_id,
                        location_to_id=location_to_id))
                cost = None
                if detail_list:
                    cost, cost_message = cls.find_groups_amount(
                        True, service, date_from, date_to, cost_groups,
                        quantity, None, detail_list
                    )
                if cost is None:
                    detail_list = list(
                        queryset.filter(
                            location_to_id=location_from_id,
                            location_from_id=location_to_id))
                    if not detail_list:
                        return None, ERROR_NO_COST_FOUND % (service, provider, date_from)
                    cost, cost_message = cls.find_groups_amount(
                        True, service, date_from, date_to, cost_groups,
                        quantity, None, detail_list
                    )
        return cost, cost_message


    @classmethod
    def transfer_prices(
            cls, service_id, date_from, date_to, price_groups, agency, booked, contract_code,
            location_from_id, location_to_id, addon_id=None, quantity=None):
        if location_from_id is None or location_from_id == '':
            return None, 'Location From Missing'
        if location_to_id is None or location_to_id == '':
            return None, 'Location To Missing'
        if date_from is None and date_to is None:
            return None, 'Both Dates are Missing'
        if date_from is None:
            date_from = date_to
        if date_to is None:
            date_to = date_from

        # agency price
        # obtain details order by date_from asc, date_to desc
        service = Transfer.objects.get(pk=service_id)

        if (price_groups is None or not price_groups) and service.cost_type == AMOUNTS_BY_PAX:
            price = None
            price_message = 'Paxes Missing'
        elif agency is None:
            price = None
            price_message = 'Agency Not Found'
        else:
            if service.pax_range:
                price = 0
                price_message = ''
                # each group can have different details
                for group in price_groups:
                    paxes = group[0] + group[1]
                    if paxes == 0:
                        continue
                    queryset = cls._get_agency_queryset(
                        AgencyTransferDetail.objects,
                        agency.id, service_id, date_from, date_to, booked, contract_code)
                    # pax range filtering
                    queryset = queryset.filter(
                        (Q(pax_range_min=0) & Q(pax_range_max__gte=paxes)) |
                        (Q(pax_range_min__lte=paxes) & Q(pax_range_max__gte=paxes)) |
                        (Q(pax_range_min__lte=paxes) & Q(pax_range_max=0)) |
                        (Q(pax_range_min=0) & Q(pax_range_max=0))
                    )
                    # addon filtering
                    if addon_id:
                        queryset = queryset.filter(addon_id=addon_id)
                    else:
                        queryset = queryset.filter(addon_id=ADDON_FOR_NO_ADDON)

                    detail_list = list(
                        queryset.filter(
                            location_from_id=location_from_id,
                            location_to_id=location_to_id))
                    group_price = None
                    if detail_list:
                        group_price, group_price_message = cls.find_groups_amount(
                            False, service, date_from, date_to, price_groups,
                            quantity, None, detail_list
                        )
                    if group_price is None:
                        detail_list = list(
                            queryset.filter(
                                location_to_id=location_from_id,
                                location_from_id=location_to_id))
                        if not detail_list:
                            return None, "Price Not Found"
                        group_price, group_price_message = cls.find_groups_amount(
                            False, service, date_from, date_to, price_groups,
                            quantity, None, detail_list
                        )

                    if group_price:
                        price += group_price
                        price_message = group_price_message
                    else:
                        price = None
                        price_message = group_price_message
                        break
            else:
                queryset = cls._get_agency_queryset(
                    AgencyTransferDetail.objects,
                    agency.id, service_id, date_from, date_to, booked, contract_code)
                # addon filtering
                if addon_id:
                    queryset = queryset.filter(addon_id=addon_id)
                else:
                    queryset = queryset.filter(addon_id=ADDON_FOR_NO_ADDON)
                detail_list = list(
                    queryset.filter(
                        location_from_id=location_from_id,
                        location_to_id=location_to_id))
                price = None
                if detail_list:
                    price, price_message = cls.find_groups_amount(
                        False, service, date_from, date_to, price_groups,
                        quantity, None, detail_list
                    )
                if price is None:
                    detail_list = list(
                        queryset.filter(
                            location_to_id=location_from_id,
                            location_from_id=location_to_id))
                    if not detail_list:
                        return None, "Price Not Found"
                    price, price_message = cls.find_groups_amount(
                        False, service, date_from, date_to, price_groups,
                        quantity, None, detail_list
                    )

        return price, price_message


    @classmethod
    def extra_amounts(
            cls, service_id, date_from, date_to, cost_groups, price_groups,
            provider, booked, contract_code, agency,
            addon_id, quantity, parameter):
        service = Extra.objects.get(pk=service_id)

        if date_from is None and date_to is None:
            return None, 'Both Dates are Missing', None, 'Both Dates are Missing'
        if date_from is None:
            if (service.parameter_type == EXTRA_PARAMETER_TYPE_DAYS
                    or service.parameter_type == EXTRA_PARAMETER_TYPE_NIGHTS):
                return None, 'Date from is Missing', None, 'Date from is Missing'
            date_from = date_to
        if date_to is None:
            if (service.parameter_type == EXTRA_PARAMETER_TYPE_DAYS
                    or service.parameter_type == EXTRA_PARAMETER_TYPE_NIGHTS):
                return None, 'Date to is Missing', None, 'Date to is Missing'
            date_to = date_from

        # provider cost
        cost, cost_message = cls.extra_costs(service_id, date_from, date_to, cost_groups,
            provider, booked, contract_code, addon_id, quantity, parameter)

        # agency price
        price, price_message = cls.extra_prices(service_id, date_from, date_to, price_groups,
            agency, booked, contract_code, addon_id, quantity, parameter)

        return cost, cost_message, price, price_message


    @classmethod
    def extra_costs(
            cls, service_id, date_from, date_to, cost_groups, provider, booked, contract_code,
            addon_id, quantity, parameter):
        service = Extra.objects.get(pk=service_id)

        if date_from is None and date_to is None:
            return None, 'Both Dates are Missing'
        if date_from is None:
            if (service.parameter_type == EXTRA_PARAMETER_TYPE_DAYS
                    or service.parameter_type == EXTRA_PARAMETER_TYPE_NIGHTS):
                return None, 'Date from is Missing'
            date_from = date_to
        if date_to is None:
            if (service.parameter_type == EXTRA_PARAMETER_TYPE_DAYS
                    or service.parameter_type == EXTRA_PARAMETER_TYPE_NIGHTS):
                return None, 'Date to is Missing'
            date_to = date_from

        # provider cost
        # obtain details order by date_from asc, date_to desc
        if (cost_groups is None or not cost_groups) and service.cost_type == AMOUNTS_BY_PAX:
            cost = None
            cost_message = 'Empty Rooming List'
        elif provider is None:
            cost = None
            cost_message = 'Provider Not Found'
        else:
            if service.pax_range:
                cost = 0
                cost_message = ''
                # each group can have different details
                for group in cost_groups:
                    paxes = group[0] + group[1]
                    if paxes == 0:
                        continue
                    queryset = cls._get_provider_queryset(
                        ProviderExtraDetail.objects,
                        provider.id, service_id, date_from, date_to, booked, contract_code)
                    # pax range filtering
                    queryset = queryset.filter(
                        (Q(pax_range_min=0) & Q(pax_range_max__gte=paxes)) |
                        (Q(pax_range_min__lte=paxes) & Q(pax_range_max__gte=paxes)) |
                        (Q(pax_range_min__lte=paxes) & Q(pax_range_max=0)) |
                        (Q(pax_range_min=0) & Q(pax_range_max=0))
                    )
                    # addon filtering
                    if addon_id:
                        queryset = queryset.filter(addon_id=addon_id)
                    else:
                        queryset = queryset.filter(addon_id=ADDON_FOR_NO_ADDON)

                    detail_list = list(queryset)
                    if not detail_list:
                        return None, ERROR_NO_COST_FOUND % (service, provider, date_from)
                    group_cost, group_cost_message = cls.find_group_amount(
                        True, service, date_from, date_to, group,
                        quantity, parameter, detail_list
                    )
                    if group_cost:
                        cost += group_cost
                        cost_message = group_cost_message
                    else:
                        cost = None
                        cost_message = group_cost_message
                        break
            else:
                queryset = cls._get_provider_queryset(
                    ProviderExtraDetail.objects,
                    provider.id, service_id, date_from, date_to, booked, contract_code)
                # addon filtering
                if addon_id:
                    queryset = queryset.filter(addon_id=addon_id)
                else:
                    queryset = queryset.filter(addon_id=ADDON_FOR_NO_ADDON)

                detail_list = list(queryset)
                if not detail_list:
                    return None, ERROR_NO_COST_FOUND % (service, provider, date_from)
                cost, cost_message = cls.find_groups_amount(
                    True, service, date_from, date_to, cost_groups,
                    quantity, parameter, detail_list
                )
        return cost, cost_message


    @classmethod
    def extra_prices(
            cls, service_id, date_from, date_to, price_groups, agency, booked, contract_code,
            addon_id, quantity, parameter):
        service = Extra.objects.get(pk=service_id)

        if date_from is None and date_to is None:
            return None, 'Both Dates are Missing'
        if date_from is None:
            if (service.parameter_type == EXTRA_PARAMETER_TYPE_DAYS
                    or service.parameter_type == EXTRA_PARAMETER_TYPE_NIGHTS):
                return None, 'Date from is Missing'
            date_from = date_to
        if date_to is None:
            if (service.parameter_type == EXTRA_PARAMETER_TYPE_DAYS
                    or service.parameter_type == EXTRA_PARAMETER_TYPE_NIGHTS):
                return None, 'Date to is Missing'
            date_to = date_from

        # agency price
        # obtain details order by date_from asc, date_to desc
        if (price_groups is None or not price_groups) and service.cost_type == AMOUNTS_BY_PAX:
            price = None
            price_message = 'Empty Rooming List'
        elif agency is None:
            price = None
            price_message = 'Agency Not Found'
        else:
            if service.pax_range:
                price = 0
                price_message = ''
                # each group can have different details
                for group in price_groups:
                    paxes = group[0] + group[1]
                    queryset = cls._get_agency_queryset(
                        AgencyExtraDetail.objects,
                        agency.id, service_id, date_from, date_to, booked, contract_code)
                    # pax range filtering
                    queryset = queryset.filter(
                        (Q(pax_range_min=0) & Q(pax_range_max__gte=paxes)) |
                        (Q(pax_range_min__lte=paxes) & Q(pax_range_max__gte=paxes)) |
                        (Q(pax_range_min__lte=paxes) & Q(pax_range_max=0)) |
                        (Q(pax_range_min=0) & Q(pax_range_max=0))
                    )
                    # addon filtering
                    if addon_id:
                        queryset = queryset.filter(addon_id=addon_id)
                    else:
                        queryset = queryset.filter(addon_id=ADDON_FOR_NO_ADDON)

                    detail_list = list(queryset)
                    if not detail_list:
                        return None, "Price Not Found"
                    group_price, group_price_message = cls.find_group_amount(
                        False, service, date_from, date_to, group,
                        quantity, parameter, detail_list
                    )
                    if group_price:
                        price += group_price
                        price_message = group_price_message
                    else:
                        price = None
                        price_message = group_price_message
                        break
            else:
                queryset = cls._get_agency_queryset(
                    AgencyExtraDetail.objects,
                    agency.id, service_id, date_from, date_to, booked, contract_code)
                # addon filtering
                if addon_id:
                    queryset = queryset.filter(addon_id=addon_id)
                else:
                    queryset = queryset.filter(addon_id=ADDON_FOR_NO_ADDON)

                detail_list = list(queryset)
                if not detail_list:
                    return None, "Price Not Found"
                price, price_message = cls.find_groups_amount(
                    False, service, date_from, date_to, price_groups,
                    quantity, parameter, detail_list
                )
        return price, price_message


    @classmethod
    def _find_package_group_price(cls, service, date_from, date_to, group, detail_list):
        adults, children = group[0], group[1]
        free_adults, free_children = 0, 0
        if 2 in group:
            free_adults = group[2]
        if 3 in group:
            free_children = group[3]

        if adults + children - free_adults - free_children == 0:
            return 0, ''
        message = ''
        stop = False
        solved = False
        current_date = date_from
        amount = 0
        details = list(detail_list)
        # continue until solved or empty details list
        while not stop:
            # verify list not empty
            if details:
                # working with first detail
                detail = details[0]

                detail_date_from = detail.agency_service.date_from
                detail_date_to = detail.agency_service.date_to

                if current_date >= detail_date_from:
                    # verify final date included
                    end_date = detail_date_to + timedelta(days=1)
                    if end_date >= date_to:
                        # full date range
                        result = ConfigServices.get_package_price(
                            service, detail, current_date, date_to,
                            adults, children, free_adults, free_children)
                        if result is not None and result >= 0:
                            amount += result
                            solved = True
                            stop = True
                    else:
                        result = ConfigServices.get_package_price(
                            service, detail, current_date,
                            datetime(year=end_date.year, month=end_date.month, day=end_date.day),
                            adults, children, free_adults, free_children)
                        if result is not None and result >= 0:
                            amount += result
                            current_date = datetime(
                                year=end_date.year, month=end_date.month, day=end_date.day)
                # remove detail from list
                details.remove(detail)
            else:
                # empty list, no solved all days
                stop = True
                message = 'Amount Not Found for date %s' % current_date
        if not solved:
            amount = None

        if amount is not None and amount >= 0:
            return cls._round_price(amount), message
        else:
            return None, message


    @classmethod
    def _find_package_groups_price(
            cls, service, date_from, date_to, groups, detail_list):

        groups_amount = 0
        groups_message = ''
        for group in groups:
            amount, message = cls._find_package_group_price(
                service, date_from, date_to, group, detail_list)
            if amount is None:
                return None, message
            groups_amount += amount
            groups_message = message

        return groups_amount, groups_message


    @classmethod
    def find_groups_amount(
            cls, amount_for_provider, service, date_from, date_to, groups,
            quantity, parameter, detail_list):

        groups_amount = 0
        groups_message = ''
        for group in groups:
            amount, message = cls.find_group_amount(
                amount_for_provider, service, date_from, date_to, group,
                quantity, parameter, detail_list)
            if amount is None:
                return None, message
            groups_amount += float(amount)
            groups_message = message

        return groups_amount, groups_message

    @classmethod
    def find_group_amount(
            cls, amount_for_provider, service, date_from, date_to, group,
            quantity, parameter, detail_list):

        adults = group[0]
        children = group[1]
        free_adults, free_children = 0, 0
        if 2 in group:
            free_adults = group[2]
        if 3 in group:
            free_children = group[3]

        amount, message = cls.find_amount(
            amount_for_provider, service, date_from, date_to,
            adults, children, free_adults, free_children,
            quantity, parameter, detail_list)
        if amount is not None and amount >= 0:
            return amount, message
        else:
            return None, message

    @classmethod
    def find_amount(
            cls, amount_for_provider, service, date_from, date_to,
            adults, children, free_adults, free_children,
            quantity, parameter, detail_list):
        if adults + children == 0:
            return 0, ''
        message = ''
        stop = False
        solved = False
        current_date = date_from
        amount = 0
        details = list(detail_list)
        # continue until solved or empty details list
        while not stop:
            # verify list not empty
            if details:
                # working with first detail
                detail = details[0]

                # verify current dat included
                if amount_for_provider:
                    detail_date_from = detail.provider_service.date_from
                    detail_date_to = detail.provider_service.date_to
                else:
                    detail_date_from = detail.agency_service.date_from
                    detail_date_to = detail.agency_service.date_to

                if current_date >= detail_date_from:
                    # verify final date included
                    end_date = detail_date_to + timedelta(days=1)
                    if end_date >= date_to:
                        # full date range
                        result = cls._get_service_amount(
                            service, detail, current_date, date_to,
                            adults, children, free_adults, free_children,
                            quantity, parameter)
                        if result is not None and result >= 0:
                            amount += result
                            solved = True
                            stop = True
                    else:
                        result = cls._get_service_amount(
                            service, detail, current_date,
                            date(year=end_date.year, month=end_date.month, day=end_date.day),
                            adults, children, free_adults, free_children,
                            quantity, parameter)
                        if result is not None and result >= 0:
                            amount += result
                            current_date = date(
                                year=end_date.year, month=end_date.month, day=end_date.day)
                # remove detail from list
                details.remove(detail)
            else:
                # empty list, no solved all days
                stop = True
                message = 'Amount Not Found for date %s' % current_date
        if not solved:
            amount = None

        return amount, message

    @classmethod
    def _get_service_amount(
            cls, service, detail, date_from, date_to, adults, children, free_adults, free_children, quantity, parameter):
        if isinstance(service, Allotment):
            interval = date_to - date_from
            return cls._get_allotment_amount(
                service, detail, interval.days, adults, children, free_adults, free_children, quantity)
        if isinstance(service, Transfer):
            return cls._get_transfer_amount(
                service, detail, adults, children, free_adults, free_children, quantity)
        if isinstance(service, Extra):
            return cls._get_extra_amount(
                service, detail, date_from, date_to, adults, children, free_adults, free_children, quantity, parameter)
        return None

    @classmethod
    def _get_allotment_amount(
            cls, service, detail, days, adults, children, free_adults, free_children, quantity):
        if quantity is None or (quantity < 1):
            quantity = 1
        if service.cost_type == AMOUNTS_FIXED and detail.ad_1_amount is not None:
            # TODO verificar si esto es correcto
            return (adults + children - free_adults - free_children) * detail.ad_1_amount * quantity / (adults + children)
        amount = cls._find_amount(service, detail, adults, children, free_adults, free_children)
        if amount is not None and amount >= 0:
            return amount * days * quantity
        return None

    @classmethod
    def get_service_quantity(cls, service, pax_qtty, default=1):
        if not default:
            default = 1
        if not hasattr(service, 'max_capacity'):
            return default
        if service.max_capacity is None or (service.max_capacity < 1):
            return default
        return int((pax_qtty + service.max_capacity - 1) / service.max_capacity)

    @classmethod
    def _get_transfer_amount(
            cls, service, detail, adults, children, free_adults, free_children, quantity):
        quantity = cls.get_service_quantity(service, adults + children, quantity)
        if service.cost_type == AMOUNTS_FIXED and detail.ad_1_amount is not None:
            # TODO verificar si esto es correcto
            return (adults + children - free_adults - free_children) * detail.ad_1_amount * quantity / (adults + children)
        if service.cost_type == AMOUNTS_BY_PAX:
            amount = cls._find_amount(service, detail, adults, children, free_adults, free_children)
            if amount is not None and (amount >= 0):
                return amount * quantity
        return None

    @classmethod
    def _get_extra_amount(
            cls, service, detail, date_from, date_to, adults, children, free_adults, free_children, quantity, parameter):
        quantity = cls.get_service_quantity(service, adults + children, quantity)
        if service.parameter_type == EXTRA_PARAMETER_TYPE_HOURS:
            # parameter hours mandatory
            if parameter is None:
                return None
        elif service.parameter_type == EXTRA_PARAMETER_TYPE_STAY:
            parameter = 1
        else:
            interval = date_to - date_from
            if service.parameter_type == EXTRA_PARAMETER_TYPE_DAYS:
                parameter = interval.days + 1
            elif service.parameter_type == EXTRA_PARAMETER_TYPE_NIGHTS:
                parameter = interval.days
            else:
                return None
        if service.cost_type == AMOUNTS_FIXED and detail.ad_1_amount is not None:
            # TODO verificar si esto es correcto
            return (adults + children - free_adults - free_children) * detail.ad_1_amount * quantity * parameter / (adults + children)
        if service.cost_type == AMOUNTS_BY_PAX:
            amount = cls._find_amount(service, detail, adults, children, free_adults, free_children)
            if amount is not None and amount >= 0:
                return amount * quantity * parameter
        return None


    @classmethod
    def get_package_price(
            cls, service, detail, date_from, date_to, adults, children, free_adults=0, free_children=0):
        if (service.amounts_type == constants.AMOUNTS_FIXED and
                detail.ad_1_amount is not None):
            return (adults - free_adults) * detail.ad_1_amount / adults
        if service.amounts_type == constants.AMOUNTS_BY_PAX:
            if not service.grouping:
                adult_amount = 0
                if adults - free_adults > 0:
                    if detail.ad_1_amount is None:
                        return None
                    adult_amount = (adults - free_adults) * detail.ad_1_amount
                children_amount = 0
                if children - free_children > 0:
                    if detail.ch_1_ad_1_amount is None:
                        return None
                    children_amount = (children - free_children) * detail.ch_1_ad_1_amount
                amount = adult_amount + children_amount
            else:
                amount = cls.find_detail_amount(service, detail, adults, children, free_adults, free_children)
            if amount is not None and amount >= 0:
                return cls._round_price(amount)
        return None


    @classmethod
    def _find_amount(cls, service, detail, adults, children, free_adults=0, free_children=0):
        if service.grouping:
            amount = cls.find_detail_amount(
                service, detail, adults, children, free_adults, free_children)
        else:
            adult_amount = 0
            if adults > 0:
                if detail.ad_1_amount is None:
                    return None
                adult_amount = (adults - free_adults) * detail.ad_1_amount
            children_amount = 0
            if children > 0:
                if detail.ch_1_ad_1_amount is not None:
                    children_amount = (children - free_children) * detail.ch_1_ad_1_amount
                elif service.child_discount_percent is not None:
                    children_amount = (children - free_children) * float(detail.ad_1_amount) * (1.0 - float(service.child_discount_percent) / 100.0)
                else:
                    return None
            amount = adult_amount + children_amount
        return amount

    @classmethod
    def find_detail_amount(cls, service, detail, adults, children, free_adults=0, free_children=0):
        if adults == 0:
            if (children - free_children) == 1 and detail.ch_1_ad_0_amount is not None:
                return (children - free_children) * detail.ch_1_ad_0_amount
            if (children - free_children) == 2 and detail.ch_1_ad_0_amount is not None and detail.ch_2_ad_0_amount is not None:
                return detail.ch_1_ad_0_amount + detail.ch_2_ad_0_amount
            if (children == 3
                and detail.ch_1_ad_0_amount is not None
                and detail.ch_2_ad_0_amount is not None
                and detail.ch_3_ad_0_amount is not None):
                return detail.ch_1_ad_0_amount + detail.ch_2_ad_0_amount + detail.ch_3_ad_0_amount
        elif adults == 1 and detail.ad_1_amount is not None:
            if (children - free_children) == 0:
                return (adults - free_adults) * detail.ad_1_amount
            elif (children - free_children) == 1:
                if detail.ch_1_ad_1_amount is not None:
                    return (adults - free_adults) * detail.ad_1_amount + detail.ch_1_ad_1_amount
                elif  service.child_discount_percent is not None:
                    return (adults - free_adults) * float(detail.ad_1_amount) + (children - free_children) * float(detail.ad_1_amount) * (1.0 - float(service.child_discount_percent) / 100.0)
            elif (children - free_children) == 2:
                if detail.ch_1_ad_1_amount is not None and detail.ch_2_ad_1_amount is not None:
                    return (adults - free_adults) * detail.ad_1_amount + detail.ch_1_ad_1_amount + detail.ch_2_ad_1_amount
                elif  service.child_discount_percent is not None:
                    return (adults - free_adults) * float(detail.ad_1_amount) + (children - free_children) * float(detail.ad_1_amount) * (1.0 - float(service.child_discount_percent) / 100.0)
            # TODO: fix this calculation as done above
            elif children == 3:
                if detail.ch_3_ad_1_amount is not None:
                    return (adults - free_adults) * detail.ad_1_amount + (children - free_children) * detail.ch_3_ad_1_amount
                elif  service.child_discount_percent is not None:
                    return (adults - free_adults) * float(detail.ad_1_amount) + (children - free_children) * float(detail.ad_1_amount) * (1.0 - float(service.child_discount_percent) / 100.0)
        elif adults == 2 and detail.ad_2_amount is not None:
            if (children - free_children) == 0:
                return (adults - free_adults) * detail.ad_2_amount
            elif (children - free_children) == 1:
                if detail.ch_1_ad_2_amount is not None:
                    return (adults - free_adults) * detail.ad_2_amount + detail.ch_1_ad_2_amount
                elif  service.child_discount_percent is not None:
                    return (adults - free_adults) * float(detail.ad_2_amount) + (children - free_children) * float(detail.ad_2_amount) * (1.0 - float(service.child_discount_percent) / 100.0)
            elif (children - free_children) == 2:
                if detail.ch_1_ad_2_amount is not None and detail.ch_2_ad_2_amount is not None:
                    return (adults - free_adults) * detail.ad_2_amount + detail.ch_1_ad_2_amount + detail.ch_2_ad_2_amount
                elif  service.child_discount_percent is not None:
                    return (adults - free_adults) * float(detail.ad_2_amount) + (children - free_children) * float(detail.ad_2_amount) * (1.0 - float(service.child_discount_percent) / 100.0)
            # TODO: fix this calculation as done above
            elif children == 3:
                if detail.ch_3_ad_2_amount is not None:
                    return (adults - free_adults) * detail.ad_2_amount + (children - free_children) * detail.ch_3_ad_2_amount
                elif  service.child_discount_percent is not None:
                    return (adults - free_adults) * float(detail.ad_2_amount) + (children - free_children) * float(detail.ad_2_amount) * (1.0 - float(service.child_discount_percent) / 100.0)
        elif adults == 3 and detail.ad_3_amount is not None:
            if (children - free_children) == 0:
                return (adults - free_adults) * detail.ad_3_amount
            elif (children - free_children) == 1:
                if detail.ch_1_ad_3_amount is not None:
                    return (adults - free_adults) * detail.ad_3_amount + detail.ch_1_ad_3_amount
                elif  service.child_discount_percent is not None:
                    return (adults - free_adults) * float(detail.ad_3_amount) + (children - free_children) * float(detail.ad_3_amount) * (1.0 - float(service.child_discount_percent) / 100.0)
            elif (children - free_children) == 2:
                if detail.ch_1_ad_3_amount is not None and detail.ch_2_ad_3_amount is not None:
                    return (adults - free_adults) * detail.ad_3_amount + detail.ch_1_ad_3_amount + detail.ch_2_ad_3_amount
                elif  service.child_discount_percent is not None:
                    return (adults - free_adults) * float(detail.ad_3_amount) + (children - free_children) * float(detail.ad_3_amount) * (1.0 - float(service.child_discount_percent) / 100.0)
            # TODO: fix this calculation as done above
            if (children - free_children) == 3:
                if detail.ch_3_ad_3_amount is not None:
                    return (adults - free_adults) * detail.ad_3_amount + (children - free_children) * detail.ch_3_ad_3_amount
                elif  service.child_discount_percent is not None:
                    return (adults - free_adults) * float(detail.ad_3_amount) + (children - free_children) * float(detail.ad_3_amount) * (1.0 - float(service.child_discount_percent) / 100.0)
        elif adults == 4 and detail.ad_4_amount is not None:
            if (children - free_children) == 0:
                return (adults - free_adults) * detail.ad_4_amount
            elif (children - free_children) == 1:
                if detail.ch_1_ad_4_amount is not None:
                    return (adults - free_adults) * detail.ad_4_amount + detail.ch_1_ad_4_amount
                elif  service.child_discount_percent is not None:
                    return (adults - free_adults) * float(detail.ad_4_amount) + (children - free_children) * float(detail.ad_4_amount) * (1.0 - float(service.child_discount_percent) / 100.0)
            elif (children - free_children) == 2:
                if detail.ch_2_ad_4_amount is not None:
                    return (adults - free_adults) * detail.ad_4_amount + (children - free_children) * detail.ch_2_ad_4_amount
                elif  service.child_discount_percent is not None:
                    return (adults - free_adults) * float(detail.ad_4_amount) + (children - free_children) * float(detail.ad_4_amount) * (1.0 - float(service.child_discount_percent) / 100.0)
            elif (children - free_children) == 3:
                if detail.ch_3_ad_4_amount is not None:
                    return (adults - free_adults) * detail.ad_4_amount + (children - free_children) * detail.ch_3_ad_4_amount
                elif  service.child_discount_percent is not None:
                    return (adults - free_adults) * float(detail.ad_4_amount) + (children - free_children) * float(detail.ad_4_amount) * (1.0 - float(service.child_discount_percent) / 100.0)
        return None


    @classmethod
    def _get_provider_queryset(
            cls, manager, provider_id, service_id, date_from, date_to, booked, contract_code):
        if date_from is None or date_to is None:
            return manager.none()
        qs = manager.select_related('provider_service__service').filter(
                provider_service__provider_id=provider_id,
                provider_service__service_id=service_id,
                provider_service__date_to__gte=date_from,
                provider_service__date_from__lte=date_to
            ).order_by(
                'provider_service__date_from', '-provider_service__date_to'
            )
        if booked:
            qs = qs.filter(
                Q(provider_service__booked_from__isnull=True)
                | Q(provider_service__booked_from__lte=booked),
                Q(provider_service__booked_to__isnull=True)
                | Q(provider_service__booked_to__gte=booked))
        if contract_code:
            qs = qs.filter(provider_service__contract_code=contract_code)
        else:
            qs = qs.filter(provider_service__contract_code='')
        return qs


    @classmethod
    def _get_agency_queryset(
            cls, manager, agency_id, service_id, date_from, date_to, booked, contract_code=''):
        valid_contract_code = contract_code
        if contract_code is None:
            valid_contract_code = ''
        if date_from is None or date_to is None:
            return manager.none()
        qs = manager.select_related(
            'agency_service__service'
            ).filter(
                agency_service__agency_id=agency_id,
                agency_service__service_id=service_id,
                agency_service__date_to__gte=date_from,
                agency_service__date_from__lte=date_to,
            ).order_by(
                'agency_service__date_from', '-agency_service__date_to'
            )
        if booked:
            qs = qs.filter(
                Q(agency_service__booked_from__isnull=True)
                | Q(agency_service__booked_from__lte=booked),
                Q(agency_service__booked_to__isnull=True)
                | Q(agency_service__booked_to__gte=booked))
        # prices dont use contract_code
        qs = qs.filter(agency_service__contract_code=valid_contract_code)
        return qs


    @classmethod
    def transfer_time(
            cls, schedule_from_id, schedule_to_id, location_from_id, location_to_id,
            time_from, time_to, transfer_id=None, allotment_from_id=None):
        if transfer_id:
            transfer = Transfer.objects.get(pk=transfer_id)
            if transfer.has_pickup_time:
                if allotment_from_id and location_to_id:
                    allotment = Allotment.objects.get(pk=allotment_from_id)
                    pickup_times = list(TransferPickupTime.objects.filter(
                        transfer_zone__transfer = transfer,
                        transfer_zone__allotmenttransferzone__allotment = allotment,
                        location = location_to_id
                    ))
                    if pickup_times:
                        return pickup_times[0].pickup_time, None
                    else:
                        return None, 'Pickup Time Missing for Pickup and Location to'
                else:
                    return None, 'Pickup Time Missing - Pickup and Locationto are required'

        if (time_from):
            return time_from, 'Scheduled time From'
        if (schedule_from_id and schedule_from_id != ''):
            # pickup schedule specified
            schedule = Schedule.objects.get(pk=schedule_from_id)
            return schedule.time, 'Scheduled Pickup'
        if (schedule_to_id and schedule_to_id != ''):
            # dropoff schedule specified
            schedule = Schedule.objects.get(pk=schedule_to_id)
            if location_from_id is None or location_from_id == '':
                return None, 'Location From Missing'
            if location_to_id is None or location_to_id == '':
                return None, 'Location To Missing'
            intervals = list(
                TransferInterval.objects
                .filter(t_location_from_id=location_from_id)
                .filter(location_id=location_to_id))
            if intervals:
                if not time_to:
                    time_to = schedule.time
                else:
                    time_to = datetime.strptime(time_to, '%H:%M:%S')
                it = intervals[0].interval
                interval = timedelta(hours=it.hour, minutes=it.minute)
                drop_time = timedelta(hours=time_to.hour, minutes=time_to.minute)
                pickup = drop_time - interval
                if pickup < timedelta(hours=0):
                    pickup = pickup + timedelta(hours=24)
                pickup_time = time(hour=pickup.seconds // 3600, minute=(pickup.seconds // 60) % 60)
                return pickup_time, 'Scheduled Droppoff'
            else:
                return None, 'Transfer Interval Missing for those Locations'
        else:
            # no schedule
            return None, 'Non-Scheduled Time - Set Manually'


    @classmethod
    def generate_agency_allotments_amounts_from_providers_allotments(cls, providers_allotments, is_update):
        """
        generate_agency_allotments_amounts_from_providers_allotments
        """
        from reservas.custom_settings import AGENCY_FOR_AMOUNTS

        try:
            dst_agency = Agency.objects.get(id=AGENCY_FOR_AMOUNTS)
            for provider_allotment in providers_allotments:
                try:
                    cls.generate_agency_allotment_amounts_from_provider_allotment(
                        provider_allotment, dst_agency, is_update)
                except Exception as ex:
                    print('EXCEPTION config services - generate_agency_allotments_amounts_from_providers_allotments : ' + ex.__str__())

        except Agency.DoesNotExist as ex:
            # 'Destination Agency not Found'
            print('EXCEPTION config services - generate_agency_allotments_amounts_from_providers_allotments : ' + ex.__str__())
            return


    @classmethod
    def generate_agency_transfers_amounts_from_providers_transfers(cls, providers_transfers, is_update):
        """
        generate_agency_transfers_amounts_from_providers_transfers
        """
        from reservas.custom_settings import AGENCY_FOR_AMOUNTS

        try:
            dst_agency = Agency.objects.get(id=AGENCY_FOR_AMOUNTS)
            for provider_transfer in providers_transfers:
                try:
                    cls.generate_agency_transfer_amounts_from_provider_transfer(
                        provider_transfer, dst_agency, is_update)
                except Exception as ex:
                    print('EXCEPTION config services - generate_agency_transfers_amounts_from_providers_transfers : ' + ex.__str__())

        except Agency.DoesNotExist as ex:
            # 'Destination Agency not Found'
            print('EXCEPTION config services - generate_agency_transfers_amounts_from_providers_transfers : ' + ex.__str__())
            return


    @classmethod
    def generate_agency_extras_amounts_from_providers_extras(cls, providers_extras, is_update):
        """
        generate_agency_extras_amounts_from_providers_extras
        """
        from reservas.custom_settings import AGENCY_FOR_AMOUNTS

        try:
            dst_agency = Agency.objects.get(id=AGENCY_FOR_AMOUNTS)
            for provider_extra in providers_extras:
                try:
                    cls.generate_agency_extra_amounts_from_provider_extra(
                        provider_extra, dst_agency, is_update)
                except Exception as ex:
                    print('EXCEPTION config services - generate_agency_extras_amounts_from_providers_extras : ' + ex.__str__())

        except Agency.DoesNotExist as ex:
            # 'Destination Agency not Found'
            print('EXCEPTION config services - generate_agency_extras_amounts_from_providers_extras : ' + ex.__str__())
            return


    @classmethod
    def generate_agency_allotment_amounts_from_provider_allotment(cls, src_provider_service, dst_agency, is_update):
        dst_agency_service, created = AgencyAllotmentService.objects.get_or_create(
            agency_id=dst_agency.id,
            date_from=src_provider_service.date_from,
            date_to=src_provider_service.date_to,
            booked_from=src_provider_service.booked_from,
            booked_to=src_provider_service.booked_to,
            contract_code=src_provider_service.contract_code,
            service_id=src_provider_service.service_id
        )
        if created:
            dst_agency_service.booked_from = src_provider_service.booked_from
            dst_agency_service.booked_to = src_provider_service.booked_to

        # find details
        details = list(
            ProviderAllotmentDetail.objects.filter(provider_service=src_provider_service))
        # for each src provider detail create dst agency detail
        for detail in details:
            if is_update:
                # update - dont modify if exists
                agency_detail, created = AgencyAllotmentDetail.objects.get_or_create(
                    agency_service_id=dst_agency_service.id,
                    room_type_id=detail.room_type_id,
                    board_type=detail.board_type,
                    addon_id=detail.addon_id,
                    pax_range_min=detail.pax_range_min,
                    pax_range_max=detail.pax_range_max,
                    defaults=cls.calculate_default_amounts(
                        detail, 0, dst_agency.gain_percent)
                )
            else:
                # rewrite - modify if exists
                agency_detail, created = AgencyAllotmentDetail.objects.update_or_create(
                    agency_service_id=dst_agency_service.id,
                    room_type_id=detail.room_type_id,
                    board_type=detail.board_type,
                    addon_id=detail.addon_id,
                    pax_range_min=detail.pax_range_min,
                    pax_range_max=detail.pax_range_max,
                    defaults=cls.calculate_default_amounts(
                        detail, 0, dst_agency.gain_percent)
                )


    @classmethod
    def generate_agency_transfer_amounts_from_provider_transfer(cls, src_provider_service, dst_agency, is_update):
        dst_agency_service, created = AgencyTransferService.objects.get_or_create(
            agency_id=dst_agency.id,
            date_from=src_provider_service.date_from,
            date_to=src_provider_service.date_to,
            contract_code=src_provider_service.contract_code,
            service_id=src_provider_service.service_id
        )
        if created:
            dst_agency_service.booked_from = src_provider_service.booked_from
            dst_agency_service.booked_to = src_provider_service.booked_to

        # find details
        details = list(
            ProviderTransferDetail.objects.filter(provider_service=src_provider_service))
        # for each src provider detail create dst agency detail
        for detail in details:
            if is_update:
                # update - dont modify if exists
                agency_detail, created = AgencyTransferDetail.objects.get_or_create(
                    agency_service_id=dst_agency_service.id,
                    location_from_id=detail.location_from_id,
                    location_to_id=detail.location_to_id,
                    addon_id=detail.addon_id,
                    pax_range_min=detail.pax_range_min,
                    pax_range_max=detail.pax_range_max,
                    not_reversible=False,
                    defaults=cls.calculate_default_amounts(
                        detail, 0, dst_agency.gain_percent)
                )
            else:
                # rewrite - modify if exists
                agency_detail, created = AgencyTransferDetail.objects.update_or_create(
                    agency_service_id=dst_agency_service.id,
                    location_from_id=detail.location_from_id,
                    location_to_id=detail.location_to_id,
                    addon_id=detail.addon_id,
                    pax_range_min=detail.pax_range_min,
                    pax_range_max=detail.pax_range_max,
                    not_reversible=False,
                    defaults=cls.calculate_default_amounts(
                        detail, 0, dst_agency.gain_percent)
                )


    @classmethod
    def generate_agency_extra_amounts_from_provider_extra(cls, src_provider_service, dst_agency, is_update):
        dst_agency_service, created = AgencyExtraService.objects.get_or_create(
            agency_id=dst_agency.id,
            date_from=src_provider_service.date_from,
            date_to=src_provider_service.date_to,
            contract_code=src_provider_service.contract_code,
            service_id=src_provider_service.service_id
        )
        if created:
            dst_agency_service.booked_from = src_provider_service.booked_from
            dst_agency_service.booked_to = src_provider_service.booked_to

        # find details
        details = list(
            ProviderExtraDetail.objects.filter(provider_service=src_provider_service))
        # for each src provider detail create dst agency detail
        for detail in details:
            if is_update:
                # update - dont modify if exists
                agency_detail, created = AgencyExtraDetail.objects.get_or_create(
                    agency_service_id=dst_agency_service.id,
                    addon_id=detail.addon_id,
                    pax_range_min=detail.pax_range_min,
                    pax_range_max=detail.pax_range_max,
                    defaults=cls.calculate_default_amounts(
                        detail, 0, dst_agency.gain_percent)
                )
            else:
                # rewrite - modify if exists
                agency_detail, created = AgencyExtraDetail.objects.update_or_create(
                    agency_service_id=dst_agency_service.id,
                    addon_id=detail.addon_id,
                    pax_range_min=detail.pax_range_min,
                    pax_range_max=detail.pax_range_max,
                    defaults=cls.calculate_default_amounts(
                        detail, 0, dst_agency.gain_percent)
                )

    @classmethod
    def update_detail_amount(cls, detail_amount, diff_percent, diff_amount, min_diff, max_diff, apply_round=True):
        if (diff_percent is None or diff_percent == 0) and (
            diff_amount is None or diff_amount == 0):
            return detail_amount
        if detail_amount is None:
            return None
        result = float(detail_amount)
        diff = 0.0
        if diff_percent is not None:
            diff += result * float(diff_percent) / 100.0
        if diff_amount is not None:
            diff += float(diff_amount)
        if min_diff is not None:
            if abs(diff) < abs(min_diff):
                diff = math.copysign(min_diff, diff)
        if max_diff is not None:
            if abs(diff) > abs(max_diff):
                diff = math.copysign(max_diff, diff)
        if apply_round:
            return round(0.499999 + result + diff)
        return round(result + diff, 2)

    @classmethod
    def next_year_catalog_service_amounts(
            cls, catalog_service, diff_percent,
            diff_amount, min_diff, max_diff):

        # catalog_service_pk = catalog_service.pk

        catalog_details = catalog_service.get_detail_objects()
        new_catalog_service = catalog_service
        new_catalog_service.pk = None
        new_catalog_service.id = None
        one_year = relativedelta(years=1)
        if new_catalog_service.date_from:
            new_catalog_service.date_from = new_catalog_service.date_from + one_year
        if new_catalog_service.date_to:
            new_catalog_service.date_to = new_catalog_service.date_to + one_year
        if new_catalog_service.booked_from:
            new_catalog_service.booked_from = new_catalog_service.booked_from + one_year
        if new_catalog_service.booked_to:
            new_catalog_service.booked_to = new_catalog_service.booked_to + one_year
        new_catalog_service.save()

        details_success_count = 0
        details_error_count = 0
        details_error_messages = []

        for detail in catalog_details:
            try:
                new_detail = detail
                new_detail.pk = None
                new_detail.id = None

                apply_round = True
                if not isinstance(
                        new_detail,
                        (AgencyAllotmentDetail, AgencyTransferDetail, AgencyExtraDetail)):
                    apply_round = False

                new_detail.ad_1_amount = cls.update_detail_amount(
                    detail.ad_1_amount, diff_percent, diff_amount, min_diff, max_diff, apply_round)
                new_detail.ad_2_amount = cls.update_detail_amount(
                    detail.ad_2_amount, diff_percent, diff_amount, min_diff, max_diff, apply_round)
                new_detail.ad_3_amount = cls.update_detail_amount(
                    detail.ad_3_amount, diff_percent, diff_amount, min_diff, max_diff, apply_round)
                new_detail.ad_4_amount = cls.update_detail_amount(
                    detail.ad_4_amount, diff_percent, diff_amount, min_diff, max_diff, apply_round)
                new_detail.ch_1_ad_0_amount = cls.update_detail_amount(
                    detail.ch_1_ad_0_amount, diff_percent, diff_amount, min_diff, max_diff, apply_round)
                new_detail.ch_1_ad_1_amount = cls.update_detail_amount(
                    detail.ch_1_ad_1_amount, diff_percent, diff_amount, min_diff, max_diff, apply_round)
                new_detail.ch_1_ad_2_amount = cls.update_detail_amount(
                    detail.ch_1_ad_2_amount, diff_percent, diff_amount, min_diff, max_diff, apply_round)
                new_detail.ch_1_ad_3_amount = cls.update_detail_amount(
                    detail.ch_1_ad_3_amount, diff_percent, diff_amount, min_diff, max_diff, apply_round)
                new_detail.ch_1_ad_4_amount = cls.update_detail_amount(
                    detail.ch_1_ad_4_amount, diff_percent, diff_amount, min_diff, max_diff, apply_round)
                new_detail.ch_2_ad_0_amount = cls.update_detail_amount(
                    detail.ch_2_ad_0_amount, diff_percent, diff_amount, min_diff, max_diff, apply_round)
                new_detail.ch_2_ad_1_amount = cls.update_detail_amount(
                    detail.ch_2_ad_1_amount, diff_percent, diff_amount, min_diff, max_diff, apply_round)
                new_detail.ch_2_ad_2_amount = cls.update_detail_amount(
                    detail.ch_2_ad_2_amount, diff_percent, diff_amount, min_diff, max_diff, apply_round)
                new_detail.ch_2_ad_3_amount = cls.update_detail_amount(
                    detail.ch_2_ad_3_amount, diff_percent, diff_amount, min_diff, max_diff, apply_round)
                new_detail.ch_2_ad_4_amount = cls.update_detail_amount(
                    detail.ch_2_ad_4_amount, diff_percent, diff_amount, min_diff, max_diff, apply_round)
                new_detail.ch_3_ad_0_amount = cls.update_detail_amount(
                    detail.ch_3_ad_0_amount, diff_percent, diff_amount, min_diff, max_diff, apply_round)
                new_detail.ch_3_ad_1_amount = cls.update_detail_amount(
                    detail.ch_3_ad_1_amount, diff_percent, diff_amount, min_diff, max_diff, apply_round)
                new_detail.ch_3_ad_2_amount = cls.update_detail_amount(
                    detail.ch_3_ad_2_amount, diff_percent, diff_amount, min_diff, max_diff, apply_round)
                new_detail.ch_3_ad_3_amount = cls.update_detail_amount(
                    detail.ch_3_ad_3_amount, diff_percent, diff_amount, min_diff, max_diff, apply_round)
                new_detail.ch_3_ad_4_amount = cls.update_detail_amount(
                    detail.ch_3_ad_4_amount, diff_percent, diff_amount, min_diff, max_diff, apply_round)

                if isinstance(
                        new_detail,
                        (AgencyAllotmentDetail, AgencyTransferDetail, AgencyExtraDetail)):
                    new_detail.agency_service = new_catalog_service
                else:
                    new_detail.provider_service = new_catalog_service
                new_detail.save()

                details_success_count += 1
            except Exception as ex:
                details_error_count += 1
                details_error_messages.append(
                    'Error for detail : %s - %s' % (detail, ex.__str__()))
                # print('EXCEPTION config services - next_year_catalog_service_amounts : ' + ex.__str__())
        return details_success_count, details_error_count, details_error_messages

    @classmethod
    def next_year_catalog_amounts(
            cls, catalog_model, catalog_service_ids, diff_percent=None,
            diff_amount=None, min_diff=None, max_diff=None):

        services_success_count = 0
        services_error_count = 0
        services_error_messages = []
        details_success_count = 0
        details_error_count = 0
        details_error_messages = []
        for catalog_service_id in catalog_service_ids:
            try:
                catalog_service = catalog_model.objects.get(id=catalog_service_id)
                with transaction.atomic():
                    tmp_success_count, tmp_error_count, tmp_error_messages = \
                        cls.next_year_catalog_service_amounts(
                            catalog_service, diff_percent,
                            diff_amount,
                            min_diff,
                            max_diff)
                details_success_count += tmp_success_count
                details_error_count += tmp_error_count
                details_error_messages.extend(tmp_error_messages)
                services_success_count += 1
            except IntegrityError:
                services_error_count += 1
                services_error_messages.append(
                    '%s - This registry already has entry on new year' % catalog_service)
                # print('{} config services - next_year_catalog_amounts : {}'.format(ex.__class__.__name__, ex))
        return {
            'services_success_count': services_success_count,
            'services_error_count': services_error_count,
            'services_error_messages': services_error_messages,
            'details_success_count': details_success_count,
            'details_error_count': details_error_count,
            'details_error_messages': details_error_messages
        }

    @classmethod
    def list_allotment_details(cls, allotment, agency, date_from, date_to, booked_from, booked_to):
        qs = AgencyAllotmentDetail.objects.all()
        qs = qs.filter(
            agency_service__agency=agency,
            agency_service__service=allotment.id)
        if date_from:
            qs = qs.filter(agency_service__date_to__gte=date_from)
        if date_to:
            qs = qs.filter(agency_service__date_from__lte=date_to)
        if booked_from:
            qs = qs.filter(Q(agency_service__booked_to__gte=booked_from) |
                           Q(agency_service__booked_to__isnull=True))
        if booked_to:
            qs = qs.filter(Q(agency_service__booked_from__lte=booked_to) |
                           Q(agency_service__booked_from__isnull=True))
        qs = qs.order_by(
            'board_type', 'room_type', 'addon', 'pax_range_min', '-pax_range_max',
            'agency_service__date_from', '-agency_service__date_to')
        return list(qs)

    @classmethod
    def list_allotment_costs_details(cls, allotment, date_from, date_to, booked_from, booked_to):
        qs = ProviderAllotmentDetail.objects.all()
        qs = qs.filter(
            provider_service__service=allotment.id)
        if date_from:
            qs = qs.filter(provider_service__date_to__gte=date_from)
        if date_to:
            qs = qs.filter(provider_service__date_from__lte=date_to)
        if booked_from:
            qs = qs.filter(Q(provider_service__booked_to__gte=booked_from) |
                           Q(provider_service__booked_to__isnull=True))
        if booked_to:
            qs = qs.filter(Q(provider_service__booked_from__lte=booked_to) |
                           Q(provider_service__booked_from__isnull=True))
        qs = qs.order_by(
            'board_type', 'room_type', 'addon', 'provider_service__provider', 'pax_range_min', '-pax_range_max',
            'provider_service__date_from', '-provider_service__date_to')
        return list(qs)

    @classmethod
    def list_transfer_details(cls, transfer, agency, date_from='', date_to='', booked_from='', booked_to=''):
        # raw_sql collect transfer routes with their reverses excluding
        # not_reversible routes and explicitly specified ones
        raw_sql = """
        SELECT sq_pd.*
        FROM
        (
        SELECT
            atd.id, atd.location_from_id, atd.location_to_id,
            ats.date_from, atd.ad_1_amount, atd.pax_range_min, atd.pax_range_max
          FROM `config_agencytransferdetail` atd
          JOIN `config_agencytransferservice` ats
            ON ats.id = atd.`agency_service_id`
          JOIN `config_location` l1
            ON l1.id = atd.location_from_id
          JOIN `config_location` l2
            ON l2.id = atd.location_to_id
          WHERE
            ats.service_id = %s AND ats.agency_id = %s
            AND ats.date_to >= %s AND ats.date_from <= %s
        UNION
        SELECT
            atd1.id, l2.id AS location_from_id, l1.id AS location_to_id,
            ats.date_from, atd1.ad_1_amount, atd1.pax_range_min, atd1.pax_range_max
          FROM
            `config_agencytransferdetail` atd1
          JOIN `config_agencytransferservice` ats
            ON ats.id = atd1.`agency_service_id`
          JOIN `config_location` l1
            ON l1.id = atd1.location_from_id
          JOIN `config_location` l2
            ON l2.id = atd1.location_to_id
          LEFT JOIN `config_agencytransferdetail` atd2
            ON atd2.`agency_service_id` = atd1.`agency_service_id`
            AND atd2.`location_from_id` = atd1.`location_to_id`
            AND atd2.`location_to_id` = atd1.`location_from_id`
          WHERE
            atd2.id IS NULL
            AND ats.service_id = %s AND ats.agency_id = %s
            AND ats.date_to >= %s AND ats.date_from <= %s
            AND atd1.not_reversible = FALSE
        ) sq_pd
        ORDER BY
          sq_pd.location_from_id,
          sq_pd.location_to_id,
          sq_pd.date_from """
        qs = AgencyTransferDetail.objects.raw(raw_sql,
                                              [transfer.id,
                                               agency.id,
                                               date_from,
                                               date_to,
                                               transfer.id,
                                               agency.id,
                                               date_from,
                                               date_to])
        # qs = AgencyTransferDetail.objects.annotate(
        #     origin=F('location_from__name'),
        #     destination=F('location_to__name'))
        # qs = qs.filter(
        #     agency_service__agency=agency,
        #     agency_service__service=transfer.id)
        # if date_from:
        #     qs = qs.filter(agency_service__date_to__gte=date_from)
        # if date_to:
        #     qs = qs.filter(agency_service__date_from__lte=date_to)
        # reversed_qs = qs.filter(not_reversible=False)#.annotate(
        #     origin=F('location_to__name'),
        #     destination=F('location_from__name'))
        # print(qs.count())
        # print(reversed_qs.count())
        # qs = qs.union(reversed_qs, all=True)
        # print(qs[6].__dict__)
        # qs = qs.order_by(
        #     'origin', 'destination', 'addon', 'pax_range_min', '-pax_range_max',
        #     'agency_service__date_from', '-agency_service__date_to')
        return list(qs)

    @classmethod
    def list_transfer_costs_details(cls, transfer, date_from='', date_to='', booked_from='', booked_to=''):
        # raw_sql collect transfer routes with their reverses excluding
        # not_reversible routes and explicitly specified ones
        raw_sql = """
        SELECT sq_pd.*
        FROM
        (
        SELECT
            p.id as provider_id, p.name as provider_name, ptd.id, ptd.location_from_id, ptd.location_to_id,
            pts.date_from, ptd.ad_1_amount, ptd.pax_range_min, ptd.pax_range_max
          FROM `config_providertransferdetail` ptd
          JOIN `config_providertransferservice` pts
            ON pts.id = ptd.`provider_service_id`
          JOIN `finance_provider` p
            ON p.id = pts.`provider_id`
          JOIN `config_location` l1
            ON l1.id = ptd.location_from_id
          JOIN `config_location` l2
            ON l2.id = ptd.location_to_id
          WHERE
            pts.service_id = %s AND pts.date_to >= %s AND pts.date_from <= %s
        UNION
        SELECT
            p.id as provider_id, p.name as provider_name, ptd1.id, l2.id AS location_from_id, l1.id AS location_to_id,
            pts.date_from, ptd1.ad_1_amount, ptd1.pax_range_min, ptd1.pax_range_max
          FROM
            `config_providertransferdetail` ptd1
          JOIN `config_providertransferservice` pts
            ON pts.id = ptd1.`provider_service_id`
          JOIN `finance_provider` p
            ON p.id = pts.`provider_id`
          JOIN `config_location` l1
            ON l1.id = ptd1.location_from_id
          JOIN `config_location` l2
            ON l2.id = ptd1.location_to_id
          LEFT JOIN `config_providertransferdetail` ptd2
            ON ptd2.`provider_service_id` = ptd1.`provider_service_id`
            AND ptd2.`location_from_id` = ptd1.`location_to_id`
            AND ptd2.`location_to_id` = ptd1.`location_from_id`
          WHERE
            ptd2.id IS NULL
            AND pts.service_id = %s AND pts.date_to >= %s AND pts.date_from <= %s
        ) sq_pd
        ORDER BY
          sq_pd.location_from_id,
          sq_pd.location_to_id,
          sq_pd.provider_name,
          sq_pd.provider_id,
          sq_pd.date_from """
        qs = ProviderTransferDetail.objects.raw(raw_sql,
                                              [transfer.id,
                                               date_from,
                                               date_to,
                                               transfer.id,
                                               date_from,
                                               date_to])
        return list(qs)

    @classmethod
    def list_extra_details(cls, extra, agency, date_from, date_to, booked_from, booked_to):
        qs = AgencyExtraDetail.objects.all()
        qs = qs.filter(
            agency_service__agency=agency,
            agency_service__service=extra.id)
        if date_from:
            qs = qs.filter(agency_service__date_to__gte=date_from)
        if date_to:
            qs = qs.filter(agency_service__date_from__lte=date_to)
        if booked_from:
            qs = qs.filter(Q(agency_service__booked_to__gte=booked_from) |
                           Q(agency_service__booked_to__isnull=True))
        if booked_to:
            qs = qs.filter(Q(agency_service__booked_from__lte=booked_to) |
                           Q(agency_service__booked_from__isnull=True))
        qs = qs.order_by(
            'addon', 'pax_range_min', '-pax_range_max',
            'agency_service__date_from', '-agency_service__date_to')
        return list(qs)

    @classmethod
    def list_extra_costs_details(cls, extra, date_from, date_to, booked_from, booked_to):
        qs = ProviderExtraDetail.objects.all()
        qs = qs.filter(
            provider_service__service=extra.id)
        if date_from:
            qs = qs.filter(provider_service__date_to__gte=date_from)
        if date_to:
            qs = qs.filter(provider_service__date_from__lte=date_to)
        if booked_from:
            qs = qs.filter(Q(agency_service__booked_to__gte=booked_from) |
                           Q(agency_service__booked_to__isnull=True))
        if booked_to:
            qs = qs.filter(Q(agency_service__booked_from__lte=booked_to) |
                           Q(agency_service__booked_from__isnull=True))
        qs = qs.order_by(
            'addon', 'provider_service__provider', 'pax_range_min', '-pax_range_max',
            'provider_service__date_from', '-provider_service__date_to')
        return list(qs)

    # @classmethod
    # def list_package_details(cls, package, agency, date_from, date_to):
    #     qs = AgencyPackageDetail.objects.all()
    #     qs = qs.filter(
    #         agency_service__agency=agency,
    #         agency_service__service=package.id)
    #     if date_from:
    #         qs = qs.filter(agency_service__date_to__gte=date_from)
    #     if date_to:
    #         qs = qs.filter(agency_service__date_from__lte=date_to)
    #     qs = qs.order_by(
    #         'pax_range_min', '-pax_range_max',
    #         'agency_service__date_from', '-agency_service__date_to')
    #     return list(qs)


    @classmethod
    def list_service_prices(cls, service, agency, date_from, date_to, booked_from, booked_to):
        if service.category == 'A':
            return cls.list_allotment_details(service, agency, date_from, date_to, booked_from, booked_to)
        if service.category == 'T':
            return cls.list_transfer_details(service, agency, date_from, date_to, booked_from, booked_to)
        if service.category == 'E':
            return cls.list_extra_details(service, agency, date_from, date_to, booked_from, booked_to)
        # if service.category == 'P':
        #     return cls.list_package_details(service, agency, date_from, date_to)


    @classmethod
    def list_service_costs(cls, service, date_from, date_to, booked_from, booked_to):
        if service.category == 'A':
            return cls.list_allotment_costs_details(service, date_from, date_to, booked_from, booked_to)
        if service.category == 'T':
            return cls.list_transfer_costs_details(service, date_from, date_to, booked_from, booked_to)
        if service.category == 'E':
            return cls.list_extra_costs_details(service, date_from, date_to, booked_from, booked_to)


    @classmethod
    def copy_book_service_data(cls, dst_service, src_service):
        dst_service.name = src_service.name
        dst_service.description = src_service.description
        dst_service.base_service = src_service.base_service
        dst_service.base_location = src_service.base_location
        dst_service.service_addon = src_service.service_addon
        dst_service.time = src_service.time


    @classmethod
    def copy_book_allotment_data(cls, dst_service, src_service):
        cls.copy_book_service_data(dst_service, src_service)
        dst_service.room_type = src_service.room_type
        dst_service.board_type = src_service.board_type


    @classmethod
    def copy_book_transfer_data(cls, dst_service, src_service):
        cls.copy_book_service_data(dst_service, src_service)
        dst_service.location_from = src_service.location_from
        dst_service.location_to = src_service.location_to
        dst_service.place_from = src_service.place_from
        dst_service.place_to = src_service.place_to
        dst_service.schedule_from = src_service.schedule_from
        dst_service.schedule_to = src_service.schedule_to
        dst_service.schedule_time_from = src_service.schedule_time_from
        dst_service.schedule_time_to = src_service.schedule_time_to
        dst_service.pickup = src_service.pickup
        dst_service.dropoff = src_service.dropoff
        dst_service.quantity = src_service.quantity


    @classmethod
    def copy_book_extra_data(cls, dst_service, src_service):
        cls.copy_book_service_data(dst_service, src_service)
        dst_service.pickup_office = src_service.pickup_office
        dst_service.dropoff_office = src_service.dropoff_office
        dst_service.quantity = src_service.quantity
        dst_service.parameter = src_service.parameter


    @classmethod
    def clone_catalog_details(cls, old_id, new_catalog_service):

        if isinstance(new_catalog_service, ProviderAllotmentService):
            CatalogServiceClass = ProviderAllotmentService
            CatalogDetailClass = ProviderAllotmentDetail
            filter_field = 'provider_service'
        elif isinstance(new_catalog_service, ProviderTransferService):
            CatalogServiceClass = ProviderTransferService
            CatalogDetailClass = ProviderTransferDetail
            filter_field = 'provider_service'
        elif isinstance(new_catalog_service, ProviderExtraService):
            CatalogServiceClass = ProviderExtraService
            CatalogDetailClass = ProviderExtraDetail
            filter_field = 'provider_service'
        elif isinstance(new_catalog_service, AgencyAllotmentService):
            CatalogServiceClass = AgencyAllotmentService
            CatalogDetailClass = AgencyAllotmentDetail
            filter_field = 'agency_service'
        elif isinstance(new_catalog_service, AgencyTransferService):
            CatalogServiceClass = AgencyTransferService
            CatalogDetailClass = AgencyTransferDetail
            filter_field = 'agency_service'
        elif isinstance(new_catalog_service, AgencyExtraService):
            CatalogServiceClass = AgencyExtraService
            CatalogDetailClass = AgencyExtraDetail
            filter_field = 'agency_service'
        else:
            return

        old_catalog_service = CatalogServiceClass.objects.get(pk=old_id)
        details = list(CatalogDetailClass.objects.filter(**{filter_field: old_catalog_service}))
        for detail in details:
            cls._clone_catalog_detail(detail, new_catalog_service)


    @classmethod
    def _clone_catalog_detail(cls, catalog_detail, catalog_service):

        catalog_detail.pk = None
        catalog_detail.id = None
        if hasattr(catalog_detail, 'provider_service'):
            catalog_detail.provider_service = catalog_service
            catalog_detail.provider_service_id = catalog_service.pk
        else :
            catalog_detail.agency_service = catalog_service
            catalog_detail.agency_service_id = catalog_service.pk
        catalog_detail.save()
