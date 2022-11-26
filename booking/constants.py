from config.constants import (
    AMOUNTS_FIXED, AMOUNTS_BY_PAX,
    SERVICE_CATEGORY_EXTRA, SERVICE_CATEGORY_ALLOTMENT, SERVICE_CATEGORY_TRANSFER)


BASE_BOOKING_SERVICE_CATEGORY_BOOKING_ALLOTMENT = 'BA'
BASE_BOOKING_SERVICE_CATEGORY_BOOKING_TRANSFER = 'BT'
BASE_BOOKING_SERVICE_CATEGORY_BOOKING_EXTRA = 'BE'
BASE_BOOKING_SERVICE_CATEGORY_BOOKING_PACKAGE = 'BP'
BASE_BOOKING_SERVICE_CATEGORY_BOOKING_PACKAGE_ALLOTMENT = 'PA'
BASE_BOOKING_SERVICE_CATEGORY_BOOKING_PACKAGE_TRANSFER = 'PT'
BASE_BOOKING_SERVICE_CATEGORY_BOOKING_PACKAGE_EXTRA = 'PE'
BASE_BOOKING_SERVICE_CATEGORY_BOOKING_DETAIL_ALLOTMENT = 'DA'
BASE_BOOKING_SERVICE_CATEGORY_BOOKING_DETAIL_TRANSFER = 'DT'
BASE_BOOKING_SERVICE_CATEGORY_BOOKING_DETAIL_EXTRA = 'DE'

BASE_BOOKING_SERVICE_CATEGORIES = (
    (BASE_BOOKING_SERVICE_CATEGORY_BOOKING_ALLOTMENT, 'Booking Allotment'),
    (BASE_BOOKING_SERVICE_CATEGORY_BOOKING_TRANSFER, 'Booking Transfer'),
    (BASE_BOOKING_SERVICE_CATEGORY_BOOKING_EXTRA, 'Booking Extra'),
    (BASE_BOOKING_SERVICE_CATEGORY_BOOKING_PACKAGE, 'Booking Package'),
    (BASE_BOOKING_SERVICE_CATEGORY_BOOKING_PACKAGE_ALLOTMENT, 'Booking Package Allotment'),
    (BASE_BOOKING_SERVICE_CATEGORY_BOOKING_PACKAGE_TRANSFER, 'Booking Package Transfer'),
    (BASE_BOOKING_SERVICE_CATEGORY_BOOKING_PACKAGE_EXTRA, 'Booking Package Extra'),
    (BASE_BOOKING_SERVICE_CATEGORY_BOOKING_DETAIL_ALLOTMENT, 'Booking Detail Allotment'),
    (BASE_BOOKING_SERVICE_CATEGORY_BOOKING_DETAIL_TRANSFER, 'Booking Detail Transfer'),
    (BASE_BOOKING_SERVICE_CATEGORY_BOOKING_DETAIL_EXTRA, 'Booking Detail Extra'),
)

BOOKINGSERVICE_TYPES = {
    BASE_BOOKING_SERVICE_CATEGORY_BOOKING_ALLOTMENT: 'bookingprovidedallotment',
    BASE_BOOKING_SERVICE_CATEGORY_BOOKING_TRANSFER: 'bookingprovidedtransfer',
    BASE_BOOKING_SERVICE_CATEGORY_BOOKING_EXTRA: 'bookingprovidedextra',
    BASE_BOOKING_SERVICE_CATEGORY_BOOKING_PACKAGE: 'bookingextrapackage',
    BASE_BOOKING_SERVICE_CATEGORY_BOOKING_PACKAGE_ALLOTMENT: 'bookingprovidedallotment',
    BASE_BOOKING_SERVICE_CATEGORY_BOOKING_PACKAGE_TRANSFER: 'bookingprovidedtransfer',
    BASE_BOOKING_SERVICE_CATEGORY_BOOKING_PACKAGE_EXTRA: 'bookingprovidedextra',
    BASE_BOOKING_SERVICE_CATEGORY_BOOKING_DETAIL_ALLOTMENT: 'bookingbookdetailallotment',
    BASE_BOOKING_SERVICE_CATEGORY_BOOKING_DETAIL_TRANSFER: 'bookingbookdetailtransfer',
    BASE_BOOKING_SERVICE_CATEGORY_BOOKING_DETAIL_EXTRA: 'bookingbookdetailextra',
}

QUOTE_STATUS_DRAFT = 'DR'
QUOTE_STATUS_READY = 'RD'
QUOTE_STATUS_LIST = (
    (QUOTE_STATUS_DRAFT, 'Draft'),
    (QUOTE_STATUS_READY, 'Ready'),
)

