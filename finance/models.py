from django.db import connection, models
from django.core.exceptions import ValidationError
from django.conf import settings
from django.utils.timezone import now

from accounting.constants import (
    CURRENCIES, CURRENCY_CUC, CURRENCY_USD)
from accounting.models import Account, Operation

from finance.constants import (
    STATUSES, STATUS_DRAFT, STATUS_READY,
    DOC_TYPES,
    DOC_TYPE_DEPOSIT, DOC_TYPE_WITHDRAW, DOC_TYPE_TRANSFER, DOC_TYPE_CURRENCY_EXCHANGE,
    DOC_TYPE_LOAN_ENTITY_DEPOSIT, DOC_TYPE_LOAN_ENTITY_WITHDRAW,
    DOC_TYPE_LOAN_ACCOUNT_DEPOSIT, DOC_TYPE_LOAN_ACCOUNT_WITHDRAW,
    DOC_TYPE_AGENCY_INVOICE, DOC_TYPE_AGENCY_PAYMENT,
    DOC_TYPE_AGENCY_DEVOLUTION, DOC_TYPE_AGENCY_DISCOUNT,
    DOC_TYPE_PROVIDER_INVOICE, DOC_TYPE_PROVIDER_PAYMENT,
    DOC_TYPE_PROVIDER_DEVOLUTION, DOC_TYPE_PROVIDER_DISCOUNT)


class FinantialDocument(models.Model):
    class Meta:
        verbose_name = 'Finantial Document'
        verbose_name_plural = 'Finantials Documents'
    document_type = models.CharField(max_length=50, choices=DOC_TYPES)
    name = models.CharField(max_length=200, default='Finantial Document')
    date = models.DateField(default=now)
    currency = models.CharField(max_length=5, choices=CURRENCIES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(
        max_length=2, choices=STATUSES, default=STATUS_DRAFT)

    def fill_data(self):
        pass

    def __str__(self):
        return self.name

    def delete(self, using=None, keep_parents=False):
        raise ValidationError(
            'Can not delete Finantials Documents')


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
        max_length=2, choices=STATUSES,
        blank=True, null=True)
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
    matched_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)


class Deposit(FinantialDocument, AccountingDocument):
    class Meta:
        verbose_name = 'Deposit'
        verbose_name_plural = 'Deposits'

    def fill_data(self):
        self.document_type = DOC_TYPE_DEPOSIT
        account = Account.objects.get(pk=self.account_id)
        status = ''
        if not (self.status is STATUS_READY):
            status = ' - %s' % self.get_status_display()
        self.name = '%s%s - Deposit on %s of %s %s ' % (
            self.date, status.upper(), account, self.amount, account.get_currency_display())

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        self.fill_data()
        # Call the real save() method
        super(Deposit, self).save(force_insert, force_update, using, update_fields)

class Withdraw(FinantialDocument, AccountingDocument):
    class Meta:
        verbose_name = 'Withdraw'
        verbose_name_plural = 'Withdraws'

    def fill_data(self):
        self.document_type = DOC_TYPE_WITHDRAW
        account = Account.objects.get(pk=self.account_id)
        self.name = '%s - Withdraw from %s of %s %s ' % (
            self.date, account, self.amount, account.get_currency_display())
        return self.name

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        self.fill_data()
        # Call the real save() method
        super(Withdraw, self).save(force_insert, force_update, using, update_fields)


class CurrencyExchange(FinantialDocument, AccountingDocument):
    class Meta:
        verbose_name = 'Currency Exchange'
        verbose_name_plural = 'Currencies Exchanges'
    exchange_account = models.ForeignKey(Account, related_name='exchange_account')
    exchange_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def fill_data(self):
        self.document_type = DOC_TYPE_CURRENCY_EXCHANGE
        account = Account.objects.get(pk=self.account_id)
        exchange_account = Account.objects.get(pk=self.exchange_account_id)
        self.name = '%s - Exchange to %s of %s %s from %s of %s %s' % (
            self.date, account, self.amount, account.get_currency_display(),
            exchange_account, self.exchange_amount, exchange_account.get_currency_display())

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        self.fill_data()
        # Call the real save() method
        super(CurrencyExchange, self).save(force_insert, force_update, using, update_fields)


class Transfer(FinantialDocument, AccountingDocument):
    class Meta:
        verbose_name = 'Transfer'
        verbose_name_plural = 'Transfers'
    transfer_account = models.ForeignKey(Account, related_name='transfer_account')

    def fill_data(self):
        self.document_type = DOC_TYPE_TRANSFER
        account = Account.objects.get(pk=self.account_id)
        transfer_account = Account.objects.get(pk=self.transfer_account_id)
        self.name = '%s - Transfer to %s of %s %s from %s' % (
            self.date, account, self.amount, account.currency, transfer_account)

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        self.fill_data()
        # Call the real save() method
        super(Transfer, self).save(force_insert, force_update, using, update_fields)


class LoanDocument(FinantialDocument, AccountingDocument, MatchingDocument):
    class Meta:
        abstract = True


