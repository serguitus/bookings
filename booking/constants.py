from config.constants import (SERVICE_CATEGORY_EXTRA,
                              SERVICE_CATEGORY_ALLOTMENT,
                              SERVICE_CATEGORY_TRANSFER)

SERVICE_CATEGORY_PACKAGE = 'P'
SERVICE_CATEGORIES = (
    (SERVICE_CATEGORY_ALLOTMENT, 'Allotment'),
    (SERVICE_CATEGORY_TRANSFER, 'Transfer'),
    (SERVICE_CATEGORY_EXTRA, 'Extra'),
    (SERVICE_CATEGORY_PACKAGE, 'Package'),
)

QUOTE_STATUS_DRAFT = 'DR'
QUOTE_STATUS_READY = 'RD'
QUOTE_STATUS_LIST = (
    (QUOTE_STATUS_DRAFT, 'Draft'),
    (QUOTE_STATUS_READY, 'Ready'),
)

BOOKING_STATUS_PENDING = 'PD'
BOOKING_STATUS_REQUEST = 'RQ'
BOOKING_STATUS_CONFIRMED = 'OK'
BOOKING_STATUS_COORDINATED = 'CD'
BOOKING_STATUS_CANCELLED = 'CN'
BOOKING_STATUS_LIST = (
    (BOOKING_STATUS_PENDING, 'Pending'),
    (BOOKING_STATUS_REQUEST, 'Requested'),
    (BOOKING_STATUS_CONFIRMED, 'Confirmed'),
    (BOOKING_STATUS_COORDINATED, 'Coordinated'),
    (BOOKING_STATUS_CANCELLED, 'Cancelled'),
)

SERVICE_STATUS_PENDING = 'PD'
SERVICE_STATUS_REQUEST = 'RQ'
SERVICE_STATUS_PHONE_CONFIRMED = 'PH'
SERVICE_STATUS_CONFIRMED = 'OK'
SERVICE_STATUS_COORDINATED = 'CD'
SERVICE_STATUS_CANCELLED = 'CN'
SERVICE_STATUS_LIST = (
    (SERVICE_STATUS_PENDING, 'Pending'),
    (SERVICE_STATUS_REQUEST, 'Requested'),
    (SERVICE_STATUS_PHONE_CONFIRMED, 'Phone Confirmed'),
    (SERVICE_STATUS_CONFIRMED, 'Confirmed'),
    (SERVICE_STATUS_COORDINATED, 'Coordinated'),
    (SERVICE_STATUS_CANCELLED, 'Cancelled'),
)

PACKAGESERVICE_TYPES = {
    SERVICE_CATEGORY_ALLOTMENT: 'packageallotment',
    SERVICE_CATEGORY_TRANSFER: 'packagetransfer',
    SERVICE_CATEGORY_EXTRA: 'packageextra',
}

QUOTESERVICE_TYPES = {
    SERVICE_CATEGORY_ALLOTMENT: 'quoteallotment',
    SERVICE_CATEGORY_TRANSFER: 'quotetransfer',
    SERVICE_CATEGORY_EXTRA: 'quoteextra',
    SERVICE_CATEGORY_PACKAGE: 'quotepackage',
}

QUOTEPACKAGESERVICE_TYPES = {
    SERVICE_CATEGORY_ALLOTMENT: 'quotepackageallotment',
    SERVICE_CATEGORY_TRANSFER: 'quotepackagetransfer',
    SERVICE_CATEGORY_EXTRA: 'quotepackageextra',
}

BOOKINGSERVICE_TYPES = {
    SERVICE_CATEGORY_ALLOTMENT: 'bookingallotment',
    SERVICE_CATEGORY_TRANSFER: 'bookingtransfer',
    SERVICE_CATEGORY_EXTRA: 'bookingextra',
    SERVICE_CATEGORY_PACKAGE: 'bookingpackage',
}

BOOKINGPACKAGESERVICE_TYPES = {
    SERVICE_CATEGORY_ALLOTMENT: 'bookingpackageallotment',
    SERVICE_CATEGORY_TRANSFER: 'bookingpackagetransfer',
    SERVICE_CATEGORY_EXTRA: 'bookingpackageextra',
}

ACTIONS = {
    'vouchers': 'BookingSiteModel.config_vouchers',
}

PACKAGE_AMOUNTS_FIXED = 'F'
PACKAGE_AMOUNTS_BY_PAX = 'P'
PACKAGE_AMOUNTS_TYPES = (
    (PACKAGE_AMOUNTS_FIXED, 'Fixed'),
    (PACKAGE_AMOUNTS_BY_PAX, 'By Pax'),
)