BOOKING_STATUS_PENDING = 'PD'
BOOKING_STATUS_REQUEST = 'RQ'
BOOKING_STATUS_ON_HOLD = 'OH'
BOOKING_STATUS_CONFIRMED = 'OK'
BOOKING_STATUS_COORDINATED = 'CD'
BOOKING_STATUS_NOSHOW = 'NS'
BOOKING_STATUS_CANCELLED = 'CN'
BOOKING_STATUS_LIST = (
    (BOOKING_STATUS_PENDING, 'Pending'),
    (BOOKING_STATUS_REQUEST, 'Requested'),
    (BOOKING_STATUS_ON_HOLD, 'On Hold'),
    (BOOKING_STATUS_CONFIRMED, 'Confirmed'),
    (BOOKING_STATUS_COORDINATED, 'Coordinated'),
    (BOOKING_STATUS_NOSHOW, 'No Show'),
    (BOOKING_STATUS_CANCELLED, 'Cancelled'),
)

BOOKING_STATUS_ORDER = [
    BOOKING_STATUS_CANCELLED,  # index 0
    BOOKING_STATUS_PENDING,  # index 1 ....
    BOOKING_STATUS_REQUEST,
    BOOKING_STATUS_ON_HOLD,
    BOOKING_STATUS_CONFIRMED,
    BOOKING_STATUS_COORDINATED,
    BOOKING_STATUS_NOSHOW,  # index 6
]

SERVICE_STATUS_PENDING = 'PD'
SERVICE_STATUS_REQUEST = 'RQ'
SERVICE_STATUS_PHONE_CONFIRMED = 'PH'
SERVICE_STATUS_ON_HOLD = 'OH'
SERVICE_STATUS_CONFIRMED = 'OK'
SERVICE_STATUS_COORDINATED = 'CD'
SERVICE_STATUS_NOSHOW = 'NS'
SERVICE_STATUS_CANCELLING = 'CR'
SERVICE_STATUS_CANCELLED = 'CN'
SERVICE_STATUS_LIST = (
    (SERVICE_STATUS_PENDING, 'Pending'),
    (SERVICE_STATUS_REQUEST, 'Requested'),
    (SERVICE_STATUS_PHONE_CONFIRMED, 'Phone Confirmed'),
    (SERVICE_STATUS_ON_HOLD, 'On Hold'),
    (SERVICE_STATUS_CONFIRMED, 'Confirmed'),
    (SERVICE_STATUS_COORDINATED, 'Coordinated'),
    (SERVICE_STATUS_NOSHOW, 'No Show'),
    (SERVICE_STATUS_CANCELLING, 'Cancellation Requested'),
    (SERVICE_STATUS_CANCELLED, 'Cancelled'),
)

SERVICE_STATUS_ORDER = [
    SERVICE_STATUS_PENDING,  # index 0
    SERVICE_STATUS_REQUEST,
    SERVICE_STATUS_PHONE_CONFIRMED,
    SERVICE_STATUS_ON_HOLD,
    SERVICE_STATUS_CONFIRMED,
    SERVICE_STATUS_COORDINATED,
    SERVICE_STATUS_NOSHOW,
    SERVICE_STATUS_CANCELLING,
    SERVICE_STATUS_CANCELLED,
]

BOOTSTRAP_STYLE_QUOTE_STATUS_MAPPING = {
    QUOTE_STATUS_DRAFT: '',
    QUOTE_STATUS_READY: 'success',
}

BOOTSTRAP_STYLE_BOOKING_STATUS_MAPPING = {
    BOOKING_STATUS_PENDING: 'table-danger',
    BOOKING_STATUS_REQUEST: 'table-warning',
    BOOKING_STATUS_ON_HOLD: 'table-primary',
    BOOKING_STATUS_CONFIRMED: '',
    BOOKING_STATUS_COORDINATED: 'table-success',
    BOOKING_STATUS_NOSHOW: '',
    BOOKING_STATUS_CANCELLED: 'table-active',
}

BOOTSTRAP_STYLE_BOOKING_SERVICE_STATUS_MAPPING = {
    SERVICE_STATUS_PENDING: 'table-danger',
    SERVICE_STATUS_REQUEST: 'table-warning',
    SERVICE_STATUS_PHONE_CONFIRMED: '',
    SERVICE_STATUS_ON_HOLD: 'table-primary',
    SERVICE_STATUS_CONFIRMED: '',
    SERVICE_STATUS_COORDINATED: 'table-success',
    SERVICE_STATUS_NOSHOW: '',
    SERVICE_STATUS_CANCELLING: 'table-danger',
    SERVICE_STATUS_CANCELLED: 'table-active',
}