class LoanEntity(models.Model):
    class Meta:
        verbose_name = 'Loan Entity'
        verbose_name_plural = 'Loans Entities'
        unique_together = (('name',),)

    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class LoanEntityCurrency(models.Model):
    class Meta:
        verbose_name = 'Loan Entity Currency'
        verbose_name_plural = 'Loans Entities Currencies'
        unique_together = (('loan_entity', 'currency',),)
    loan_entity = models.ForeignKey(LoanEntity)
    currency = models.CharField(max_length=5, choices=CURRENCIES)
    credit_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    debit_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    matched_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return '%s (%s)' % (self.name, self.get_currency_display())

    def fix_credit_amount(self):
        cursor = connection.cursor()
        try:
            cursor.execute("""
                UPDATE finance_loanentitycurrency lec SET lec.credit_amount = (
                    SELECT COALESCE(SUM(fd.amount), 0)
                    FROM finance_loanentitydeposit ledd
                        INNER JOIN finance_loanentitydocument led
                            ON led.finantialdocument_ptr_id = ledd.loanentitydocument_ptr_id
                        INNER JOIN finance_finantialdocument fd
                            ON fd.id = led.finantialdocument_ptr_id
                    WHERE led.loan_entity_id = lec.loan_entity_id
                        AND fd.currency = lec.currency
                        AND fd.status = %s)
                WHERE lec.id = %s
                """, [STATUS_READY, self.pk])
            self.refresh_from_db()
        finally:
            cursor.close()

    @classmethod
    def fix_credit_amounts(cls):
        cursor = connection.cursor()
        try:
            cursor.execute("""
                UPDATE finance_loanentitycurrency lec SET lec.credit_amount = (
                    SELECT COALESCE(SUM(fd.amount), 0)
                    FROM finance_loanentitydeposit ledd
                        INNER JOIN finance_loanentitydocument led
                            ON led.finantialdocument_ptr_id = ledd.loanentitydocument_ptr_id
                        INNER JOIN finance_finantialdocument fd
                            ON fd.id = led.finantialdocument_ptr_id
                    WHERE led.loan_entity_id = lec.loan_entity_id
                        AND fd.currency = lec.currency
                        AND fd.status = %s)
            """, [STATUS_READY])
        finally:
            cursor.close()

    def fix_debit_amount(self):
        cursor = connection.cursor()
        try:
            cursor.execute("""
                UPDATE finance_loanentitycurrency lec SET lec.credit_amount = (
                    SELECT COALESCE(SUM(fd.amount), 0)
                    FROM finance_loanentitywithdraw lew
                        INNER JOIN finance_loanentitydocument led
                            ON led.finantialdocument_ptr_id = lew.loanentitydocument_ptr_id
                        INNER JOIN finance_finantialdocument fd
                            ON fd.id = led.finantialdocument_ptr_id
                    WHERE led.loan_entity_id = lec.loan_entity_id
                        AND fd.currency = lec.currency
                        AND fd.status = %s)
                WHERE lec.id = %s
                """, [STATUS_READY, self.pk])
            self.refresh_from_db()
        finally:
            cursor.close()

    @classmethod
    def fix_debit_amounts(cls):
        cursor = connection.cursor()
        try:
            cursor.execute("""
                UPDATE finance_loanentitycurrency lec SET lec.credit_amount = (
                    SELECT COALESCE(SUM(fd.amount), 0)
                    FROM finance_loanentitywithdraw lew
                        INNER JOIN finance_loanentitydocument led
                            ON led.finantialdocument_ptr_id = lew.loanentitydocument_ptr_id
                        INNER JOIN finance_finantialdocument fd
                            ON fd.id = led.finantialdocument_ptr_id
                    WHERE led.loan_entity_id = lec.loan_entity_id
                        AND fd.currency = lec.currency
                        AND fd.status = %s)
            """, [STATUS_READY])
        finally:
            cursor.close()

    def fix_matched_amount(self):
        cursor = connection.cursor()
        try:
            cursor.execute("""
                UPDATE finance_loanentitycurrency lec SET lec.matched_amount = (
                    SELECT COALESCE(SUM(lem.matched_amount), 0)
                    FROM finance_loanentitymatch lem
                        INNER JOIN finance_loanentitydeposit ledd
                            ON ledd.loanentitydocument_ptr_id = lem.loan_entity_deposit_id
                        INNER JOIN finance_loanentitydocument led1
                            ON led1.finantialdocument_ptr_id = ledd.loanentitydocument_ptr_id
                        INNER JOIN finance_finantialdocument fd1
                            ON fd1.id = led1.finantialdocument_ptr_id
                        INNER JOIN finance_loanentitywithdraw lew
                            ON lew.loanentitydocument_ptr_id = lem.loan_entity_withdraw_id
                        INNER JOIN finance_loanentitydocument led2
                            ON led2.finantialdocument_ptr_id = lew.loanentitydocument_ptr_id
                        INNER JOIN finance_finantialdocument fd2
                            ON fd2.id = led2.finantialdocument_ptr_id
                    WHERE led1.loan_entity_id = lec.loan_entity_id
                        AND led2.loan_entity_id = lec.loan_entity_id
                        AND fd1.currency = lec.currency
                        AND fd2.currency = lec.currency
                        AND fd1.status = %s
                        AND fd2.status = fd1.status)
                WHERE lec.id = %s
                """, [STATUS_READY, self.pk])
            self.refresh_from_db()
        finally:
            cursor.close()

    @classmethod
    def fix_matched_amounts(cls):
        cursor = connection.cursor()
        try:
            cursor.execute("""
                UPDATE finance_loanentitycurrency lec SET lec.matched_amount = (
                    SELECT COALESCE(SUM(lem.matched_amount), 0)
                    FROM finance_loanentitymatch lem
                        INNER JOIN finance_loanentitydeposit ledd
                            ON ledd.loanentitydocument_ptr_id = lem.loan_entity_deposit_id
                        INNER JOIN finance_loanentitydocument led1
                            ON led1.finantialdocument_ptr_id = ledd.loanentitydocument_ptr_id
                        INNER JOIN finance_finantialdocument fd1
                            ON fd1.id = led1.finantialdocument_ptr_id
                        INNER JOIN finance_loanentitywithdraw lew
                            ON lew.loanentitydocument_ptr_id = lem.loan_entity_withdraw_id
                        INNER JOIN finance_loanentitydocument led2
                            ON led2.finantialdocument_ptr_id = lew.loanentitydocument_ptr_id
                        INNER JOIN finance_finantialdocument fd2
                            ON fd2.id = led2.finantialdocument_ptr_id
                    WHERE led1.loan_entity_id = lec.loan_entity_id
                        AND led2.loan_entity_id = lec.loan_entity_id
                        AND fd1.currency = lec.currency
                        AND fd2.currency = lec.currency
                        AND fd1.status = %s
                        AND fd2.status = fd1.status)
            """, [STATUS_READY])
        finally:
            cursor.close()


