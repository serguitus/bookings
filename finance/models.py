from django.db import models
from django.conf import settings

from accounting.constants import CURRENCIES, CURRENCY_DICT, CURRENCY_CUC, CURRENCY_USD
from accounting.models import Account, Operation

from finance.constants import STATUSES, STATUS_DRAFT


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
    account = models.ForeignKey(Account)
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
    amount_matched = models.DecimalField(max_digits=10, decimal_places=2, default=0)


class Deposit(FinantialDocument, AccountingDocument):
    class Meta:
        verbose_name = 'Deposit'
        verbose_name_plural = 'Deposits'


class Withdraw(FinantialDocument, AccountingDocument):
    class Meta:
        verbose_name = 'Withdraw'
        verbose_name_plural = 'Withdraws'


class LoanDeposit(FinantialDocument, AccountingDocument, MatchingDocument):
    class Meta:
        verbose_name = 'Loan Deposit'
        verbose_name_plural = 'Loans Deposits'


class LoanWithdraw(FinantialDocument, AccountingDocument, MatchingDocument):
    class Meta:
        verbose_name = 'Loan Withdraw'
        verbose_name_plural = 'Loans Withdraws'


class LoanMatch(models.Model):
    class Meta:
        verbose_name = 'Loan Match'
        verbose_name_plural = 'Loans Matches'
    loan_deposit = models.ForeignKey(LoanDeposit)
    loan_withdraw = models.ForeignKey(LoanWithdraw)
    amount = models.DecimalField(max_digits=10, decimal_places=2)


class LoanAccountDeposit(LoanDeposit):
    class Meta:
        verbose_name = 'Loan Account Deposit'
        verbose_name_plural = 'Loans Accounts Deposits'
    withdraw_account = models.ForeignKey(Account, related_name='withdraw_account')


class LoanAccountWithdraw(LoanWithdraw):
    class Meta:
        verbose_name = 'Loan Account Withdraw'
        verbose_name_plural = 'Loans Accounts Withdraws'
    deposit_account = models.ForeignKey(Account, related_name='deposit_account')


class LoanAccountMatch(models.Model):
    class Meta:
        verbose_name = 'Loan Account Match'
        verbose_name_plural = 'Loans Accounts Matches'
    loan_account_deposit = models.ForeignKey(LoanAccountDeposit)
    loan_account_withdraw = models.ForeignKey(LoanAccountWithdraw)
    amount = models.DecimalField(max_digits=10, decimal_places=2)


class AgencyInvoiceItem(models.Model):
    class Meta:
        verbose_name = 'Agency Invoice Item'
        verbose_name_plural = 'Agencies Invoices Items'
    agency = models.ForeignKey(Agency)
    file = models.FileField()


class AgencyDocument(FinantialDocument):
    class Meta:
        verbose_name = 'Agency Document'
        verbose_name_plural = 'Agencies Documents'
    agency = models.ForeignKey(Agency)


class AgencyDebitDocument(AgencyDocument):
    class Meta:
        verbose_name = 'Agency Debit Document'
        verbose_name_plural = 'Agencies Debits Documents'


class AgencyCreditDocument(AgencyDocument):
    class Meta:
        verbose_name = 'Agency Credit Document'
        verbose_name_plural = 'Agencies Credits Documents'


class AgencyInvoice(AgencyDebitDocument):
    class Meta:
        verbose_name = 'Agency Invoice'
        verbose_name_plural = 'Agencies Invoices'
    item = models.ForeignKey(AgencyInvoiceItem)


class AgencyPayment(AgencyCreditDocument, AccountingDocument):
    class Meta:
        verbose_name = 'Agency Payment'
        verbose_name_plural = 'Agencies Payments'


class AgencyDiscount(AgencyCreditDocument):
    class Meta:
        verbose_name = 'Agency Discount'
        verbose_name_plural = 'Agencies Discounts'


class AgencyDevolution(AgencyDebitDocument, AccountingDocument):
    class Meta:
        verbose_name = 'Agency Devolution'
        verbose_name_plural = 'Agencies Devolutions'


class AgencyMatch(models.Model):
    class Meta:
        verbose_name = 'Agency Match'
        verbose_name_plural = 'Agencies Matches'
    debit_document = models.ForeignKey(AgencyDebitDocument)
    credit_document = models.ForeignKey(AgencyCreditDocument)
    amount = models.DecimalField(max_digits=10, decimal_places=2)


class ProviderInvoiceItem(models.Model):
    class Meta:
        verbose_name = 'Provider Invoice Item'
        verbose_name_plural = 'Providers Invoices Items'
    provider = models.ForeignKey(Provider)


class ProviderDocument(FinantialDocument):
    class Meta:
        verbose_name = 'Provider Document'
        verbose_name_plural = 'Providers Documents'
    provider = models.ForeignKey(Provider)


class ProviderDebitDocument(ProviderDocument):
    class Meta:
        verbose_name = 'Provider Debit Document'
        verbose_name_plural = 'Providers Debits Documents'


class ProviderCreditDocument(ProviderDocument):
    class Meta:
        verbose_name = 'Provider Credit Document'
        verbose_name_plural = 'Providers Credits Documents'


class ProviderInvoice(ProviderDebitDocument):
    class Meta:
        verbose_name = 'Provider Invoice'
        verbose_name_plural = 'Providers Invoices'
    item = models.ForeignKey(ProviderInvoiceItem)


class ProviderPayment(ProviderCreditDocument, AccountingDocument):
    class Meta:
        verbose_name = 'Provider Payment'
        verbose_name_plural = 'Providers Payments'


class ProviderDiscount(ProviderCreditDocument):
    class Meta:
        verbose_name = 'Provider Discount'
        verbose_name_plural = 'Providers Discounts'


class ProviderDevolution(ProviderDebitDocument, AccountingDocument):
    class Meta:
        verbose_name = 'Provider Devolution'
        verbose_name_plural = 'Providers Devolutions'


class ProviderMatch(models.Model):
    class Meta:
        verbose_name = 'Provider Match'
        verbose_name_plural = 'Providers Matches'
    debit_document = models.ForeignKey(ProviderDebitDocument)
    credit_document = models.ForeignKey(ProviderCreditDocument)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