QUOTE_SERVICE_CATEGORY_QUOTE_ALLOTMENT = 'QA'
QUOTE_SERVICE_CATEGORY_QUOTE_TRANSFER = 'QT'
QUOTE_SERVICE_CATEGORY_QUOTE_EXTRA = 'QE'
QUOTE_SERVICE_CATEGORY_QUOTE_PACKAGE = 'QP'
QUOTE_SERVICE_CATEGORY_QUOTE_PACKAGE_ALLOTMENT = 'PA'
QUOTE_SERVICE_CATEGORY_QUOTE_PACKAGE_TRANSFER = 'PT'
QUOTE_SERVICE_CATEGORY_QUOTE_PACKAGE_EXTRA = 'PE'
QUOTE_SERVICE_CATEGORY_QUOTE_DETAIL_ALLOTMENT = 'DA'
QUOTE_SERVICE_CATEGORY_QUOTE_DETAIL_TRANSFER = 'DT'
QUOTE_SERVICE_CATEGORY_QUOTE_DETAIL_EXTRA = 'DE'

QUOTE_SERVICE_CATEGORIES = (
    (QUOTE_SERVICE_CATEGORY_QUOTE_ALLOTMENT, 'Quote Allotment'),
    (QUOTE_SERVICE_CATEGORY_QUOTE_TRANSFER, 'Quote Transfer'),
    (QUOTE_SERVICE_CATEGORY_QUOTE_EXTRA, 'Quote Extra'),
    (QUOTE_SERVICE_CATEGORY_QUOTE_PACKAGE, 'Quote Package'),
    (QUOTE_SERVICE_CATEGORY_QUOTE_PACKAGE_ALLOTMENT, 'Quote Package Allotment'),
    (QUOTE_SERVICE_CATEGORY_QUOTE_PACKAGE_TRANSFER, 'Quote Package Transfer'),
    (QUOTE_SERVICE_CATEGORY_QUOTE_PACKAGE_EXTRA, 'Quote Package Extra'),
    (QUOTE_SERVICE_CATEGORY_QUOTE_DETAIL_ALLOTMENT, 'Quote Detail Allotment'),
    (QUOTE_SERVICE_CATEGORY_QUOTE_DETAIL_TRANSFER, 'Quote Detail Transfer'),
    (QUOTE_SERVICE_CATEGORY_QUOTE_DETAIL_EXTRA, 'Quote Detail Extra'),
)

QUOTESERVICE_TYPES = {
    QUOTE_SERVICE_CATEGORY_QUOTE_ALLOTMENT: 'newquoteallotment',
    QUOTE_SERVICE_CATEGORY_QUOTE_TRANSFER: 'newquotetransfer',
    QUOTE_SERVICE_CATEGORY_QUOTE_EXTRA: 'newquoteextra',
    QUOTE_SERVICE_CATEGORY_QUOTE_PACKAGE: 'quoteextrapackage',
    QUOTE_SERVICE_CATEGORY_QUOTE_PACKAGE_ALLOTMENT: 'newquoteallotment',
    QUOTE_SERVICE_CATEGORY_QUOTE_PACKAGE_TRANSFER: 'newquotetransfer',
    QUOTE_SERVICE_CATEGORY_QUOTE_PACKAGE_EXTRA: 'newquoteextra',
    QUOTE_SERVICE_CATEGORY_QUOTE_DETAIL_ALLOTMENT: 'newquoteservicebookdetailallotment',
    QUOTE_SERVICE_CATEGORY_QUOTE_DETAIL_TRANSFER: 'newquoteservicebookdetailtransfer',
    QUOTE_SERVICE_CATEGORY_QUOTE_DETAIL_EXTRA: 'newquoteservicebookdetailextra',
}

ACTIONS = {
    'vouchers': 'BookingSiteModel.config_vouchers',
}

INVOICE_FORMAT_COMPACT = 'C'
INVOICE_FORMAT_SERVICES = 'S'
INVOICE_FORMAT_DETAILS = 'D'
INVOICE_FORMATS = (
    (INVOICE_FORMAT_COMPACT, 'Compact'),
    (INVOICE_FORMAT_SERVICES, 'Services'),
    (INVOICE_FORMAT_DETAILS, 'Details'),
)

QUOTE_BOOK_DETAIL_CATEGORIES = {
    SERVICE_CATEGORY_ALLOTMENT: 'newquoteservicebookdetailallotment',
    SERVICE_CATEGORY_TRANSFER: 'newquoteservicebookdetailtransfer',
    SERVICE_CATEGORY_EXTRA: 'newquoteservicebookdetailextra',
}