class LoanEntityDocument(LoanDocument):
    class Meta:
        verbose_name = 'Loan Entity Document'
        verbose_name_plural = 'Loans Entities Documents'
    loan_entity = models.ForeignKey(LoanEntity)


class LoanEntityDeposit(LoanEntityDocument):
    class Meta:
        verbose_name = 'Loan Entity Deposit'
        verbose_name_plural = 'Loans Entities Deposits'

    def fill_data(self):
        self.document_type = DOC_TYPE_LOAN_ENTITY_DEPOSIT
        account = Account.objects.get(pk=self.account_id)
        loan_entity = LoanEntity.objects.get(pk=self.loan_entity_id)
        self.name = '%s - Loan Entity Deposit to %s of %s %s from %s' % (
            self.date, account, self.amount, account.get_currency_display(), loan_entity)

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        self.fill_data()
        # Call the real save() method
        super(LoanEntityDeposit, self).save(force_insert, force_update, using, update_fields)

    def fix_matched_amount(self):
        cursor = connection.cursor()
        try:
            cursor.execute("""
                UPDATE finance_loanentitydocument led SET led.matched_amount = (
                    SELECT COALESCE(
                        CASE WHEN fd1.status != %s THEN 0 ELSE SUM(lem.matched_amount) END,
                        0)
                    FROM finance_loanentitymatch lem
                        INNER JOIN finance_finantialdocument fd1
                            ON fd1.id = lem.loan_entity_deposit_id
                        INNER JOIN finance_finantialdocument fd2
                            ON fd2.id = lem.loan_entity_withdraw_id
                    WHERE fd1.id = led.finantialdocument_ptr_id
                        AND fd2.status = fd1.status)
                WHERE led.finantialdocument_ptr_id = %s
                """, [STATUS_READY, self.pk])
            self.refresh_from_db()
        finally:
            cursor.close()

    @classmethod
    def fix_matched_amounts(cls):
        cursor = connection.cursor()
        try:
            cursor.execute("""
                UPDATE finance_loanentitydocument led SET led.matched_amount = (
                    SELECT COALESCE(
                        CASE WHEN fd1.status != %s THEN 0 ELSE SUM(lem.matched_amount) END,
                        0)
                    FROM finance_loanentitymatch lem
                        INNER JOIN finance_finantialdocument fd1
                            ON fd1.id = lem.loan_entity_deposit_id
                        INNER JOIN finance_finantialdocument fd2
                            ON fd2.id = lem.loan_entity_withdraw_id
                    WHERE fd1.id = led.finantialdocument_ptr_id
                        AND fd2.status = fd1.status)
            """, [STATUS_READY])
        finally:
            cursor.close()


class LoanEntityWithdraw(LoanEntityDocument):
    class Meta:
        verbose_name = 'Loan Entity Withdraw'
        verbose_name_plural = 'Loans Entities Withdraws'

    def fill_data(self):
        self.document_type = DOC_TYPE_LOAN_ENTITY_WITHDRAW
        account = Account.objects.get(pk=self.account_id)
        loan_entity = LoanEntity.objects.get(pk=self.loan_entity_id)
        self.name = '%s - Loan Entity Withdraw from %s of %s %s to %s' % (
            self.date, account, self.amount, account.get_currency_display(), loan_entity)

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        self.fill_data()
        # Call the real save() method
        super(LoanEntityWithdraw, self).save(force_insert, force_update, using, update_fields)

    def fix_matched_amount(self):
        cursor = connection.cursor()
        try:
            cursor.execute("""
                UPDATE finance_loanentitydocument led SET led.matched_amount = (
                    SELECT COALESCE(
                        CASE WHEN fd1.status != %s THEN 0 ELSE SUM(lem.matched_amount) END,
                        0)
                    FROM finance_loanentitymatch lem
                        INNER JOIN finance_finantialdocument fd1
                            ON fd1.id = lem.loan_entity_withdraw_id
                        INNER JOIN finance_finantialdocument fd2
                            ON fd2.id = lem.loan_entity_deposit_id
                    WHERE fd1.id = led.finantialdocument_ptr_id
                        AND fd2.status = fd1.status)
                WHERE led.finantialdocument_ptr_id = %s
                """, [STATUS_READY, self.pk])
            self.refresh_from_db()
        finally:
            cursor.close()

    @classmethod
    def fix_matched_amounts(cls):
        cursor = connection.cursor()
        try:
            cursor.execute("""
                UPDATE finance_loanentitydocument led SET led.matched_amount = (
                    SELECT COALESCE(
                        CASE WHEN fd1.status != %s THEN 0 ELSE SUM(lem.matched_amount) END,
                        0)
                    FROM finance_loanentitymatch lem
                        INNER JOIN finance_finantialdocument fd1
                            ON fd1.id = lem.loan_entity_withdraw_id
                        INNER JOIN finance_finantialdocument fd2
                            ON fd2.id = lem.loan_entity_deposit_id
                    WHERE fd1.id = led.finantialdocument_ptr_id
                        AND fd2.status = fd1.status)
            """, [STATUS_READY])
        finally:
            cursor.close()


