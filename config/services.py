from __future__ import unicode_literals
"""
config services
"""


from datetime import date, timedelta, time, datetime

from django.db.models import Q

from config.constants import (
    SERVICE_CATEGORY_EXTRA, SERVICE_CATEGORY_ALLOTMENT, SERVICE_CATEGORY_TRANSFER,
    AMOUNTS_FIXED, AMOUNTS_BY_PAX,
    EXTRA_PARAMETER_TYPE_HOURS, EXTRA_PARAMETER_TYPE_DAYS,
    EXTRA_PARAMETER_TYPE_NIGHTS, EXTRA_PARAMETER_TYPE_STAY,
    ERROR_INVALID_SERVICE_CATEGORY)
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


class ConfigServices(object):
    """
    ConfigServices
    """

    @classmethod
    def copy_agency_amounts(cls, src_agency, dst_agency, is_update):
        """
        copy_agency_amounts
        """
        cls._copy_allotments(src_agency, dst_agency, is_update)
        cls._copy_transfers(src_agency, dst_agency, is_update)
        cls._copy_extras(src_agency, dst_agency, is_update)


    @classmethod
    def _copy_allotments(cls, src_agency, dst_agency, is_update):
        # find agencyservice list
        src_agency_services = AgencyAllotmentService.objects.filter(agency=src_agency.id)
        # for each agencyservice create agencyservice
        for src_agency_service in src_agency_services:
            dst_agency_service, created = AgencyAllotmentService.objects.get_or_create(
                agency_id=dst_agency.id,
                date_from=src_agency_service.date_from,
                date_to=src_agency_service.date_to,
                service_id=src_agency_service.service_id
            )
            # find details
            details = list(
                AgencyAllotmentDetail.objects.filter(agency_service=src_agency_service))
            # for each src agency detail create dst agency detail
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
                            detail, src_agency.gain_percent, dst_agency.gain_percent)
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
                            detail, src_agency.gain_percent, dst_agency.gain_percent)
                    )


    @classmethod
    def _copy_transfers(cls, src_agency, dst_agency, is_update):
        # find agencyservice list
        src_agency_services = list(AgencyTransferService.objects.filter(agency=src_agency.id))
        # for each agencyservice create agencyservice
        for src_agency_service in src_agency_services:
            dst_agency_service, created = AgencyTransferService.objects.get_or_create(
                agency_id=dst_agency.id,
                date_from=src_agency_service.date_from,
                date_to=src_agency_service.date_to,
                service_id=src_agency_service.service_id
            )
            # find details
            details = list(
                AgencyTransferDetail.objects.filter(agency_service=src_agency_service))
            # for each src agency detail create dst agency detail
            for detail in details:
                if is_update:
                    # update - dont modify if exists
                    agency_detail, created = AgencyTransferDetail.objects.get_or_create(
                        agency_service_id=dst_agency_service.id,
                        a_location_from_id=detail.a_location_from_id,
                        a_location_to_id=detail.a_location_to_id,
                        addon_id=detail.addon_id,
                        pax_range_min=detail.pax_range_min,
                        pax_range_max=detail.pax_range_max,
                        defaults=cls.calculate_default_amounts(
                            detail, src_agency.gain_percent, dst_agency.gain_percent)
                    )
                else:
                    # rewrite - modify if exists
                    agency_detail, created = AgencyTransferDetail.objects.update_or_create(
                        agency_service_id=dst_agency_service.id,
                        a_location_from_id=detail.a_location_from_id,
                        a_location_to_id=detail.a_location_to_id,
                        addon_id=detail.addon_id,
                        pax_range_min=detail.pax_range_min,
                        pax_range_max=detail.pax_range_max,
                        defaults=cls.calculate_default_amounts(
                            detail, src_agency.gain_percent, dst_agency.gain_percent)
                    )


    @classmethod
    def _copy_extras(cls, src_agency, dst_agency, is_update):
        # find agencyservice list
        src_agency_services = list(AgencyExtraService.objects.filter(agency=src_agency.id))
        # for each agencyservice create agencyservice
        for src_agency_service in src_agency_services:
            dst_agency_service, created = AgencyExtraService.objects.get_or_create(
                agency_id=dst_agency.id,
                date_from=src_agency_service.date_from,
                date_to=src_agency_service.date_to,
                service_id=src_agency_service.service_id
            )
            # find details
            details = list(
                AgencyExtraDetail.objects.filter(agency_service=src_agency_service))
            # for each src agency detail create dst agency detail
            for detail in details:
                if is_update:
                    # update - dont modify if exists
                    agency_detail, created = AgencyExtraDetail.objects.get_or_create(
                        agency_service_id=dst_agency_service.id,
                        addon_id=detail.addon_id,
                        pax_range_min=detail.pax_range_min,
                        pax_range_max=detail.pax_range_max,
                        defaults=cls.calculate_default_amounts(
                            detail, src_agency.gain_percent, dst_agency.gain_percent)
                    )
                else:
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
            cls, service_id, date_from, date_to, cost_groups, price_groups, provider, agency,
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
            provider, board_type, room_type_id, addon_id, quantity)

        # agency price
        price, price_message = cls.allotment_prices(
            service_id, date_from, date_to, price_groups,
            agency, board_type, room_type_id, addon_id, quantity)

        return cost, cost_message, price, price_message

    @classmethod
    def allotment_costs(
            cls, service_id, date_from, date_to, cost_groups, provider,
            board_type, room_type_id, addon_id=None, quantity=None):
        if room_type_id is None or room_type_id == '':
            return None, 'Room Missing'
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
            cost_message = 'Paxes Missing'
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
                        provider.id, service_id, date_from, date_to)
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
                        return None, "Cost Not Found"
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
                    provider.id, service_id, date_from, date_to)
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
                    return None, "Cost Not Found"
                cost, cost_message = cls.find_groups_amount(
                    True, service, date_from, date_to, cost_groups,
                    quantity, None, detail_list
                )
        return cost, cost_message


    @classmethod
    def allotment_prices(
            cls, service_id, date_from, date_to, price_groups, agency,
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
                        AgencyAllotmentDetail.objects,
                        agency.id, service_id, date_from, date_to)
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
                    agency.id, service_id, date_from, date_to)
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
            cls, service_id, date_from, date_to, cost_groups, price_groups, provider, agency,
            location_from_id, location_to_id, addon_id=None, quantity=None):
        if location_from_id is None or location_from_id == '':
            return None, 'Location From Missing', None, 'Location From Missing'
        if location_to_id is None or location_to_id == '':
            return None, 'Location To Missing', None, 'Location To Missing'
        if date_from is None and date_to is None:
            return None, 'Both Dates are Missing', None, 'Both Dates are Missing'
        if date_from is None:
            date_from = date_to
        if date_to is None:
            date_to = date_from

        # provider cost
        cost, cost_message = cls.transfer_costs(
            service_id, date_from, date_to, cost_groups,
            provider, location_from_id, location_to_id, addon_id, quantity)

        # agency price
        price, price_message = cls.transfer_prices(
            service_id, date_from, date_to, price_groups,
            agency, location_from_id, location_to_id, addon_id, quantity)

        return cost, cost_message, price, price_message


    @classmethod
    def transfer_costs(
            cls, service_id, date_from, date_to, cost_groups, provider,
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

        # provider cost
        # obtain details order by date_from asc, date_to desc
        service = Transfer.objects.get(pk=service_id)

        if (cost_groups is None or not cost_groups) and service.cost_type == AMOUNTS_BY_PAX:
            cost = None
            cost_message = 'Paxes Missing'
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
                        provider.id, service_id, date_from, date_to)
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
                            p_location_from_id=location_from_id,
                            p_location_to_id=location_to_id))
                    group_cost = None
                    if detail_list:
                        group_cost, group_cost_message = cls.find_groups_amount(
                            True, service, date_from, date_to, cost_groups,
                            quantity, None, detail_list
                        )
                    if group_cost is None:
                        detail_list = list(
                            queryset.filter(
                                p_location_to_id=location_from_id,
                                p_location_from_id=location_to_id))
                        if not detail_list:
                            return None, "Cost Not Found"
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
                    provider.id, service_id, date_from, date_to)
                # addon filtering
                if addon_id:
                    queryset = queryset.filter(addon_id=addon_id)
                else:
                    queryset = queryset.filter(addon_id=ADDON_FOR_NO_ADDON)
                detail_list = list(
                    queryset.filter(
                        p_location_from_id=location_from_id,
                        p_location_to_id=location_to_id))
                cost = None
                if detail_list:
                    cost, cost_message = cls.find_groups_amount(
                        True, service, date_from, date_to, cost_groups,
                        quantity, None, detail_list
                    )
                if cost is None:
                    detail_list = list(
                        queryset.filter(
                            p_location_to_id=location_from_id,
                            p_location_from_id=location_to_id))
                    if not detail_list:
                        return None, "Cost Not Found"
                    cost, cost_message = cls.find_groups_amount(
                        True, service, date_from, date_to, cost_groups,
                        quantity, None, detail_list
                    )
        return cost, cost_message


    @classmethod
    def transfer_prices(
            cls, service_id, date_from, date_to, price_groups, agency,
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
                        agency.id, service_id, date_from, date_to)
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
                            a_location_from_id=location_from_id,
                            a_location_to_id=location_to_id))
                    group_price = None
                    if detail_list:
                        group_price, group_price_message = cls.find_groups_amount(
                            False, service, date_from, date_to, price_groups,
                            quantity, None, detail_list
                        )
                    if group_price is None:
                        detail_list = list(
                            queryset.filter(
                                a_location_to_id=location_from_id,
                                a_location_from_id=location_to_id))
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
                    agency.id, service_id, date_from, date_to)
                # addon filtering
                if addon_id:
                    queryset = queryset.filter(addon_id=addon_id)
                else:
                    queryset = queryset.filter(addon_id=ADDON_FOR_NO_ADDON)
                detail_list = list(
                    queryset.filter(
                        a_location_from_id=location_from_id,
                        a_location_to_id=location_to_id))
                price = None
                if detail_list:
                    price, price_message = cls.find_groups_amount(
                        False, service, date_from, date_to, price_groups,
                        quantity, None, detail_list
                    )
                if price is None:
                    detail_list = list(
                        queryset.filter(
                            a_location_to_id=location_from_id,
                            a_location_from_id=location_to_id))
                    if not detail_list:
                        return None, "Price Not Found"
                    price, price_message = cls.find_groups_amount(
                        False, service, date_from, date_to, price_groups,
                        quantity, None, detail_list
                    )

        return price, price_message


    @classmethod
    def extra_amounts(
            cls, service_id, date_from, date_to, cost_groups, price_groups, provider, agency,
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
            provider, addon_id, quantity, parameter)

        # agency price
        price, price_message = cls.extra_prices(service_id, date_from, date_to, price_groups,
            agency, addon_id, quantity, parameter)

        return cost, cost_message, price, price_message


    @classmethod
    def extra_costs(
            cls, service_id, date_from, date_to, cost_groups, provider,
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
            cost_message = 'Paxes Missing'
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
                        provider.id, service_id, date_from, date_to)
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
                        return None, "Cost Not Found"
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
                    provider.id, service_id, date_from, date_to)
                # addon filtering
                if addon_id:
                    queryset = queryset.filter(addon_id=addon_id)
                else:
                    queryset = queryset.filter(addon_id=ADDON_FOR_NO_ADDON)

                detail_list = list(queryset)
                if not detail_list:
                    return None, "Cost Not Found"
                cost, cost_message = cls.find_groups_amount(
                    True, service, date_from, date_to, cost_groups,
                    quantity, parameter, detail_list
                )
        return cost, cost_message


    @classmethod
    def extra_prices(
            cls, service_id, date_from, date_to, price_groups, agency,
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
                    queryset = cls._get_agency_queryset(
                        AgencyExtraDetail.objects,
                        agency.id, service_id, date_from, date_to)
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
                    agency.id, service_id, date_from, date_to)
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
            groups_amount += amount
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
    def get_service_quantity(cls, service, pax_qtty):
        if not hasattr(service, 'max_capacity'):
            return 1
        if service.max_capacity is None or (service.max_capacity < 1):
            return 1
        return int((pax_qtty + service.max_capacity - 1) / service.max_capacity)

    @classmethod
    def _get_transfer_amount(
            cls, service, detail, adults, children, free_adults, free_children, quantity):
        quantity = cls.get_service_quantity(service, adults + children)
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
        if quantity is None or quantity < 1:
            quantity = cls.get_service_quantity(service, adults + children)
        if service.cost_type == AMOUNTS_FIXED and detail.ad_1_amount is not None:
            # TODO verificar si esto es correcto
            return (adults + children - free_adults - free_children) * detail.ad_1_amount * quantity * parameter / (adults + children)
        if service.cost_type == AMOUNTS_BY_PAX:
            amount = cls._find_amount(service, detail, adults, children, free_adults, free_children)
            if amount is not None and amount >= 0:
                return amount * quantity * parameter
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
            if children == 1 and detail.ch_1_ad_0_amount is not None:
                return (children - free_children) * detail.ch_1_ad_0_amount
            if children == 2 and detail.ch_2_ad_0_amount is not None:
                return (children - free_children) * detail.ch_2_ad_0_amount
            if children == 3 and detail.ch_3_ad_0_amount is not None:
                return (children - free_children) * detail.ch_3_ad_0_amount
        if adults == 1 and detail.ad_1_amount is not None:
            if children == 0:
                return (adults - free_adults) * detail.ad_1_amount
            if children == 1:
                if detail.ch_1_ad_1_amount is not None:
                    return (adults - free_adults) * detail.ad_1_amount + (children - free_children) * detail.ch_1_ad_1_amount
                elif  service.child_discount_percent is not None:
                    return (adults - free_adults) * float(detail.ad_1_amount) + (children - free_children) * float(detail.ad_1_amount) * (1.0 - float(service.child_discount_percent) / 100.0)
            elif children == 2:
                if detail.ch_2_ad_1_amount is not None:
                    return (adults - free_adults) * float(detail.ad_1_amount) + (children - free_children) * detail.ch_2_ad_1_amount
                elif  service.child_discount_percent is not None:
                    return (adults - free_adults) * float(detail.ad_1_amount) + (children - free_children) * float(detail.ad_1_amount) * (1.0 - float(service.child_discount_percent) / 100.0)
            elif children == 3:
                if detail.ch_3_ad_1_amount is not None:
                    return (adults - free_adults) * float(detail.ad_1_amount) + (children - free_children) * detail.ch_3_ad_1_amount
                elif  service.child_discount_percent is not None:
                    return (adults - free_adults) * detail.ad_1_amount + (children - free_children) * float(detail.ad_1_amount) * (1.0 - float(service.child_discount_percent) / 100.0)
        if adults == 2 and detail.ad_2_amount is not None:
            if children == 0:
                return (adults - free_adults) * detail.ad_2_amount
            if children == 1:
                if detail.ch_1_ad_2_amount is not None:
                    return (adults - free_adults) * detail.ad_2_amount + (children - free_children) * detail.ch_1_ad_2_amount
                elif  service.child_discount_percent is not None:
                    return (adults - free_adults) * detail.ad_2_amount + (children - free_children) * float(detail.ad_2_amount) * (1.0 - float(service.child_discount_percent) / 100.0)
            if children == 2:
                if detail.ch_2_ad_2_amount is not None:
                    return (adults - free_adults) * detail.ad_2_amount + (children - free_children) * detail.ch_2_ad_2_amount
                elif  service.child_discount_percent is not None:
                    return (adults - free_adults) * detail.ad_2_amount + (children - free_children) * float(detail.ad_2_amount) * (1.0 - float(service.child_discount_percent) / 100.0)
            if children == 3:
                if detail.ch_3_ad_2_amount is not None:
                    return (adults - free_adults) * detail.ad_2_amount + (children - free_children) * detail.ch_3_ad_2_amount
                elif  service.child_discount_percent is not None:
                    return (adults - free_adults) * detail.ad_2_amount + (children - free_children) * float(detail.ad_2_amount) * (1.0 - float(service.child_discount_percent) / 100.0)
        if adults == 3 and detail.ad_3_amount is not None:
            if children == 0:
                return (adults - free_adults) * detail.ad_3_amount
            if children == 1:
                if detail.ch_1_ad_3_amount is not None:
                    return (adults - free_adults) * detail.ad_3_amount + (children - free_children) * detail.ch_1_ad_3_amount
                elif  service.child_discount_percent is not None:
                    return (adults - free_adults) * detail.ad_3_amount + (children - free_children) * float(detail.ad_3_amount) * (1.0 - float(service.child_discount_percent) / 100.0)
            if children == 2:
                if detail.ch_2_ad_3_amount is not None:
                    return (adults - free_adults) * detail.ad_3_amount + (children - free_children) * detail.ch_2_ad_3_amount
                elif  service.child_discount_percent is not None:
                    return (adults - free_adults) * detail.ad_3_amount + (children - free_children) * float(detail.ad_3_amount) * (1.0 - float(service.child_discount_percent) / 100.0)
            if children == 3:
                if detail.ch_3_ad_3_amount is not None:
                    return (adults - free_adults) * detail.ad_3_amount + (children - free_children) * detail.ch_3_ad_3_amount
                elif  service.child_discount_percent is not None:
                    return (adults - free_adults) * detail.ad_3_amount + (children - free_children) * float(detail.ad_3_amount) * (1.0 - float(service.child_discount_percent) / 100.0)
        if adults == 4 and detail.ad_4_amount is not None:
            if children == 0:
                return (adults - free_adults) * detail.ad_4_amount
            if children == 1:
                if detail.ch_1_ad_4_amount is not None:
                    return (adults - free_adults) * detail.ad_4_amount + (children - free_children) * detail.ch_1_ad_4_amount
                elif  service.child_discount_percent is not None:
                    return (adults - free_adults) * detail.ad_4_amount + (children - free_children) * float(detail.ad_4_amount) * (1.0 - float(service.child_discount_percent) / 100.0)
            if children == 2:
                if detail.ch_2_ad_4_amount is not None:
                    return (adults - free_adults) * detail.ad_4_amount + (children - free_children) * detail.ch_2_ad_4_amount
                elif  service.child_discount_percent is not None:
                    return (adults - free_adults) * detail.ad_4_amount + (children - free_children) * float(detail.ad_4_amount) * (1.0 - float(service.child_discount_percent) / 100.0)
            if children == 3:
                if detail.ch_3_ad_4_amount is not None:
                    return (adults - free_adults) * detail.ad_4_amount + (children - free_children) * detail.ch_3_ad_4_amount
                elif  service.child_discount_percent is not None:
                    return (adults - free_adults) * detail.ad_4_amount + (children - free_children) * float(detail.ad_4_amount) * (1.0 - float(service.child_discount_percent) / 100.0)
        return None

    @classmethod
    def _get_provider_queryset(
            cls, manager, provider_id, service_id, date_from, date_to):
        return manager.select_related(
            'provider_service__service'
            ).filter(
                provider_service__provider_id=provider_id
            ).filter(
                provider_service__service_id=service_id
            ).filter(
                provider_service__date_to__gte=date_from,
                provider_service__date_from__lte=date_to
            ).order_by(
                'provider_service__date_from', '-provider_service__date_to'
            )

    @classmethod
    def _get_agency_queryset(
            cls, manager, agency_id, service_id, date_from, date_to):
        if date_from is None:
            return manager.none()
        if date_to is None:
            return manager.none()
        return manager.select_related(
            'agency_service__service'
            ).filter(
                agency_service__agency_id=agency_id
            ).filter(
                agency_service__service_id=service_id
            ).filter(
                agency_service__date_to__gte=date_from,
                agency_service__date_from__lte=date_to
            ).order_by(
                'agency_service__date_from', '-agency_service__date_to'
            )


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
            service_id=src_provider_service.service_id
        )
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
            service_id=src_provider_service.service_id
        )
        # find details
        details = list(
            ProviderTransferDetail.objects.filter(provider_service=src_provider_service))
        # for each src provider detail create dst agency detail
        for detail in details:
            if is_update:
                # update - dont modify if exists
                agency_detail, created = AgencyTransferDetail.objects.get_or_create(
                    agency_service_id=dst_agency_service.id,
                    a_location_from_id=detail.p_location_from_id,
                    a_location_to_id=detail.p_location_to_id,
                    addon_id=detail.addon_id,
                    pax_range_min=detail.pax_range_min,
                    pax_range_max=detail.pax_range_max,
                    defaults=cls.calculate_default_amounts(
                        detail, 0, dst_agency.gain_percent)
                )
            else:
                # rewrite - modify if exists
                agency_detail, created = AgencyTransferDetail.objects.update_or_create(
                    agency_service_id=dst_agency_service.id,
                    a_location_from_id=detail.p_location_from_id,
                    a_location_to_id=detail.p_location_to_id,
                    addon_id=detail.addon_id,
                    pax_range_min=detail.pax_range_min,
                    pax_range_max=detail.pax_range_max,
                    defaults=cls.calculate_default_amounts(
                        detail, 0, dst_agency.gain_percent)
                )


    @classmethod
    def generate_agency_extra_amounts_from_provider_extra(cls, src_provider_service, dst_agency, is_update):
        dst_agency_service, created = AgencyExtraService.objects.get_or_create(
            agency_id=dst_agency.id,
            date_from=src_provider_service.date_from,
            date_to=src_provider_service.date_to,
            service_id=src_provider_service.service_id
        )
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
    def update_detail_amount(cls, detail_amount, percent, amount):
        if percent is Nane and amount is None:
            return detail_amount
        if detail_amount is None:
            return None
        result = float(detail_amount)
        if percent is not None:
            result += result * float(percent) / 100.0
        if amount is not None:
            result += float(amount)
        return round(0.499999 + result)


    @classmethod
    def next_year_price(cls, manager, agency_service, percent, amount):
        details = list(manager.filter(agency_service=agency_service.id))
        new_agency_service = agency_service
        new_agency_service.pk = None
        new_agency_service.id = None
        one_year = timedelta(years=1)
        if new_agency_service.date_from:
            new_agency_service.date_from = new_agency_service.date_from + one_year
        if new_agency_service.date_to:
            new_agency_service.date_to = new_agency_service.date_to + one_year
        new_agency_service.save()
        for detail in details:
            new_detail = detail
            new_detail.pk = None
            new_detail.id = None

            ad_1_amount = cls.update_detail_amount(ad_1_amount, percent, amount)
            ad_2_amount = cls.update_detail_amount(ad_2_amount, percent, amount)
            ad_3_amount = cls.update_detail_amount(ad_3_amount, percent, amount)
            ad_4_amount = cls.update_detail_amount(ad_4_amount, percent, amount)
            ch_1_ad_0_amount = cls.update_detail_amount(ch_1_ad_0_amount, percent, amount)
            ch_1_ad_1_amount = cls.update_detail_amount(ch_1_ad_1_amount, percent, amount)
            ch_1_ad_2_amount = cls.update_detail_amount(ch_1_ad_2_amount, percent, amount)
            ch_1_ad_3_amount = cls.update_detail_amount(ch_1_ad_3_amount, percent, amount)
            ch_1_ad_4_amount = cls.update_detail_amount(ch_1_ad_4_amount, percent, amount)
            ch_2_ad_0_amount = cls.update_detail_amount(ch_2_ad_0_amount, percent, amount)
            ch_2_ad_1_amount = cls.update_detail_amount(ch_2_ad_1_amount, percent, amount)
            ch_2_ad_2_amount = cls.update_detail_amount(ch_2_ad_2_amount, percent, amount)
            ch_2_ad_3_amount = cls.update_detail_amount(ch_2_ad_3_amount, percent, amount)
            ch_2_ad_4_amount = cls.update_detail_amount(ch_2_ad_4_amount, percent, amount)
            ch_3_ad_0_amount = cls.update_detail_amount(ch_3_ad_0_amount, percent, amount)
            ch_3_ad_1_amount = cls.update_detail_amount(ch_3_ad_1_amount, percent, amount)
            ch_3_ad_2_amount = cls.update_detail_amount(ch_3_ad_2_amount, percent, amount)
            ch_3_ad_3_amount = cls.update_detail_amount(ch_3_ad_3_amount, percent, amount)
            ch_3_ad_4_amount = cls.update_detail_amount(ch_3_ad_4_amount, percent, amount)

            new_detail.agency_service = new_agency_service
            new_detail.save()


    @classmethod
    def next_year_allotment_prices(cls, agency_service_ids, percent=None, amount=None):
        for agency_service_id in agency_service_ids:
            try:
                agency_service = AgencyAllotmentService.objects.get(agency_service_id)
                cls.next_year_price(AgencyAllotmentDetail.objects, agency_service, percent, amount)
            except Error as ex:
                print('EXCEPTION config services - next_year_allotment_prices : ' + ex.__str__())


    @classmethod
    def next_year_transfer_prices(cls, agency_service_ids, percent=None, amount=None):
        for agency_service_id in agency_service_ids:
            try:
                agency_service = AgencyTransferService.objects.get(agency_service_id)
                cls.next_year_price(AgencyTransferDetail.objects, agency_service, percent, amount)
            except Error as ex:
                print('EXCEPTION config services - next_year_transfer_prices : ' + ex.__str__())


    @classmethod
    def next_year_extra_prices(cls, agency_service_ids, percent=None, amount=None):
        for agency_service_id in agency_service_ids:
            try:
                agency_service = AgencyExtraService.objects.get(agency_service_id)
                cls.next_year_price(AgencyExtraDetail.objects, agency_service, percent, amount)
            except Error as ex:
                print('EXCEPTION config services - next_year_extra_prices : ' + ex.__str__())


    @classmethod
    def list_allotment_details(cls, allotment, agency, date_from, date_to):
        qs = AgencyAllotmentDetail.objects.all()
        qs = qs.filter(
            agency_service__agency=agency,
            agency_service__service=allotment.id)
        if date_from:
            qs = qs.filter(agency_service__date_to__gte=date_from)
        if date_to:
            qs = qs.filter(agency_service__date_from__lte=date_to)
        qs = qs.order_by(
            'board_type', 'room_type', 'addon', 'pax_range_min', '-pax_range_max',
            'agency_service__date_from', '-agency_service__date_to')
        return list(qs)


    @classmethod
    def list_transfer_details(cls, transfer, agency, date_from, date_to):
        qs = AgencyTransferDetail.objects.all()
        qs = qs.filter(
            agency_service__agency=agency,
            agency_service__service=transfer.id)
        if date_from:
            qs = qs.filter(agency_service__date_to__gte=date_from)
        if date_to:
            qs = qs.filter(agency_service__date_from__lte=date_to)
        qs = qs.order_by(
            'a_location_from', 'a_location_to', 'addon', 'pax_range_min', '-pax_range_max',
            'agency_service__date_from', '-agency_service__date_to')
        return list(qs)


    @classmethod
    def list_extra_details(cls, extra, agency, date_from, date_to):
        qs = AgencyExtraDetail.objects.all()
        qs = qs.filter(
            agency_service__agency=agency,
            agency_service__service=extra.id)
        if date_from:
            qs = qs.filter(agency_service__date_to__gte=date_from)
        if date_to:
            qs = qs.filter(agency_service__date_from__lte=date_to)
        qs = qs.order_by(
            'addon', 'pax_range_min', '-pax_range_max',
            'agency_service__date_from', '-agency_service__date_to')
        return list(qs)


    @classmethod
    def list_service_prices(cls, service, agency, date_from, date_to):
        if service.category == 'A':
            return cls.list_allotment_details(service, agency, date_from, date_to)
        if service.category == 'T':
            return cls.list_transfer_details(service, agency, date_from, date_to)
        if service.category == 'E':
            return cls.list_extra_details(service, agency, date_from, date_to)
        if service.category == 'P':
            from booking.services import BookingServices
            return BookingServices.list_package_details(service, agency, date_from, date_to)
