from django.db import models
from django.conf import settings

from accounting.constants import *
from accounting.models import *

from .constants import *


class Agency(models.Model):
    class Meta:
        verbose_name = 'Agency'
        verbose_name_plural = 'Agencies'
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=500, blank=True, null=True)
    currency = models.CharField(
        max_length=5, choices=CURRENCIES, default=CURRENCY_USD)
    enabled = models.BooleanField(default=True)

    def __str__(self):
        return '%s (%s)' % (self.name, CURRENCY_DICT[self.currency])


class Provider(models.Model):
    class Meta:
        verbose_name = 'Provider'
        verbose_name_plural = 'Providers'
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=500, blank=True, null=True)
    currency = models.CharField(
        max_length=5, choices=CURRENCIES, default=CURRENCY_CUC)
    enabled = models.BooleanField(default=True)

    def __str__(self):
        return '%s (%s)' % (self.name, CURRENCY_DICT[self.currency])


class FinantialDocument(models.Model):
    class Meta:
        verbose_name = 'Finantial Document'
        verbose_name_plural = 'Finantials Documents'
    name = models.CharField(max_length=50)
    date = models.DateTimeField()
    currency = models.CharField(
        max_length=5, choices=CURRENCIES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(
        max_length=2, choices=STATUSES, default=STATUS_DRAFT)

    def __str__(self):
        return '%s (%s)' % (self.name, CURRENCY_DICT[self.currency])


class FinantialDocumentHistory(models.Model):
    class Meta:
        verbose_name = 'Finantial Document History'
        verbose_name_plural = 'Finantials Documents History'
    document = models.ForeignKey(FinantialDocument)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        help_text='User who did the operation.',
    )
    date = models.DateTimeField()
    old_status = models.CharField(
        max_length=2, choices=STATUSES)
    new_status = models.CharField(
        max_length=2, choices=STATUSES)


class AccountingDocument(models.Model):
    class Meta:
        abstract = True
    current_operation = models.ForeignKey(Operation, blank=True, null=True)


class AccountingDocumentHistory(models.Model):
    class Meta:
        verbose_name = 'Accounting Document History'
        verbose_name_plural = 'Accountings Documents History'
    document = models.ForeignKey(FinantialDocument)
    operation = models.ForeignKey(Operation)


class MatchingDocument(models.Model):
    class Meta:
        abstract = True
    unmatched = models.DecimalField(max_digits=10, decimal_places=2)


class Deposit(FinantialDocument, AccountingDocument):
    class Meta:
        verbose_name = 'Deposit'
        verbose_name_plural = 'Deposits'
    deposit_account = models.ForeignKey(Account)


class Withdraw(FinantialDocument, AccountingDocument):
    class Meta:
        verbose_name = 'Withdraw'
        verbose_name_plural = 'Withdraws'
    withdraw_account = models.ForeignKey(Account)


class Loan(FinantialDocument, AccountingDocument):
    class Meta:
        verbose_name = 'Loan'
        verbose_name_plural = 'Loans'
    account = models.ForeignKey(Account)


class LoanDevolution(FinantialDocument, AccountingDocument):
    class Meta:
        verbose_name = 'Loan Devolution'
        verbose_name_plural = 'Loans Devolutions'
    account = models.ForeignKey(Account)


class LoanAccount(Loan):
    class Meta:
        verbose_name = 'Loan Account'
        verbose_name_plural = 'Loans Accounts'
    account_dst = models.ForeignKey(Account, related_name='account_dst')


class LoanAccountDevolution(LoanDevolution):
    class Meta:
        verbose_name = 'Loan Account Devolution'
        verbose_name_plural = 'Loans Accounts Devolutions'
    account_src = models.ForeignKey(Account, related_name='account_src')


class LoanMatch(models.Model):
    class Meta:
        verbose_name = 'Loan Match'
        verbose_name_plural = 'Loans Matches'
    currency = models.DecimalField(max_digits=10, decimal_places=2)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    loan = models.ForeignKey(Loan)
    devolution = models.ForeignKey(LoanDevolution)