class LoanEntityMatch(models.Model):
    class Meta:
        verbose_name = 'Loan Entity Match'
        verbose_name_plural = 'Loans Entities Matches'
        unique_together = (('loan_entity_deposit', 'loan_entity_withdraw',),)
    loan_entity_deposit = models.ForeignKey(LoanEntityDeposit)
    loan_entity_withdraw = models.ForeignKey(LoanEntityWithdraw)
    matched_amount = models.DecimalField(max_digits=10, decimal_places=2)


class LoanAccount(models.Model):
    class Meta:
        verbose_name = 'Finantial Account'
        verbose_name_plural = 'Finantials Accounts'
        unique_together = (('loan_account',),)
    loan_account = models.ForeignKey(Account)
    credit_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    debit_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    matched_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def fix_credit_amount(self):
        cursor = connection.cursor()
        try:
            cursor.execute("""
                UPDATE finance_loanaccount la SET la.credit_amount = (
                    SELECT COALESCE(SUM(fd.amount), 0)
                    FROM finance_loanaccountdeposit ladd
                        INNER JOIN finance_loanaccountdocument lad
                            ON lad.finantialdocument_ptr_id = ladd.loanaccountdocument_ptr_id
                        INNER JOIN finance_finantialdocument fd
                            ON fd.id = lad.finantialdocument_ptr_id
                    WHERE lad.loan_account_id = la.loan_account_id
                        AND fd.status = %s)
                WHERE la.id = %s
                """, [STATUS_READY, self.pk])
            self.refresh_from_db()
        finally:
            cursor.close()

    @classmethod
    def fix_credit_amounts(cls):
        cursor = connection.cursor()
        try:
            cursor.execute("""
                UPDATE finance_loanaccount la SET la.credit_amount = (
                    SELECT COALESCE(SUM(fd.amount), 0)
                    FROM finance_loanaccountdeposit ladd
                        INNER JOIN finance_loanaccountdocument lad
                            ON lad.finantialdocument_ptr_id = ladd.loanaccountdocument_ptr_id
                        INNER JOIN finance_finantialdocument fd
                            ON fd.id = lad.finantialdocument_ptr_id
                    WHERE lad.loan_account_id = la.loan_account_id
                        AND fd.status = %s)
            """, [STATUS_READY])
        finally:
            cursor.close()

    def fix_debit_amount(self):
        cursor = connection.cursor()
        try:
            cursor.execute("""
                UPDATE finance_loanaccount la SET la.debit_amount = (
                    SELECT COALESCE(SUM(fd.amount), 0)
                    FROM finance_loanaccountwithdraw law
                        INNER JOIN finance_loanaccountdocument lad
                            ON lad.finantialdocument_ptr_id = law.loanaccountdocument_ptr_id
                        INNER JOIN finance_finantialdocument fd
                            ON fd.id = lad.finantialdocument_ptr_id
                    WHERE lad.loan_account_id = la.loan_account_id
                        AND fd.status = %s)
                WHERE la.id = %s
                """, [STATUS_READY, self.pk])
            self.refresh_from_db()
        finally:
            cursor.close()

    @classmethod
    def fix_debit_amounts(cls):
        cursor = connection.cursor()
        try:
            cursor.execute("""
                UPDATE finance_loanaccount la SET la.debit_amount = (
                    SELECT COALESCE(SUM(fd.amount), 0)
                    FROM finance_loanaccountwithdraw law
                        INNER JOIN finance_loanaccountdocument lad
                            ON lad.finantialdocument_ptr_id = law.loanaccountdocument_ptr_id
                        INNER JOIN finance_finantialdocument fd
                            ON fd.id = lad.finantialdocument_ptr_id
                    WHERE lad.loan_account_id = la.loan_account_id
                        AND fd.status = %s)
            """, [STATUS_READY])
        finally:
            cursor.close()

    def fix_matched_amount(self):
        cursor = connection.cursor()
        try:
            cursor.execute("""
                UPDATE finance_loanaccount la SET la.matched_amount = (
                    SELECT COALESCE(SUM(lam.amount), 0)
                    FROM finance_loanaccountmatch lam
                        INNER JOIN finance_loanaccountdeposit ladd
                            ON ladd.loanaccountdocument_ptr_id = lam.loan_account_deposit_id
                        INNER JOIN finance_loanaccountdocument lad1
                            ON lad1.finantialdocument_ptr_id = ladd.loanaccountdocument_ptr_id
                        INNER JOIN finance_finantialdocument fd1
                            ON fd1.id = lad1.finantialdocument_ptr_id
                        INNER JOIN finance_loanaccountwithdraw law
                            ON law.loanaccountdocument_ptr_id = lam.loan_account_withdraw_id
                        INNER JOIN finance_loanaccountdocument lad2
                            ON lad2.finantialdocument_ptr_id = law.loanaccountdocument_ptr_id
                        INNER JOIN finance_finantialdocument fd2
                            ON fd2.id = lad2.finantialdocument_ptr_id
                    WHERE lad1.loan_account_id = la.loan_account_id
                        AND lad2.loan_account_id = la.loan_account_id
                        AND fd1.status = %s
                        AND fd2.status = fd1.status)
                WHERE la.id = %s
                """, [STATUS_READY, self.pk])
            self.refresh_from_db()
        finally:
            cursor.close()

    @classmethod
    def fix_matched_amounts(cls):
        cursor = connection.cursor()
        try:
            cursor.execute("""
                UPDATE finance_loanaccount la SET la.matched_amount = (
                    SELECT COALESCE(SUM(lam.amount), 0)
                    FROM finance_loanaccountmatch lam
                        INNER JOIN finance_loanaccountdeposit ladd
                            ON ladd.loanaccountdocument_ptr_id = lam.loan_account_deposit_id
                        INNER JOIN finance_loanaccountdocument lad1
                            ON lad1.finantialdocument_ptr_id = ladd.loanaccountdocument_ptr_id
                        INNER JOIN finance_finantialdocument fd1
                            ON fd1.id = lad1.finantialdocument_ptr_id
                        INNER JOIN finance_loanaccountwithdraw law
                            ON law.loanaccountdocument_ptr_id = lam.loan_account_withdraw_id
                        INNER JOIN finance_loanaccountdocument lad2
                            ON lad2.finantialdocument_ptr_id = law.loanentitydocument_ptr_id
                        INNER JOIN finance_finantialdocument fd2
                            ON fd2.id = lad2.finantialdocument_ptr_id
                    WHERE lad1.loan_account_id = la.loan_account_id
                        AND lad2.loan_account_id = la.loan_account_id
                        AND fd1.status = %s
                        AND fd2.status = fd1.status)
            """, [STATUS_READY])
        finally:
            cursor.close()


