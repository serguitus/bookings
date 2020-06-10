"""
Config Constants
"""

SERVICE_CATEGORY_EXTRA = 'E'
SERVICE_CATEGORY_ALLOTMENT = 'A'
SERVICE_CATEGORY_TRANSFER = 'T'
SERVICE_CATEGORIES = (
    (SERVICE_CATEGORY_EXTRA, 'Extra'),
    (SERVICE_CATEGORY_ALLOTMENT, 'Allotment'),
    (SERVICE_CATEGORY_TRANSFER, 'Transfer'),
)

BOOK_DETAIL_CATEGORIES = {
    SERVICE_CATEGORY_ALLOTMENT: 'servicebookdetailallotment',
    SERVICE_CATEGORY_TRANSFER: 'servicebookdetailtransfer',
    SERVICE_CATEGORY_EXTRA: 'servicebookdetailextra',
}

AMOUNTS_FIXED = 'F'
AMOUNTS_BY_PAX = 'P'
AMOUNTS_BY_DAY = 'D'
AMOUNTS_BY_PAX_DAY = 'PD'
AMOUNTS_BY_HOURS = 'H'

PACKAGE_AMOUNTS_TYPES = (
    (AMOUNTS_FIXED, 'Fixed'),
    (AMOUNTS_BY_PAX, 'By Pax'),
)

ALLOTMENT_AMOUNTS_TYPES = (
    (AMOUNTS_FIXED, 'Fixed'),
    (AMOUNTS_BY_PAX, 'By Pax'),
)

TRANSFER_AMOUNTS_TYPES = (
    (AMOUNTS_FIXED, 'Fixed'),
    (AMOUNTS_BY_PAX, 'By Pax'),
)

EXTRA_AMOUNTS_TYPES = (
    (AMOUNTS_FIXED, 'Fixed'),
    (AMOUNTS_BY_PAX, 'By Pax'),
)

EXTRA_PARAMETER_TYPE_HOURS = 'H'
EXTRA_PARAMETER_TYPE_DAYS = 'D'
EXTRA_PARAMETER_TYPE_NIGHTS = 'N'
EXTRA_PARAMETER_TYPE_STAY = 'S'
EXTRA_PARAMETER_TYPES = (
    (EXTRA_PARAMETER_TYPE_HOURS, 'Hours'),
    (EXTRA_PARAMETER_TYPE_DAYS, 'Days'),
    (EXTRA_PARAMETER_TYPE_NIGHTS, 'Nights'),
    (EXTRA_PARAMETER_TYPE_STAY, 'Stay'),
)

ROOM_CAPACITY_SINGLE = '1'
ROOM_CAPACITY_DOUBLE = '2'
ROOM_CAPACITY_TRIPLE = '3'
ROOM_CAPACITY_QDRPLE = '4'
ROOM_CAPACITY_MLTPLE = '5'
ROOM_CAPACITIES = (
    (ROOM_CAPACITY_SINGLE, 'SGL'),
    (ROOM_CAPACITY_DOUBLE, 'DBL'),
    (ROOM_CAPACITY_TRIPLE, 'TPL'),
    (ROOM_CAPACITY_QDRPLE, 'QPL'),
    (ROOM_CAPACITY_MLTPLE, 'MPL'),
)

BOARD_TYPE_NB = 'NB'
BOARD_TYPE_BB = 'BB'
BOARD_TYPE_HB = 'HB'
BOARD_TYPE_FB = 'FB'
BOARD_TYPE_AI = 'AI'
BOARD_TYPES = (
    (BOARD_TYPE_NB, 'No Board'),
    (BOARD_TYPE_BB, 'Breakfast Board'),
    (BOARD_TYPE_HB, 'Half Board'),
    (BOARD_TYPE_FB, 'Full Board'),
    (BOARD_TYPE_AI, 'All Included'),
)

PAX_TYPE_CHILD = 'C'
PAX_TYPE_ADULT = 'A'
PAX_TYPES = (
    (PAX_TYPE_CHILD, 'Child'),
    (PAX_TYPE_ADULT, 'Adult'),
)

ERROR_INVALID_SERVICE_CATEGORY = 'Invalid Service Category %s'
ERROR_NO_EXTRA_COST_FOUND = 'Cost Not Found for Service %s - Provider %s - Date %s'