class AgencyInvoiceItem(models.Model):
    class Meta:
        verbose_name = 'Agency Invoice Item'
        verbose_name_plural = 'Agencies Invoices Items'
    agency = models.ForeignKey(Agency)
    file = models.FileField()


class AgencyDocument(FinantialDocument):
    class Meta:
        abstract = True
    agency = models.ForeignKey(Agency)


class AgencyDebitDocument(AgencyDocument):
    class Meta:
        verbose_name = 'Agency Debit Document'
        verbose_name_plural = 'Agencies Debits Documents'


class AgencyCreditDocument(AgencyDocument):
    class Meta:
        verbose_name = 'Agency Credit Document'
        verbose_name_plural = 'Agencies Credits Documents'


class AgencyPayment(AgencyCreditDocument, AccountingDocument):
    class Meta:
        verbose_name = 'Agency Payment'
        verbose_name_plural = 'Agencies Payments'
    deposit_account = models.ForeignKey(Account)


class AgencyDiscount(AgencyCreditDocument):
    class Meta:
        verbose_name = 'Agency Discount'
        verbose_name_plural = 'Agencies Discounts'


class AgencyInvoice(AgencyDebitDocument):
    class Meta:
        verbose_name = 'Agency Invoice'
        verbose_name_plural = 'Agencies Invoices'
    item = models.ForeignKey(AgencyInvoiceItem)


class AgencyDevolution(AgencyDebitDocument, AccountingDocument):
    class Meta:
        verbose_name = 'Agency Devolution'
        verbose_name_plural = 'Agencies Devolutions'
    withdraw_account = models.ForeignKey(Account)


class AgencyMatch(models.Model):
    class Meta:
        verbose_name = 'Agency Match'
        verbose_name_plural = 'Agencies Matches'
    currency = models.DecimalField(max_digits=10, decimal_places=2)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    debit_document = models.ForeignKey(AgencyDebitDocument)
    credit_document = models.ForeignKey(AgencyCreditDocument)


class ProviderInvoiceItem(models.Model):
    class Meta:
        verbose_name = 'Provider Invoice Item'
        verbose_name_plural = 'Providers Invoices Items'
    provider = models.ForeignKey(Provider)


class ProviderDocument(FinantialDocument):
    class Meta:
        abstract = True
    provider = models.ForeignKey(Provider)


class ProviderDebitDocument(ProviderDocument):
    class Meta:
        verbose_name = 'Provider Debit Document'
        verbose_name_plural = 'Providers Debits Documents'


class ProviderCreditDocument(ProviderDocument):
    class Meta:
        verbose_name = 'Provider Credit Document'
        verbose_name_plural = 'Providers Credits Documents'


class ProviderPayment(ProviderDebitDocument, AccountingDocument):
    class Meta:
        verbose_name = 'Provider Payment'
        verbose_name_plural = 'Providers Payments'
    withdraw_account = models.ForeignKey(Account)


class ProviderDiscount(ProviderDebitDocument):
    class Meta:
        verbose_name = 'Provider Discount'
        verbose_name_plural = 'Providers Discounts'


class ProviderInvoice(ProviderCreditDocument):
    class Meta:
        verbose_name = 'Provider Invoice'
        verbose_name_plural = 'Providers Invoices'
    item = models.ForeignKey(ProviderInvoiceItem)


class ProviderDevolution(ProviderCreditDocument, AccountingDocument):
    class Meta:
        verbose_name = 'Provider Devolution'
        verbose_name_plural = 'Providers Devolutions'
    deposit_account = models.ForeignKey(Account)


class ProviderMatch(models.Model):
    class Meta:
        verbose_name = 'Provider Match'
        verbose_name_plural = 'Providers Matches'
    currency = models.DecimalField(max_digits=10, decimal_places=2)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    debit_document = models.ForeignKey(ProviderDebitDocument)
    credit_document = models.ForeignKey(ProviderCreditDocument)