class LoanAccountDocument(LoanDocument):
    class Meta:
        verbose_name = 'Loan Account document'
        verbose_name_plural = 'Loans Accounts Documents'
    loan_account = models.ForeignKey(Account, related_name='loan_account')

class LoanAccountDeposit(LoanAccountDocument):
    class Meta:
        verbose_name = 'Loan Account Deposit'
        verbose_name_plural = 'Loans Accounts Deposits'

    def fill_data(self):
        self.document_type = DOC_TYPE_LOAN_ACCOUNT_DEPOSIT
        account = Account.objects.get(pk=self.account_id)
        loan_account = Account.objects.get(pk=self.loan_account_id)
        self.name = '%s - Loan Account Deposit to %s of %s %s from %s' % (
            self.date, account, self.amount, account.get_currency_display(), loan_account)

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        self.fill_data()
        # Call the real save() method
        super(LoanAccountDeposit, self).save(force_insert, force_update, using, update_fields)

    def fix_matched_amount(self):
        cursor = connection.cursor()
        try:
            cursor.execute("""
                UPDATE finance_loanaccountdocument lad SET lad.matched_amount = (
                    SELECT COALESCE(
                        CASE WHEN fd1.status != %s THEN 0 ELSE SUM(lam.matched_amount) END,
                        0)
                    FROM finance_loanaccountmatch lam
                        INNER JOIN finance_finantialdocument fd1
                            ON fd1.id = lam.loan_account_deposit_id
                        INNER JOIN finance_finantialdocument fd2
                            ON fd2.id = lam.loan_account_withdraw_id
                    WHERE fd1.id = lad.finantialdocument_ptr_id
                        AND fd2.status = fd1.status)
                WHERE lad.finantialdocument_ptr_id = %s
                """, [STATUS_READY, self.pk])
            self.refresh_from_db()
        finally:
            cursor.close()

    @classmethod
    def fix_matched_amounts(cls):
        cursor = connection.cursor()
        try:
            cursor.execute("""
                UPDATE finance_loanaccountdocument lad SET lad.matched_amount = (
                    SELECT COALESCE(
                        CASE WHEN fd1.status != %s THEN 0 ELSE SUM(lam.matched_amount) END,
                        0)
                    FROM finance_loanaccountmatch lam
                        INNER JOIN finance_finantialdocument fd1
                            ON fd1.id = lam.loan_account_deposit_id
                        INNER JOIN finance_finantialdocument fd2
                            ON fd2.id = lam.loan_account_withdraw_id
                    WHERE fd1.id = lad.finantialdocument_ptr_id
                        AND fd2.status = fd1.status)
            """, [STATUS_READY])
        finally:
            cursor.close()


