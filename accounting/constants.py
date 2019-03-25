CURRENCY_CUC = 'CUC'
CURRENCY_USD = 'USD'
CURRENCY_EUR = 'EUR'
CURRENCY_CUP = 'CUP'

CURRENCIES = (
    (CURRENCY_CUC, 'CUC'),
    (CURRENCY_USD, 'USD'),
    (CURRENCY_EUR, 'EUR'),
    (CURRENCY_CUP, 'CUP')
)

MOVEMENT_TYPE_INPUT = 'I'
MOVEMENT_TYPE_OUTPUT = 'O'

MOVEMENT_TYPES = (
    (MOVEMENT_TYPE_INPUT, 'Input'),
    (MOVEMENT_TYPE_OUTPUT, 'Output'),
)

ERROR_ACCOUNT_REQUIRED = 'Account Required'
ERROR_AMOUNT_REQUIRED = 'Positive Amount Required'
ERROR_DISABLED = 'Account %s is Disabled'
ERROR_NOT_BALANCE = 'Account %s Balance (%s) Insufficient for (%s)'
ERROR_UNKNOWN_MOVEMENT_TYPE = 'Unknown Movement Type: %s'
ERROR_SAME_CURRENCY = 'Account %s and %s must have different currencies'
ERROR_DIFFERENT_CURRENCY = 'Account %s and %s must have same currency'
ERROR_MODEL_NOT_FOUND = 'Invalid %s PK'
ERROR_MODEL = 'Invalid %s'
