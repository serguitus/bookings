"""
Contants for Finance
"""
STATUS_DRAFT = 'D'
STATUS_READY = 'R'
STATUS_CANCELLED = 'C'

STATUSES = (
    (STATUS_DRAFT, 'Draft'),
    (STATUS_READY, 'Ready'),
    (STATUS_CANCELLED, 'Cancelled'),
)

STATUS_LABELS = {
    STATUS_DRAFT: 'Draft',
    STATUS_READY: 'Ready',
    STATUS_CANCELLED: 'Cancelled'
}

DOC_TYPE_DEPOSIT = 'DEPOSIT'
DOC_TYPE_WITHDRAW = 'WITHDRAW'
DOC_TYPE_TRANSFER = 'TRANSFER'
DOC_TYPE_CURRENCY_EXCHANGE = 'CURRENCY_EXCHANGE'
DOC_TYPE_LOAN_ENTITY_DEPOSIT = 'LOAN_ENTITY_DEPOSIT'
DOC_TYPE_LOAN_ENTITY_WITHDRAW = 'LOAN_ENTITY_WITHDRAW'
DOC_TYPE_LOAN_ACCOUNT_DEPOSIT = 'LOAN_ACCOUNT_DEPOSIT'
DOC_TYPE_LOAN_ACCOUNT_WITHDRAW = 'LOAN_ACCOUNT_WITHDRAW'
DOC_TYPE_AGENCY_INVOICE = 'AGENCY_INVOICE'
DOC_TYPE_AGENCY_BOOKING_INVOICE = 'AGENCY_BKNG_INVOICE'
DOC_TYPE_AGENCY_PAYMENT = 'AGENCY_PAYMENT'
DOC_TYPE_AGENCY_DEVOLUTION = 'AGENCY_DEVOLUTION'
DOC_TYPE_AGENCY_DISCOUNT = 'AGENCY_DISCOUNT'
DOC_TYPE_PROVIDER_INVOICE = 'PROVIDER_INVOICE'
DOC_TYPE_PROVIDER_PAYMENT = 'PROVIDER_PAYMENT'
DOC_TYPE_PROVIDER_DEVOLUTION = 'PROVIDER_DEVOLUTION'
DOC_TYPE_PROVIDER_DISCOUNT = 'PROVIDER_DISCOUNT'
DOC_TYPE_PROVIDER_PAYMENT_WITHDRAW = 'PROV.PAYM.WITHDRAW'

DOC_TYPES = (
    (DOC_TYPE_DEPOSIT, 'Deposit'),
    (DOC_TYPE_WITHDRAW, 'Withdraw'),
    (DOC_TYPE_TRANSFER, 'Transfer'),
    (DOC_TYPE_CURRENCY_EXCHANGE, 'Currency Exchange'),
    (DOC_TYPE_LOAN_ENTITY_DEPOSIT, 'Loan Entity Deposit'),
    (DOC_TYPE_LOAN_ENTITY_WITHDRAW, 'Loan Entity Withdraw'),
    (DOC_TYPE_LOAN_ACCOUNT_DEPOSIT, 'Loan Account Deposit'),
    (DOC_TYPE_LOAN_ACCOUNT_WITHDRAW, 'Loan Account Withdraw'),
    (DOC_TYPE_AGENCY_INVOICE, 'Agency Invoice'),
    (DOC_TYPE_AGENCY_PAYMENT, 'Agency Payment'),
    (DOC_TYPE_AGENCY_DEVOLUTION, 'Agency Devolution'),
    (DOC_TYPE_AGENCY_DISCOUNT, 'Agency Discount'),
    (DOC_TYPE_AGENCY_BOOKING_INVOICE, 'Ag.Booking Invoice'),
    (DOC_TYPE_PROVIDER_INVOICE, 'Provider Invoice'),
    (DOC_TYPE_PROVIDER_PAYMENT, 'Provider Payment'),
    (DOC_TYPE_PROVIDER_DEVOLUTION, 'Provider Devolution'),
    (DOC_TYPE_PROVIDER_DISCOUNT, 'Provider Discount'),
    (DOC_TYPE_PROVIDER_PAYMENT_WITHDRAW, 'Prov.Payment Withdraw'),
)

DOC_CLASSES = {
    DOC_TYPE_DEPOSIT: 'finance_deposit',
    DOC_TYPE_WITHDRAW: 'finance_withdraw',
    DOC_TYPE_TRANSFER: 'finance_transfer',
    DOC_TYPE_CURRENCY_EXCHANGE: 'finance_currencyexchange',
    DOC_TYPE_LOAN_ENTITY_DEPOSIT: 'finance_loanentitydeposit',
    DOC_TYPE_LOAN_ENTITY_WITHDRAW: 'finance_loanentitywithdraw',
    DOC_TYPE_LOAN_ACCOUNT_DEPOSIT: 'finance_loanaccountdeposit',
    DOC_TYPE_LOAN_ACCOUNT_WITHDRAW: 'finance_loanaccountwithdraw',
    DOC_TYPE_AGENCY_INVOICE: 'finance_agencyinvoice',
    DOC_TYPE_AGENCY_PAYMENT: 'finance_agencypayment',
    DOC_TYPE_AGENCY_DEVOLUTION: 'finance_agencydevolution',
    DOC_TYPE_AGENCY_DISCOUNT: 'finance_agencydiscount',
    DOC_TYPE_AGENCY_BOOKING_INVOICE: 'booking_bookinginvoice',
    DOC_TYPE_PROVIDER_INVOICE: 'finance_providerinvoice',
    DOC_TYPE_PROVIDER_PAYMENT: 'finance_providerpayment',
    DOC_TYPE_PROVIDER_DEVOLUTION: 'finance_providerdevolution',
    DOC_TYPE_PROVIDER_DISCOUNT: 'finance_providerdiscount',
    # DOC_TYPE_PROVIDER_PAYMENT_WITHDRAW: 'Prov.Payment Withdraw',

}

BOOTSTRAP_STYLE_FINANCE_DOCUMENT_STATUS_MAPPING = {
    STATUS_CANCELLED: 'table-active',
    STATUS_DRAFT: 'table-warning',
    STATUS_READY: 'table-success',
}

ERROR_INVALID_MATCH = 'Invalid total matching (%s)'
ERROR_DIFFERENT_DOCUMENTS = '%s documents must be the same'
ERROR_MATCH_AMOUNT = 'Can not decrease Amount below matched amount'
ERROR_MATCH_ACCOUNT = 'Can not change Account if document has matches'
ERROR_MATCH_CURRENCY = 'Can not change Currency if document has matches'
ERROR_MATCH_OVERMATCHED = 'Matched amount is too high for %s'
ERROR_MATCH_LOAN_ENTITY = 'Can not change Loan Entity if document has matches'
ERROR_MATCH_LOAN_ACCOUNT = 'Can not change Loan Account if document has matches'
ERROR_MATCH_AGENCY = 'Can not change Agency if document has matches'
ERROR_MATCH_PROVIDER = 'Can not change Provider if document has matches'
ERROR_MATCH_STATUS = 'Can not change Status from Ready if document has matches'
ERROR_MATCH_WITHOUT_AMOUNT = 'Amount (%s) Insufficient for total matching (%s)'
ERROR_NOT_READY = '%s Status must be Ready'