class LoanAccountWithdraw(LoanAccountDocument):
    class Meta:
        verbose_name = 'Loan Account Withdraw'
        verbose_name_plural = 'Loans Accounts Withdraws'

    def fill_data(self):
        self.document_type = DOC_TYPE_LOAN_ACCOUNT_WITHDRAW
        account = Account.objects.get(pk=self.account_id)
        loan_account = Account.objects.get(pk=self.loan_account_id)
        self.name = '%s - Loan Account Withdraw from %s of %s %s to %s' % (
            self.date, account, self.amount, account.get_currency_display(), loan_account)

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        self.fill_data()
        # Call the real save() method
        super(LoanAccountWithdraw, self).save(force_insert, force_update, using, update_fields)

    def fix_matched_amount(self):
        cursor = connection.cursor()
        try:
            cursor.execute("""
                UPDATE finance_loanaccountdocument lad SET lad.matched_amount = (
                    SELECT COALESCE(
                        CASE WHEN fd1.status != %s THEN 0 ELSE SUM(lam.matched_amount) END,
                        0)
                    FROM finance_loanaccountmatch lam
                        INNER JOIN finance_finantialdocument fd1
                            ON fd1.id = lam.loan_account_withdraw_id
                        INNER JOIN finance_finantialdocument fd2
                            ON fd2.id = lam.loan_account_deposit_id
                    WHERE fd1.id = lad.finantialdocument_ptr_id
                        AND fd2.status = fd1.status)
                WHERE lad.finantialdocument_ptr_id = %s
                """, [STATUS_READY, self.pk])
            self.refresh_from_db()
        finally:
            cursor.close()

    @classmethod
    def fix_matched_amounts(cls):
        cursor = connection.cursor()
        try:
            cursor.execute("""
                UPDATE finance_loanaccountdocument lad SET lad.matched_amount = (
                    SELECT COALESCE(
                        CASE WHEN fd1.status != %s THEN 0 ELSE SUM(lam.matched_amount) END,
                        0)
                    FROM finance_loanaccountmatch lam
                        INNER JOIN finance_finantialdocument fd1
                            ON fd1.id = lam.loan_account_withdraw_id
                        INNER JOIN finance_finantialdocument fd2
                            ON fd2.id = lam.loan_account_deposit_id
                    WHERE fd1.id = lad.finantialdocument_ptr_id
                        AND fd2.status = fd1.status)
            """, [STATUS_READY])
        finally:
            cursor.close()


class LoanAccountMatch(models.Model):
    class Meta:
        verbose_name = 'Loan Account Match'
        verbose_name_plural = 'Loans Accounts Matches'
        unique_together = (('loan_account_deposit', 'loan_account_withdraw',),)
    loan_account_deposit = models.ForeignKey(LoanAccountDeposit)
    loan_account_withdraw = models.ForeignKey(LoanAccountWithdraw)
    matched_amount = models.DecimalField(max_digits=10, decimal_places=2)


class Agency(models.Model):
    class Meta:
        verbose_name = 'Agency'
        verbose_name_plural = 'Agencies'
        unique_together = (('name',),)
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=500, blank=True, null=True)
    currency = models.CharField(
        max_length=5, choices=CURRENCIES, default=CURRENCY_USD)
    enabled = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class AgencyCurrency(models.Model):
    class Meta:
        verbose_name = 'Agency Currency Match'
        verbose_name_plural = 'Agencies Currencies Matches'
        unique_together = (('agency', 'currency',),)
    agency = models.ForeignKey(Agency)
    currency = models.CharField(max_length=5, choices=CURRENCIES)
    credit_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    debit_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    matched_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)


class AgencyDocument(FinantialDocument, MatchingDocument):
    class Meta:
        verbose_name = 'Agency Document'
        verbose_name_plural = 'Agencies Documents'
    agency = models.ForeignKey(Agency)


class AgencyDebitDocument(AgencyDocument):
    class Meta:
        verbose_name = 'Agency Debit Document'
        verbose_name_plural = 'Agencies Debits Documents'

    def fix_matched_amount(self):
        cursor = connection.cursor()
        try:
            cursor.execute("""
                UPDATE finance_agencydocument ad SET ad.matched_amount = (
                    SELECT COALESCE(
                        CASE WHEN fd1.status != %s THEN 0 ELSE SUM(adm.matched_amount) END,
                        0)
                    FROM finance_agencydocumentmatch adm
                        INNER JOIN finance_finantialdocument fd1
                            ON fd1.id = adm.debit_document_id
                        INNER JOIN finance_finantialdocument fd2
                            ON fd2.id = adm.credit_document_id
                    WHERE fd1.id = ad.finantialdocument_ptr_id
                        AND fd2.status = fd1.status)
                WHERE ad.finantialdocument_ptr_id = %s
                """, [STATUS_READY, self.pk])
            self.refresh_from_db()
        finally:
            cursor.close()

    @classmethod
    def fix_matched_amounts(cls):
        cursor = connection.cursor()
        try:
            cursor.execute("""
                UPDATE finance_agencydocument ad SET ad.matched_amount = (
                    SELECT COALESCE(
                        CASE WHEN fd1.status != %s THEN 0 ELSE SUM(adm.matched_amount) END,
                        0)
                    FROM finance_agencydocumentmatch adm
                        INNER JOIN finance_finantialdocument fd1
                            ON fd1.id = adm.debdit_document_id
                        INNER JOIN finance_finantialdocument fd2
                            ON fd2.id = adm.credit_document_id
                    WHERE fd1.id = ad.finantialdocument_ptr_id
                        AND fd2.status = fd1.status)
                """, [STATUS_READY])
        finally:
            cursor.close()


class AgencyCreditDocument(AgencyDocument):
    class Meta:
        verbose_name = 'Agency Credit Document'
        verbose_name_plural = 'Agencies Credits Documents'

    def fix_matched_amount(self):
        cursor = connection.cursor()
        try:
            cursor.execute("""
                UPDATE finance_agencydocument ad SET ad.matched_amount = (
                    SELECT COALESCE(
                        CASE WHEN fd1.status != %s THEN 0 ELSE SUM(adm.matched_amount) END,
                        0)
                    FROM finance_agencydocumentmatch adm
                        INNER JOIN finance_finantialdocument fd1
                            ON fd1.id = adm.credit_document_id
                        INNER JOIN finance_finantialdocument fd2
                            ON fd2.id = adm.debit_document_id
                    WHERE fd1.id = ad.finantialdocument_ptr_id
                        AND fd2.status = fd1.status)
                WHERE ad.finantialdocument_ptr_id = %s
                """, [STATUS_READY, self.pk])
            self.refresh_from_db()
        finally:
            cursor.close()

    @classmethod
    def fix_matched_amounts(cls):
        cursor = connection.cursor()
        try:
            cursor.execute("""
                UPDATE finance_agencydocument ad SET ad.matched_amount = (
                    SELECT COALESCE(
                        CASE WHEN fd1.status != %s THEN 0 ELSE SUM(adm.matched_amount) END,
                        0)
                    FROM finance_agencydocumentmatch adm
                        INNER JOIN finance_finantialdocument fd1
                            ON fd1.id = adm.credit_document_id
                        INNER JOIN finance_finantialdocument fd2
                            ON fd2.id = adm.debit_document_id
                    WHERE fd1.id = ad.finantialdocument_ptr_id
                        AND fd2.status = fd1.status)
                """, [STATUS_READY])
        finally:
            cursor.close()


