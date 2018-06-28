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

EXTRA_COST_TYPE_BY_PAX = 'P'
EXTRA_COST_TYPE_BY_EXTRA = 'E'
EXTRA_COST_TYPE_BY_PAX_EXTRA = 'PE'
EXTRA_COST_TYPES = (
    (EXTRA_COST_TYPE_BY_PAX, 'By Paxes'),
    (EXTRA_COST_TYPE_BY_EXTRA, 'By Extras'),
    (EXTRA_COST_TYPE_BY_PAX_EXTRA, 'By Paxes Extras'),
)

TRANSFER_COST_TYPE_FIXED = 'F'
TRANSFER_COST_TYPE_BY_PAX = 'P'
TRANSFER_COST_TYPE_BY_TRANSPORT = 'T'
TRANSFER_COST_TYPES = (
    (TRANSFER_COST_TYPE_FIXED, 'Fixed'),
    (TRANSFER_COST_TYPE_BY_PAX, 'By Pax'),
    (TRANSFER_COST_TYPE_BY_TRANSPORT, 'By Transport'),
)

TRANSPORT_SUPPLEMENT_COST_TYPE_FIXED = 'F'
TRANSPORT_SUPPLEMENT_COST_TYPE_BY_PAX = 'H'
TRANSPORT_SUPPLEMENT_COST_TYPE_BY_TRANSPORT = 'T'
TRANSPORT_SUPPLEMENT_COST_TYPE_BY_HOUR = 'H'
TRANSPORT_SUPPLEMENT_COST_TYPE_BY_PAX_HOUR = 'PH'
TRANSPORT_SUPPLEMENT_COST_TYPE_BY_TRANSPORT_HOUR = 'TH'
TRANSPORT_SUPPLEMENT_COST_TYPES = (
    (TRANSPORT_SUPPLEMENT_COST_TYPE_FIXED, 'Fixed'),
    (TRANSPORT_SUPPLEMENT_COST_TYPE_BY_HOUR, 'By Hours'),
    (TRANSPORT_SUPPLEMENT_COST_TYPE_BY_TRANSPORT, 'By Paxes'),
    (TRANSPORT_SUPPLEMENT_COST_TYPE_BY_TRANSPORT, 'By Transports'),
    (TRANSPORT_SUPPLEMENT_COST_TYPE_BY_TRANSPORT, 'By Paxes Hours'),
    (TRANSPORT_SUPPLEMENT_COST_TYPE_BY_TRANSPORT, 'By Transports Hours'),
)

ALLOTMENT_SUPPLEMENT_COST_TYPE_FIXED = 'F'
ALLOTMENT_SUPPLEMENT_COST_TYPE_BYPAXES = 'P'
ALLOTMENT_SUPPLEMENT_COST_TYPE_BYDAYS = 'D'
ALLOTMENT_SUPPLEMENT_COST_TYPE_BYPAXESDAYS = 'PD'
ALLOTMENT_SUPPLEMENT_COST_TYPES = (
    (ALLOTMENT_SUPPLEMENT_COST_TYPE_FIXED, 'Fixed'),
    (ALLOTMENT_SUPPLEMENT_COST_TYPE_BYPAXES, 'By Paxes'),
    (ALLOTMENT_SUPPLEMENT_COST_TYPE_BYDAYS, 'By Days'),
    (ALLOTMENT_SUPPLEMENT_COST_TYPE_BYPAXESDAYS, 'By Paxes Days'),
)

TRANSFER_SUPPLEMENT_COST_TYPE_FIXED = 'F'
TRANSFER_SUPPLEMENT_COST_TYPE_BYTRANSPORTS = 'T'
TRANSFER_SUPPLEMENT_COST_TYPE_BYHOURS = 'H'
TRANSFER_SUPPLEMENT_COST_TYPE_BYTRANSPORTSHOURS = 'TH'
TRANSFER_SUPPLEMENT_COST_TYPES = (
    (TRANSFER_SUPPLEMENT_COST_TYPE_FIXED, 'Fixed'),
    (TRANSFER_SUPPLEMENT_COST_TYPE_BYTRANSPORTS, 'By Transports'),
    (TRANSFER_SUPPLEMENT_COST_TYPE_BYHOURS, 'By Hours'),
    (TRANSFER_SUPPLEMENT_COST_TYPE_BYTRANSPORTSHOURS, 'By Transports Hours'),
)

ROOM_TYPE_SINGLE = 'S'
ROOM_TYPE_DOUBLE = 'D'
ROOM_TYPE_TRIPLE = 'T'
ROOM_TYPES = (
    (ROOM_TYPE_SINGLE, 'Single'),
    (ROOM_TYPE_DOUBLE, 'Double'),
    (ROOM_TYPE_TRIPLE, 'Triple'),
)

BOARD_TYPE_NB = 'NB'
BOARD_TYPE_BB = 'BB'
BOARD_TYPE_HB = 'HB'
BOARD_TYPE_FB = 'FB'
BOARD_TYPE_AI = 'AI'
BOARD_TYPES = (
    (BOARD_TYPE_NB, 'NB'),
    (BOARD_TYPE_BB, 'BB'),
    (BOARD_TYPE_HB, 'HB'),
    (BOARD_TYPE_FB, 'FB'),
    (BOARD_TYPE_AI, 'AI'),
)

PAX_TYPE_BABY = 'B'
PAX_TYPE_CHILD = 'C'
PAX_TYPE_ADULT = 'A'
PAX_TYPE_SENIOR = 'S'
PAX_TYPES = (
    (PAX_TYPE_BABY, 'Baby'),
    (PAX_TYPE_CHILD, 'Child'),
    (PAX_TYPE_ADULT, 'Adult'),
    (PAX_TYPE_SENIOR, 'Senior'),
)