class AgencyInvoice(AgencyDebitDocument):
    class Meta:
        verbose_name = 'Agency Invoice'
        verbose_name_plural = 'Agencies Invoices'

    def fill_data(self):
        self.document_type = DOC_TYPE_AGENCY_INVOICE
        agency = Agency.objects.get(pk=self.agency_id)
        self.name = '%s - Agency Invoice to %s for %s %s' % (
            self.date, agency, self.amount, self.get_currency_display())

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        self.fill_data()
        # Call the real save() method
        super(AgencyInvoice, self).save(force_insert, force_update, using, update_fields)


class AgencyPayment(AgencyCreditDocument, AccountingDocument):
    class Meta:
        verbose_name = 'Agency Payment'
        verbose_name_plural = 'Agencies Payments'

    def fill_data(self):
        self.document_type = DOC_TYPE_AGENCY_PAYMENT
        agency = Agency.objects.get(pk=self.agency_id)
        self.name = '%s - Agency Payment from %s for %s %s' % (
            self.date, agency, self.amount, self.get_currency_display())

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        self.fill_data()
        # Call the real save() method
        super(AgencyPayment, self).save(force_insert, force_update, using, update_fields)


class AgencyDiscount(AgencyCreditDocument):
    class Meta:
        verbose_name = 'Agency Discount'
        verbose_name_plural = 'Agencies Discounts'

    def fill_data(self):
        self.document_type = DOC_TYPE_AGENCY_DISCOUNT
        agency = Agency.objects.get(pk=self.agency_id)
        self.name = '%s - Agency Discount to %s for %s %s' % (
            self.date, agency, self.amount, self.get_currency_display())

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        self.fill_data()
        # Call the real save() method
        super(AgencyDiscount, self).save(force_insert, force_update, using, update_fields)


class AgencyDevolution(AgencyDebitDocument, AccountingDocument):
    class Meta:
        verbose_name = 'Agency Devolution'
        verbose_name_plural = 'Agencies Devolutions'

    def fill_data(self):
        self.document_type = DOC_TYPE_AGENCY_DEVOLUTION
        agency = Agency.objects.get(pk=self.agency_id)
        self.name = '%s - Agency Devolution to %s for %s %s' % (
            self.date, agency, self.amount, self.get_currency_display())

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        self.fill_data()
        # Call the real save() method
        super(AgencyDevolution, self).save(force_insert, force_update, using, update_fields)


class AgencyDocumentMatch(models.Model):
    class Meta:
        verbose_name = 'Agency Match'
        verbose_name_plural = 'Agencies Matches'
        unique_together = (('credit_document', 'debit_document',),)
    credit_document = models.ForeignKey(AgencyCreditDocument)
    debit_document = models.ForeignKey(AgencyDebitDocument)
    matched_amount = models.DecimalField(max_digits=10, decimal_places=2)


class Provider(models.Model):
    class Meta:
        verbose_name = 'Provider'
        verbose_name_plural = 'Providers'
        unique_together = (('name',),)
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=500, blank=True, null=True)
    currency = models.CharField(
        max_length=5, choices=CURRENCIES, default=CURRENCY_CUC)
    enabled = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class ProviderCurrency(models.Model):
    class Meta:
        verbose_name = 'Provider Currency Match'
        verbose_name_plural = 'Providers Currencies Matches'
        unique_together = (('provider', 'currency',),)
    provider = models.ForeignKey(Provider)
    currency = models.CharField(max_length=5, choices=CURRENCIES)
    credit_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    debit_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    matched_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)


class ProviderDocument(FinantialDocument, MatchingDocument):
    class Meta:
        verbose_name = 'Provider Document'
        verbose_name_plural = 'Providers Documents'
    provider = models.ForeignKey(Provider)


class ProviderDebitDocument(ProviderDocument):
    class Meta:
        verbose_name = 'Provider Debit Document'
        verbose_name_plural = 'Providers Debits Documents'

    def fix_matched_amount(self):
        cursor = connection.cursor()
        try:
            cursor.execute("""
                UPDATE finance_providerdocument pd SET pd.matched_amount = (
                    SELECT COALESCE(
                        CASE WHEN fd1.status != %s THEN 0 ELSE SUM(pdm.matched_amount) END,
                        0)
                    FROM finance_providerdocumentmatch pdm
                        INNER JOIN finance_finantialdocument fd1
                            ON fd1.id = pdm.debit_document_id
                        INNER JOIN finance_finantialdocument fd2
                            ON fd2.id = pdm.credit_document_id
                    WHERE fd1.id = pd.finantialdocument_ptr_id
                        AND fd2.status = fd1.status)
                WHERE pd.finantialdocument_ptr_id = %s
                """, [STATUS_READY, self.pk])
            self.refresh_from_db()
        finally:
            cursor.close()

    @classmethod
    def fix_matched_amounts(cls):
        cursor = connection.cursor()
        try:
            cursor.execute("""
                UPDATE finance_providerdocument pd SET pd.matched_amount = (
                    SELECT COALESCE(
                        CASE WHEN fd1.status != %s THEN 0 ELSE SUM(pdm.matched_amount) END,
                        0)
                    FROM finance_providerdocumentmatch pdm
                        INNER JOIN finance_finantialdocument fd1
                            ON fd1.id = pdm.debit_document_id
                        INNER JOIN finance_finantialdocument fd2
                            ON fd2.id = pdm.credit_document_id
                    WHERE fd1.id = pd.finantialdocument_ptr_id
                        AND fd2.status = fd1.status)
                """, [STATUS_READY])
        finally:
            cursor.close()


class ProviderCreditDocument(ProviderDocument):
    class Meta:
        verbose_name = 'Provider Credit Document'
        verbose_name_plural = 'Providers Credits Documents'

    def fix_matched_amount(self):
        cursor = connection.cursor()
        try:
            cursor.execute("""
                UPDATE finance_providerdocument pd SET pd.matched_amount = (
                    SELECT COALESCE(
                        CASE WHEN fd1.status != %s THEN 0 ELSE SUM(pdm.matched_amount) END,
                        0)
                    FROM finance_providerdocumentmatch pdm
                        INNER JOIN finance_finantialdocument fd1
                            ON fd1.id = pdm.credit_document_id
                        INNER JOIN finance_finantialdocument fd2
                            ON fd2.id = pdm.debit_document_id
                    WHERE fd1.id = pd.finantialdocument_ptr_id
                        AND fd2.status = fd1.status)
                WHERE pd.finantialdocument_ptr_id = %s
                """, [STATUS_READY, self.pk])
            self.refresh_from_db()
        finally:
            cursor.close()

    @classmethod
    def fix_matched_amounts(cls):
        cursor = connection.cursor()
        try:
            cursor.execute("""
                UPDATE finance_providerdocument pd SET pd.matched_amount = (
                    SELECT COALESCE(
                        CASE WHEN fd1.status != %s THEN 0 ELSE SUM(pdm.matched_amount) END,
                        0)
                    FROM finance_providerdocumentmatch pdm
                        INNER JOIN finance_finantialdocument fd1
                            ON fd1.id = pdm.credit_document_id
                        INNER JOIN finance_finantialdocument fd2
                            ON fd2.id = pdm.debit_document_id
                    WHERE fd1.id = pd.finantialdocument_ptr_id
                        AND fd2.status = fd1.status)
                """, [STATUS_READY])
        finally:
            cursor.close()


class ProviderInvoice(ProviderDebitDocument):
    class Meta:
        verbose_name = 'Provider Invoice'
        verbose_name_plural = 'Providers Invoices'

    def fill_data(self):
        self.document_type = DOC_TYPE_PROVIDER_INVOICE
        provider = Provider.objects.get(pk=self.provider_id)
        self.name = '%s - Provider Invoice from %s for %s %s' % (
            self.date, provider, self.amount, self.get_currency_display())

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        self.fill_data()
        # Call the real save() method
        super(ProviderInvoice, self).save(force_insert, force_update, using, update_fields)


class ProviderPayment(ProviderCreditDocument, AccountingDocument):
    class Meta:
        verbose_name = 'Provider Payment'
        verbose_name_plural = 'Providers Payments'

    def fill_data(self):
        self.document_type = DOC_TYPE_PROVIDER_PAYMENT
        provider = Provider.objects.get(pk=self.provider_id)
        self.name = '%s - Provider Payment from %s for %s %s' % (
            self.date, provider, self.amount, self.get_currency_display())

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        self.fill_data()
        # Call the real save() method
        super(ProviderPayment, self).save(force_insert, force_update, using, update_fields)


class ProviderDiscount(ProviderCreditDocument):
    class Meta:
        verbose_name = 'Provider Discount'
        verbose_name_plural = 'Providers Discounts'

    def fill_data(self):
        self.document_type = DOC_TYPE_PROVIDER_DISCOUNT
        provider = Provider.objects.get(pk=self.provider_id)
        self.name = '%s - Provider Discount from %s for %s %s' % (
            self.date, provider, self.amount, self.get_currency_display())

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        self.fill_data()
        # Call the real save() method
        super(ProviderDiscount, self).save(force_insert, force_update, using, update_fields)


class ProviderDevolution(ProviderDebitDocument, AccountingDocument):
    class Meta:
        verbose_name = 'Provider Devolution'
        verbose_name_plural = 'Providers Devolutions'

    def fill_data(self):
        self.document_type = DOC_TYPE_PROVIDER_DEVOLUTION
        provider = Provider.objects.get(pk=self.provider_id)
        self.name = '%s - Provider Devolution from %s for %s %s' % (
            self.date, provider, self.amount, self.get_currency_display())

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        self.fill_data()
        # Call the real save() method
        super(ProviderDevolution, self).save(force_insert, force_update, using, update_fields)


class ProviderDocumentMatch(models.Model):
    class Meta:
        verbose_name = 'Provider Match'
        verbose_name_plural = 'Providers Matches'
        unique_together = (('credit_document', 'debit_document',),)
    credit_document = models.ForeignKey(ProviderCreditDocument)
    debit_document = models.ForeignKey(ProviderDebitDocument)
    matched_amount = models.DecimalField(max_digits=10, decimal_places=2)
