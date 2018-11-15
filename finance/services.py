"""
Finance Service
"""

from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from accounting.constants import (
    MOVEMENT_TYPE_INPUT, MOVEMENT_TYPE_OUTPUT, ERROR_DIFFERENT_CURRENCY, ERROR_SAME_CURRENCY,
    ERROR_MODEL_NOT_FOUND, ERROR_MODEL, ERROR_AMOUNT_REQUIRED)
from accounting.models import Account
from accounting.services import AccountingService

from finance.constants import (
    STATUS_READY,
    ERROR_MATCH_STATUS, ERROR_NOT_READY, ERROR_MATCH_AMOUNT, ERROR_MATCH_ACCOUNT,
    ERROR_MATCH_CURRENCY, ERROR_MATCH_LOAN_ENTITY, ERROR_MATCH_LOAN_ACCOUNT,
    ERROR_MATCH_AGENCY, ERROR_MATCH_PROVIDER, ERROR_MATCH_OVERMATCHED,
    ERROR_INVALID_MATCH, ERROR_MATCH_WITHOUT_AMOUNT, ERROR_DIFFERENT_DOCUMENTS)
from finance.models import (
    Deposit, Withdraw, CurrencyExchange, Transfer,
    LoanEntityDeposit, LoanEntityWithdraw, LoanEntityMatch, LoanEntityCurrency,
    LoanAccountDeposit, LoanAccountWithdraw, LoanAccountMatch, LoanAccount,
    AgencyInvoice, AgencyPayment, AgencyDevolution, AgencyDiscount, AgencyDocumentMatch,
    AgencyCreditDocument, AgencyDebitDocument, AgencyCurrency,
    ProviderInvoice, ProviderPayment, ProviderDevolution, ProviderDiscount, ProviderDocumentMatch,
    ProviderCreditDocument, ProviderDebitDocument, ProviderCurrency,
    FinantialDocumentHistory, AccountingDocumentHistory)


MATCH_TYPE_ENTITY = 1
MATCH_TYPE_ACCOUNT = 2
MATCH_TYPE_AGENCY = 3
MATCH_TYPE_PROVIDER = 4

class FinanceService(object):
    """
    Finance Service
    """

    @classmethod
    def save_deposit(cls, user, deposit):
        """
        Saves Deposit
        """
        with transaction.atomic(savepoint=False):
            # load and lock account
            account = cls._load_locked_model_object(
                pk=deposit.account_id, model_class=Account, allow_empty_pk=False)
            db_deposit = cls._load_locked_model_object(
                pk=deposit.pk, model_class=Deposit)
            # manage saving
            return cls._document_save(
                user=user,
                document=deposit,
                db_document=db_deposit,
                account=account,
                movement_type=MOVEMENT_TYPE_INPUT)

    @classmethod
    def save_withdraw(cls, user, withdraw):
        """
        Saves Withdraw
        """
        with transaction.atomic(savepoint=False):
            # load and lock account
            account = cls._load_locked_model_object(
                pk=withdraw.account_id, model_class=Account, allow_empty_pk=False)
            db_withdraw = cls._load_locked_model_object(
                pk=withdraw.pk, model_class=Withdraw)
            # manage saving
            return cls._document_save(
                user=user,
                document=withdraw,
                db_document=db_withdraw,
                account=account,
                movement_type=MOVEMENT_TYPE_OUTPUT)

    @classmethod
    def save_transfer(cls, user, transfer):
        """
        Saves Transfer
        """
        with transaction.atomic(savepoint=False):
            # load and lock accounts
            account = cls._load_locked_model_object(
                pk=transfer.account_id, model_class=Account, allow_empty_pk=False)
            other_account = cls._load_locked_model_object(
                pk=transfer.transfer_account_id, model_class=Account,
                allow_empty_pk=False)
            # verify accounts
            if account.currency != other_account.currency:
                raise ValidationError(ERROR_DIFFERENT_CURRENCY % (account, other_account))
            db_transfer = cls._load_locked_model_object(
                pk=transfer.pk, model_class=Transfer)
            # define db others
            db_other_account_id = None
            if db_transfer:
                db_other_account_id = db_transfer.transfer_account_id
            # manage saving
            return cls._document_save(
                user=user,
                document=transfer,
                db_document=db_transfer,
                account=account,
                movement_type=MOVEMENT_TYPE_INPUT,
                other_account=other_account,
                db_other_account_id=db_other_account_id)

    @classmethod
    def save_currency_exchange(cls, user, currency_exchange):
        """
        Saves Currency Exchange
        """
        with transaction.atomic(savepoint=False):
            # load and lock account
            account = cls._load_locked_model_object(
                pk=currency_exchange.account_id, model_class=Account, allow_empty_pk=False)
            other_account = cls._load_locked_model_object(
                pk=currency_exchange.exchange_account_id, model_class=Account,
                allow_empty_pk=False)
            # verify accounts
            if account.currency == other_account.currency:
                raise ValidationError(ERROR_SAME_CURRENCY % (account, other_account))
            db_exchange = cls._load_locked_model_object(
                pk=currency_exchange.pk, model_class=CurrencyExchange)
            # define db others
            db_other_account_id = None
            db_other_amount = None
            if db_exchange:
                db_other_account_id = db_exchange.exchange_account_id
                db_other_amount = db_exchange.exchange_amount
            # manage saving
            return cls._document_save(
                user=user,
                document=currency_exchange,
                db_document=db_exchange,
                account=account,
                movement_type=MOVEMENT_TYPE_INPUT,
                other_account=other_account,
                db_other_account_id=db_other_account_id,
                other_amount=currency_exchange.exchange_amount,
                db_other_amount=db_other_amount)

    @classmethod
    def save_loan_entity_deposit(cls, user, loan_entity_deposit):
        """
        Saves Loan Entity Deposit
        """
        with transaction.atomic(savepoint=False):
            # load and lock account
            account = cls._load_locked_model_object(
                pk=loan_entity_deposit.account_id, model_class=Account, allow_empty_pk=False)
            db_loan_entity_deposit = cls._load_locked_model_object(
                pk=loan_entity_deposit.pk, model_class=LoanEntityDeposit)
            # validate matches on status, currency or amount change
            cls._validate_matches(
                document=loan_entity_deposit,
                db_document=db_loan_entity_deposit,
                match_type=MATCH_TYPE_ENTITY)
            # manage saving
            document = cls._document_save(
                user=user,
                document=loan_entity_deposit,
                db_document=db_loan_entity_deposit,
                account=account,
                movement_type=MOVEMENT_TYPE_INPUT)
            # loan_entity currency credit_amount
            cls._process_summary_amount(
                document=document,
                db_document=db_loan_entity_deposit,
                is_credit=True,
                match_type=MATCH_TYPE_ENTITY)
            return document

    @classmethod
    def save_loan_entity_withdraw(cls, user, loan_entity_withdraw):
        """
        Saves Loan Withdraw
        """
        with transaction.atomic(savepoint=False):
            # load and lock account
            account = cls._load_locked_model_object(
                pk=loan_entity_withdraw.account_id, model_class=Account, allow_empty_pk=False)
            db_loan_entity_withdraw = cls._load_locked_model_object(
                pk=loan_entity_withdraw.pk, model_class=LoanEntityWithdraw)
            # validate matches on status, currency or amount change
            cls._validate_matches(
                document=loan_entity_withdraw,
                db_document=db_loan_entity_withdraw,
                match_type=MATCH_TYPE_ENTITY)
            # manage saving
            document = cls._document_save(
                user=user,
                document=loan_entity_withdraw,
                db_document=db_loan_entity_withdraw,
                account=account,
                movement_type=MOVEMENT_TYPE_OUTPUT)
            # loan_entity currency debit_amount
            cls._process_summary_amount(
                document=document,
                db_document=db_loan_entity_withdraw,
                is_credit=False,
                match_type=MATCH_TYPE_ENTITY)
            return document

    @classmethod
    def match_loan_entity_document(cls, parent, matches, is_credit):

        current_new_matches = list(matches)
        current_db_matches = list(parent.loanentitymatch_set.all())

        decrease_matches = list()
        increase_matches = list()
        add_matches = list()

        total = 0

        new_matches = list(current_new_matches)
        for new_match in new_matches:
            total += new_match['match_amount']
            found = False
            db_matches = list(current_db_matches)
            for db_match in db_matches:
                if new_match['match_id'] and new_match['match_id'] == db_match.pk:
                    found = True
                    current_new_matches.remove(new_match)
                    current_db_matches.remove(db_match)
                    if new_match.match_amount < db_match.matched_amount:
                        db_match.matched_amount = new_match.match_amount
                        decrease_matches.append(db_match)
                    if new_match.match_amount > db_match.matched_amount:
                        db_match.matched_amount = new_match.match_amount
                        increase_matches.append(db_match)
                    break
            if not found:
                add_matches.append(new_match)
                current_new_matches.remove(new_match)

        # validation for total matched against document amount
        if total > parent.amount:
            raise ValidationError('Matched amount %s bigger than amount %s' % (total, parent.amount))

        # in current db matches are matches not found, for removing
        db_matches = list(current_db_matches)
        for db_match in current_db_matches:
            # remove db matches not included in matches
            cls.delete_loan_entity_match(db_match.pk)

        # save db matches that match amount decreased
        for match in decrease_matches:
            cls.save_loan_entity_match(db_match)

        # save db matches that match amount increased
        for match in increase_matches:
            cls.save_loan_entity_match(db_match)

        # save db matches that are new
        for match in add_matches:
            child = match['child']
            if is_credit:
                child_withdraw = LoanEntityWithdraw.objects.get(pk=child.pk)
                new_db_match = LoanEntityMatch(
                    loan_entity_deposit=parent,
                    loan_entity_withdraw=child_withdraw,
                    matched_amount=match['match_amount'],
                )
            else:
                child_deposit = LoanEntityDeposit.objects.get(pk=child.pk)
                new_db_match = LoanEntityMatch(
                    loan_entity_deposit=child_deposit,
                    loan_entity_withdraw=parent,
                    matched_amount=match['match_amount'],
                )
            cls.save_loan_entity_match(new_db_match)

    @classmethod
    def save_loan_entity_match(cls, loan_entity_match):
        """
        Save Loan Entity Match
        """
        with transaction.atomic(savepoint=False):
            if not loan_entity_match.pk:
                # new match
                # process match
                return cls._process_match(
                    document_match=loan_entity_match,
                    db_document_match=None,
                    match_type=MATCH_TYPE_ENTITY)
            else:
                # db match
                # get db loan match
                db_loan_entity_match = LoanEntityMatch.objects.get(pk=loan_entity_match.pk)
                if not db_loan_entity_match:
                    raise ValidationError(ERROR_MODEL_NOT_FOUND % 'Loan Entity Match')
                # process match
                return cls._process_match(
                    document_match=loan_entity_match,
                    db_document_match=db_loan_entity_match,
                    match_type=MATCH_TYPE_ENTITY)

    @classmethod
    def delete_loan_entity_match(cls, loan_entity_match_id):
        """
        Delete Loan Entity Match
        """
        with transaction.atomic(savepoint=False):
            # get loan match
            loan_entity_match = LoanEntityMatch.objects.get(pk=loan_entity_match_id)
            if not loan_entity_match:
                raise ValidationError(ERROR_MODEL_NOT_FOUND % 'Loan Entity Match')
            matched_amount = loan_entity_match.matched_amount
            # obtain related documents and update matched_amount
            loan_entity_deposit = cls._load_locked_model_object(
                pk=loan_entity_match.loan_entity_deposit_id, model_class=LoanEntityDeposit)
            loan_entity_withdraw = cls._load_locked_model_object(
                pk=loan_entity_match.loan_entity_withdraw_id, model_class=LoanEntityWithdraw)
            # delete loan_match
            loan_entity_match.delete()
            # documents matched_amount
            loan_entity_deposit.fix_matched_amount()
            loan_entity_withdraw.fix_matched_amount()
            # loan_entity matched_amount
            if loan_entity_deposit.loan_entity_id == loan_entity_withdraw.loan_entity_id:
                cls._process_matched_amount(
                    related_id=loan_entity_deposit.loan_entity_id,
                    currency=loan_entity_deposit.currency,
                    delta_amount=-matched_amount,
                    match_type=MATCH_TYPE_ENTITY)

    @classmethod
    def save_loan_account_deposit(cls, user, loan_account_deposit):
        """
        Saves Loan Account Deposit
        """
        with transaction.atomic(savepoint=False):
            # load and lock accounts
            account = cls._load_locked_model_object(
                pk=loan_account_deposit.account_id, model_class=Account, allow_empty_pk=False)
            other_account = cls._load_locked_model_object(
                pk=loan_account_deposit.loan_account.account_id, model_class=Account,
                allow_empty_pk=False)
            # verify accounts
            if account.currency != other_account.currency:
                raise ValidationError(ERROR_DIFFERENT_CURRENCY % (account, other_account))
            db_loan_account_deposit = cls._load_locked_model_object(
                pk=loan_account_deposit.pk, model_class=LoanAccountDeposit)
            # define db others
            db_other_account_id = None
            if db_loan_account_deposit:
                db_other_account_id = db_loan_account_deposit.loan_account.account_id
            # validate matches on status, currency or amount change
            cls._validate_matches(
                document=loan_account_deposit,
                db_document=db_loan_account_deposit,
                match_type=MATCH_TYPE_ACCOUNT)
            # manage saving
            document = cls._document_save(
                user=user,
                document=loan_account_deposit,
                db_document=db_loan_account_deposit,
                account=account,
                movement_type=MOVEMENT_TYPE_INPUT,
                other_account=other_account,
                db_other_account_id=db_other_account_id)
            # loan_account credit_amount
            cls._process_summary_amount(
                document=document,
                db_document=db_loan_account_deposit,
                is_credit=True,
                match_type=MATCH_TYPE_ACCOUNT)
            return document

    @classmethod
    def save_loan_account_withdraw(cls, user, loan_account_withdraw):
        """
        Saves Loan Account Withdraw
        """
        with transaction.atomic(savepoint=False):
            # load and lock accounts
            account = cls._load_locked_model_object(
                pk=loan_account_withdraw.account_id, model_class=Account, allow_empty_pk=False)
            other_account = cls._load_locked_model_object(
                pk=loan_account_withdraw.loan_account.account_id, model_class=Account,
                allow_empty_pk=False)
            # verify accounts
            if account.currency != other_account.currency:
                raise ValidationError(ERROR_DIFFERENT_CURRENCY % (account, other_account))
            db_loan_account_withdraw = cls._load_locked_model_object(
                pk=loan_account_withdraw.pk, model_class=LoanAccountWithdraw)
            # define db others
            db_other_account_id = None
            if db_loan_account_withdraw:
                db_other_account_id = db_loan_account_withdraw.loan_account.account_id
            # validate matches on status, currency or amount change
            cls._validate_matches(
                document=loan_account_withdraw,
                db_document=db_loan_account_withdraw,
                match_type=MATCH_TYPE_ACCOUNT)
            # manage saving
            document = cls._document_save(
                user=user,
                document=loan_account_withdraw,
                db_document=db_loan_account_withdraw,
                account=account,
                movement_type=MOVEMENT_TYPE_OUTPUT,
                other_account=other_account,
                db_other_account_id=db_other_account_id)
            # loan_account debit_amount
            cls._process_summary_amount(
                document=document,
                db_document=db_loan_account_withdraw,
                is_credit=False,
                match_type=MATCH_TYPE_ACCOUNT)
            return document

    @classmethod
    def match_loan_account_document(cls, parent, matches, is_credit):

        current_new_matches = list(matches)
        current_db_matches = list(parent.loanaccountmatch_set.all())

        decrease_matches = list()
        increase_matches = list()
        add_matches = list()

        total = 0

        new_matches = list(current_new_matches)
        for new_match in new_matches:
            total += new_match['match_amount']
            found = False
            db_matches = list(current_db_matches)
            for db_match in db_matches:
                if new_match['match_id'] and new_match['match_id'] == db_match.pk:
                    found = True
                    current_new_matches.remove(new_match)
                    current_db_matches.remove(db_match)
                    if new_match.match_amount < db_match.matched_amount:
                        db_match.matched_amount = new_match.match_amount
                        decrease_matches.append(db_match)
                    if new_match.match_amount > db_match.matched_amount:
                        db_match.matched_amount = new_match.match_amount
                        increase_matches.append(db_match)
                    break
            if not found:
                add_matches.append(new_match)
                current_new_matches.remove(new_match)

        # validation for total matched against document amount
        if total > parent.amount:
            raise ValidationError('Matched amount %s bigger than amount %s' % (total, parent.amount))

        # in current db matches are matches not found, for removing
        db_matches = list(current_db_matches)
        for db_match in current_db_matches:
            # remove db matches not included in matches
            cls.delete_loan_account_match(db_match.pk)

        # save db matches that match amount decreased
        for match in decrease_matches:
            cls.save_loan_account_match(db_match)

        # save db matches that match amount increased
        for match in increase_matches:
            cls.save_loan_account_match(db_match)

        # save db matches that are new
        for match in add_matches:
            child = match['child']
            if is_credit:
                child_withdraw = LoanAccountWithdraw.objects.get(pk=child.pk)
                new_db_match = LoanAccountMatch(
                    loan_account_deposit=parent,
                    loan_account_withdraw=child_withdraw,
                    matched_amount=match['match_amount'],
                )
            else:
                child_deposit = LoanAccountDeposit.objects.get(pk=child.pk)
                new_db_match = LoanAccountMatch(
                    loan_account_deposit=child_deposit,
                    loan_account_withdraw=parent,
                    matched_amount=match['match_amount'],
                )
            cls.save_loan_account_match(new_db_match)

    @classmethod
    def save_loan_account_match(cls, loan_account_match):
        """
        Save Loan Account Match
        """
        with transaction.atomic(savepoint=False):
            if not loan_account_match.pk:
                # new match
                # process match
                return cls._process_match(
                    document_match=loan_account_match,
                    db_document_match=None,
                    match_type=MATCH_TYPE_ACCOUNT)
            else:
                # db match
                # get db loan match
                db_loan_account_match = LoanAccountMatch.objects.get(pk=loan_account_match.pk)
                if not db_loan_account_match:
                    raise ValidationError(ERROR_MODEL_NOT_FOUND % 'Loan Account Match')
                # process match
                return cls._process_match(
                    document_match=loan_account_match,
                    db_document_match=db_loan_account_match,
                    match_type=MATCH_TYPE_ACCOUNT)

    @classmethod
    def delete_loan_account_match(cls, loan_account_match_id):
        """
        Delete Loan Account Match
        """
        with transaction.atomic(savepoint=False):
            # get loan account match
            loan_account_match = LoanAccountMatch.objects.get(pk=loan_account_match_id)
            matched_amount = loan_account_match.matched_amount
            if not loan_account_match:
                raise ValidationError(ERROR_MODEL_NOT_FOUND % 'Loan Account Match')
            # obtain related documents and update matched_amount
            loan_account_deposit = cls._load_locked_model_object(
                pk=loan_account_match.loan_account_deposit_id, model_class=LoanAccountDeposit)
            loan_account_withdraw = cls._load_locked_model_object(
                pk=loan_account_match.loan_account_withdraw_id, model_class=LoanAccountWithdraw)
            # delete loan account match
            loan_account_match.delete()
            # documents matched_amount
            loan_account_deposit.fix_matched_amount()
            loan_account_withdraw.fix_matched_amount()
            # loan_account matched_amount
            if loan_account_deposit.loan_account_id == loan_account_withdraw.loan_account_id:
                cls._process_matched_amount(
                    related_id=loan_account_deposit.loan_account_id,
                    currency=loan_account_deposit.currency,
                    delta_amount=-matched_amount,
                    match_type=MATCH_TYPE_ACCOUNT)

    @classmethod
    def save_agency_invoice(cls, user, agency_invoice):
        """
        Saves Agency Invoice
        """
        with transaction.atomic(savepoint=False):
            db_agency_invoice = cls._load_locked_model_object(
                pk=agency_invoice.pk, model_class=AgencyInvoice)
            # validate matches on status, currency or amount change
            cls._validate_matches(
                document=agency_invoice,
                db_document=db_agency_invoice,
                match_type=MATCH_TYPE_AGENCY)
            # manage saving
            document = cls._document_save(
                user=user,
                document=agency_invoice,
                db_document=db_agency_invoice)
            # agency currency debit_amount
            cls._process_summary_amount(
                document=document,
                db_document=db_agency_invoice,
                is_credit=False,
                match_type=MATCH_TYPE_AGENCY)
            return document


    @classmethod
    def save_agency_payment(cls, user, agency_payment):
        """
        Saves Agency Payment
        """
        with transaction.atomic(savepoint=False):
            # load and lock account
            account = cls._load_locked_model_object(
                pk=agency_payment.account_id, model_class=Account, allow_empty_pk=False)
            db_agency_payment = cls._load_locked_model_object(
                pk=agency_payment.pk, model_class=AgencyPayment)
            # validate matches on status, currency or amount change
            cls._validate_matches(
                document=agency_payment,
                db_document=db_agency_payment,
                match_type=MATCH_TYPE_AGENCY)
            # manage saving
            document = cls._document_save(
                user=user,
                document=agency_payment,
                db_document=db_agency_payment,
                account=account,
                movement_type=MOVEMENT_TYPE_INPUT)
            # agency currency credit_amount
            cls._process_summary_amount(
                document=document,
                db_document=db_agency_payment,
                is_credit=True,
                match_type=MATCH_TYPE_AGENCY)
            return document

    @classmethod
    def save_agency_devolution(cls, user, agency_devolution):
        """
        Saves Agency Devolution
        """
        with transaction.atomic(savepoint=False):
            # load and lock account
            account = cls._load_locked_model_object(
                pk=agency_devolution.account_id, model_class=Account, allow_empty_pk=False)
            db_agency_devolution = cls._load_locked_model_object(
                pk=agency_devolution.pk, model_class=AgencyDevolution)
            # validate matches on status, currency or amount change
            cls._validate_matches(
                document=agency_devolution,
                db_document=db_agency_devolution,
                match_type=MATCH_TYPE_AGENCY)
            # manage saving
            document = cls._document_save(
                user=user,
                document=agency_devolution,
                db_document=db_agency_devolution,
                account=account,
                movement_type=MOVEMENT_TYPE_OUTPUT)
            # agency currency debit_amount
            cls._process_summary_amount(
                document=document,
                db_document=db_agency_devolution,
                is_credit=False,
                match_type=MATCH_TYPE_AGENCY)
            return document

    @classmethod
    def save_agency_discount(cls, user, agency_discount):
        """
        Saves Agency Discount
        """
        with transaction.atomic(savepoint=False):
            db_agency_discount = cls._load_locked_model_object(
                pk=agency_discount.pk, model_class=AgencyDiscount)
            # validate matches on status, currency or amount change
            cls._validate_matches(
                document=agency_discount,
                db_document=db_agency_discount,
                match_type=MATCH_TYPE_AGENCY)
            # manage saving
            document = cls._document_save(
                user=user,
                document=agency_discount,
                db_document=db_agency_discount)
            # agency currency credit_amount
            cls._process_summary_amount(
                document=document,
                db_document=db_agency_discount,
                is_credit=True,
                match_type=MATCH_TYPE_AGENCY)
            return document

    @classmethod
    def match_agency_document(cls, parent, matches, is_credit):

        current_new_matches = list(matches)
        if is_credit:
            parent = parent.agencycreditdocument_ptr
        else:
            parent = parent.agencydebitdocument_ptr
        current_db_matches = list(parent.agencymatch_set.all())

        decrease_matches = list()
        increase_matches = list()
        add_matches = list()

        total = 0

        new_matches = list(current_new_matches)
        for new_match in new_matches:
            total += new_match['match_amount']
            found = False
            db_matches = list(current_db_matches)
            for db_match in db_matches:
                if new_match['match_id'] and new_match['match_id'] == db_match.pk:
                    found = True
                    current_new_matches.remove(new_match)
                    current_db_matches.remove(db_match)
                    if new_match.match_amount < db_match.matched_amount:
                        db_match.matched_amount = new_match.match_amount
                        decrease_matches.append(db_match)
                    if new_match.match_amount > db_match.matched_amount:
                        db_match.matched_amount = new_match.match_amount
                        increase_matches.append(db_match)
                    break
            if not found:
                add_matches.append(new_match)
                current_new_matches.remove(new_match)

        # validation for total matched against document amount
        if total > parent.amount:
            raise ValidationError('Matched amount %s bigger than amount %s' % (total, parent.amount))

        # in current db matches are matches not found, for removing
        db_matches = list(current_db_matches)
        for db_match in current_db_matches:
            # remove db matches not included in matches
            cls.delete_agency_match(db_match.pk)

        # save db matches that match amount decreased
        for match in decrease_matches:
            cls.save_agency_match(db_match)

        # save db matches that match amount increased
        for match in increase_matches:
            cls.save_agency_match(db_match)

        # save db matches that are new
        for match in add_matches:
            child = match['child']
            if is_credit:
                child_debit = AgencyDebitDocument.objects.get(pk=child.pk)
                new_db_match = AgencyDocumentMatch(
                    credit_document=parent,
                    debit_document=child_debit,
                    matched_amount=match['match_amount'],
                )
            else:
                child_credit = AgencyCreditDocument.objects.get(pk=child.pk)
                new_db_match = AgencyDocumentMatch(
                    credit_document=child_credit,
                    debit_document=parent,
                    matched_amount=match['match_amount'],
                )
            cls.save_agency_match(new_db_match)

    @classmethod
    def save_agency_match(cls, agency_match):
        """
        Save Agency Match
        """
        with transaction.atomic(savepoint=False):
            if not agency_match.pk:
                # new match
                # process match
                return cls._process_match(
                    document_match=agency_match,
                    db_document_match=None,
                    match_type=MATCH_TYPE_AGENCY)
            else:
                # db match
                # get db loan match
                db_agency_match = AgencyDocumentMatch.objects.get(pk=agency_match.pk)
                if not db_agency_match:
                    raise ValidationError(ERROR_MODEL_NOT_FOUND % 'Agency Document Match')
                # process match
                return cls._process_match(
                    document_match=agency_match,
                    db_document_match=db_agency_match,
                    match_type=MATCH_TYPE_AGENCY)

    @classmethod
    def delete_agency_match(cls, agency_match_id):
        """
        Delete Agency Match
        """
        with transaction.atomic(savepoint=False):
            # get agency match
            agency_match = AgencyDocumentMatch.objects.get(pk=agency_match_id)
            if not agency_match:
                raise ValidationError(ERROR_MODEL_NOT_FOUND % 'Agency Match')
            matched_amount = agency_match.matched_amount
            # obtain related documents and update matched_amount
            credit_document = cls._load_locked_model_object(
                pk=agency_match.credit_document_id, model_class=AgencyCreditDocument)
            debit_document = cls._load_locked_model_object(
                pk=agency_match.debit_document_id, model_class=AgencyDebitDocument)
            # delete agency_match
            agency_match.delete()
            # documents matched_amount
            credit_document.fix_matched_amount()
            debit_document.fix_matched_amount()
            # agency currency matched_amount
            if credit_document.agency_id == debit_document.agency_id:
                cls._process_matched_amount(
                    related_id=credit_document.agency_id,
                    currency=credit_document.currency,
                    delta_amount=-matched_amount,
                    match_type=MATCH_TYPE_AGENCY)

    @classmethod
    def save_provider_invoice(cls, user, provider_invoice):
        """
        Saves Provider Invoice
        """
        with transaction.atomic(savepoint=False):
            db_provider_invoice = cls._load_locked_model_object(
                pk=provider_invoice.pk, model_class=ProviderInvoice)
            # validate matches on status, currency or amount change
            cls._validate_matches(
                document=provider_invoice,
                db_document=db_provider_invoice,
                match_type=MATCH_TYPE_PROVIDER)
            # manage saving
            document = cls._document_save(
                user=user,
                document=provider_invoice,
                db_document=db_provider_invoice)
            # provider currency credit_amount
            cls._process_summary_amount(
                document=document,
                db_document=db_provider_invoice,
                is_credit=False,
                match_type=MATCH_TYPE_PROVIDER)
            return document


    @classmethod
    def save_provider_payment(cls, user, provider_payment):
        """
        Saves Provider Payment
        """
        with transaction.atomic(savepoint=False):
            # load and lock account
            account = cls._load_locked_model_object(
                pk=provider_payment.account_id, model_class=Account, allow_empty_pk=False)
            db_provider_payment = cls._load_locked_model_object(
                pk=provider_payment.pk, model_class=ProviderPayment)
            # validate matches on status, currency or amount change
            cls._validate_matches(
                document=provider_payment,
                db_document=db_provider_payment,
                match_type=MATCH_TYPE_PROVIDER)
            # manage saving
            document = cls._document_save(
                user=user,
                document=provider_payment,
                db_document=db_provider_payment,
                account=account,
                movement_type=MOVEMENT_TYPE_OUTPUT)
            # provider currency debit_amount
            cls._process_summary_amount(
                document=document,
                db_document=db_provider_payment,
                is_credit=True,
                match_type=MATCH_TYPE_PROVIDER)
            return document

    @classmethod
    def save_provider_discount(cls, user, provider_discount):
        """
        Saves Provider Discount
        """
        with transaction.atomic(savepoint=False):
            db_provider_discount = cls._load_locked_model_object(
                pk=provider_discount.pk, model_class=ProviderDiscount)
            # validate matches on status, currency or amount change
            cls._validate_matches(
                document=provider_discount,
                db_document=db_provider_discount,
                match_type=MATCH_TYPE_PROVIDER)
            # manage saving
            document = cls._document_save(
                user=user,
                document=provider_discount,
                db_document=db_provider_discount)
            # provider currency debit_amount
            cls._process_summary_amount(
                document=document,
                db_document=db_provider_discount,
                is_credit=True,
                match_type=MATCH_TYPE_PROVIDER)
            return document

    @classmethod
    def save_provider_devolution(cls, user, provider_devolution):
        """
        Saves Provider Devolution
        """
        with transaction.atomic(savepoint=False):
            # load and lock account
            account = cls._load_locked_model_object(
                pk=provider_devolution.account_id, model_class=Account, allow_empty_pk=False)
            db_provider_devolution = cls._load_locked_model_object(
                pk=provider_devolution.pk, model_class=ProviderDevolution)
            # validate matches on status, currency or amount change
            cls._validate_matches(
                document=provider_devolution,
                db_document=db_provider_devolution,
                match_type=MATCH_TYPE_PROVIDER)
            # manage saving
            document = cls._document_save(
                user=user,
                document=provider_devolution,
                db_document=db_provider_devolution,
                account=account,
                movement_type=MOVEMENT_TYPE_INPUT)
            # provider currency credit_amount
            cls._process_summary_amount(
                document=document,
                db_document=db_provider_devolution,
                is_credit=False,
                match_type=MATCH_TYPE_PROVIDER)
            return document

    @classmethod
    def match_provider_document(cls, parent, matches, is_credit):

        current_new_matches = list(matches)
        if is_credit:
            parent = parent.providercreditdocument_ptr
        else:
            parent = parent.providerdebitdocument_ptr
        current_db_matches = list(parent.providerdocumentmatch_set.all())

        decrease_matches = list()
        increase_matches = list()
        add_matches = list()

        total = 0

        new_matches = list(current_new_matches)
        for new_match in new_matches:
            total += new_match['match_amount']
            found = False
            db_matches = list(current_db_matches)
            for db_match in db_matches:
                if new_match['match_id'] and new_match['match_id'] == db_match.pk:
                    found = True
                    current_new_matches.remove(new_match)
                    current_db_matches.remove(db_match)
                    if new_match.match_amount < db_match.matched_amount:
                        db_match.matched_amount = new_match.match_amount
                        decrease_matches.append(db_match)
                    if new_match.match_amount > db_match.matched_amount:
                        db_match.matched_amount = new_match.match_amount
                        increase_matches.append(db_match)
                    break
            if not found:
                add_matches.append(new_match)
                current_new_matches.remove(new_match)

        # validation for total matched against document amount
        if total > parent.amount:
            raise ValidationError('Matched amount %s bigger than amount %s' % (total, parent.amount))

        # in current db matches are matches not found, for removing
        db_matches = list(current_db_matches)
        for db_match in current_db_matches:
            # remove db matches not included in matches
            cls.delete_provider_match(db_match.pk)

        # save db matches that match amount decreased
        for match in decrease_matches:
            cls.save_provider_match(db_match)

        # save db matches that match amount increased
        for match in increase_matches:
            cls.save_provider_match(db_match)

        # save db matches that are new
        for match in add_matches:
            child = match['child']
            if is_credit:
                child_debit = ProviderDebitDocument.objects.get(pk=child.pk)
                new_db_match = ProviderDocumentMatch(
                    credit_document=parent,
                    debit_document=child_debit,
                    matched_amount=match['match_amount'],
                )
            else:
                child_credit = ProviderCreditDocument.objects.get(pk=child.pk)
                new_db_match = ProviderDocumentMatch(
                    credit_document=child_credit,
                    debit_document=parent,
                    matched_amount=match['match_amount'],
                )
            cls.save_provider_match(new_db_match)

    @classmethod
    def save_provider_match(cls, provider_match):
        """
        Save Provider Match
        """
        with transaction.atomic(savepoint=False):
            if not provider_match.pk:
                # new match
                # process match
                return cls._process_match(
                    document_match=provider_match,
                    db_document_match=None,
                    match_type=MATCH_TYPE_PROVIDER)
            else:
                # db match
                # get db document match
                db_provider_match = ProviderDocumentMatch.objects.get(pk=provider_match.pk)
                if not db_provider_match:
                    raise ValidationError(ERROR_MODEL_NOT_FOUND % 'Provider Document Match')
                # process match
                return cls._process_match(
                    document_match=provider_match,
                    db_document_match=db_provider_match,
                    match_type=MATCH_TYPE_PROVIDER)

    @classmethod
    def delete_provider_match(cls, provider_match_id):
        """
        Delete Provider Match
        """
        with transaction.atomic(savepoint=False):
            # get provider match
            provider_match = ProviderDocumentMatch.objects.get(pk=provider_match_id)
            if not provider_match:
                raise ValidationError(ERROR_MODEL_NOT_FOUND % 'Provider Match')
            matched_amount = provider_match.matched_amount
            # obtain related documents and update matched_amount
            credit_document = cls._load_locked_model_object(
                pk=provider_match.credit_document_id, model_class=ProviderCreditDocument)
            debit_document = cls._load_locked_model_object(
                pk=provider_match.debit_document_id, model_class=ProviderDebitDocument)
            # delete provider_match
            provider_match.delete()
            # documents matched_amount
            credit_document.fix_matched_amount()
            debit_document.fix_matched_amount()
            # provider matched_amount
            if credit_document.provider_id == debit_document.provider_id:
                cls._process_matched_amount(
                    related_id=credit_document.provider_id,
                    currency=credit_document.currency,
                    delta_amount=-matched_amount,
                    match_type=MATCH_TYPE_PROVIDER)

    @classmethod
    def _load_locked_model_object(cls, pk, model_class, allow_empty_pk=True):
        db_model_object = None
        # verify if not new
        if pk:
            # load agency_invoice from db
            db_model_object = model_class.objects.select_for_update().get(pk=pk)
            if not db_model_object:
                raise ValidationError(ERROR_MODEL_NOT_FOUND % model_class.__name__)
        elif not allow_empty_pk:
            raise ValidationError(ERROR_MODEL_NOT_FOUND % model_class.__name__)
        return db_model_object

    @classmethod
    def _document_save(
            cls, user, document, db_document, account=None, movement_type=None,
            other_account=None, db_other_account_id=None, other_amount=None, db_other_amount=None):
        document.fill_data()
        current_datetime = timezone.now()
        # manage operations
        if account:
            document.currency = account.currency
            concept = document.document_type
            detail = document.name
            operations = cls._manage_operations(
                user=user,
                document=document,
                db_document=db_document,
                current_datetime=current_datetime,
                concept=concept,
                detail=detail,
                account=account,
                movement_type=movement_type,
                other_account=other_account,
                db_other_account_id=db_other_account_id,
                other_amount=other_amount,
                db_other_amount=db_other_amount)
        # save documment
        document.save()
        # manage accounting history
        if account:
            for operation in operations:
                accounting_history = AccountingDocumentHistory(
                    document=document,
                    operation=operation)
                accounting_history.save()
        # manage finantial history
        cls._finantial_history(
            user=user,
            document=document,
            db_document=db_document,
            current_datetime=current_datetime)
        return document

    @classmethod
    def _manage_operations(
            cls, user, document, db_document, account, concept, detail, movement_type,
            current_datetime,
            other_account=None, db_other_account_id=None, other_amount=None, db_other_amount=None):
        result = []
        # verify previous operation revertion
        reverted = False
        needs_revertion = cls._needs_revertion(
            document=document,
            db_document=db_document,
            other_account=other_account,
            db_other_account_id=db_other_account_id,
            other_amount=other_amount,
            db_other_amount=db_other_amount)
        if needs_revertion:
            revertion = cls._manage_output_revertion(
                user=user,
                document=document,
                db_document=db_document,
                movement_type=movement_type,
                current_datetime=current_datetime,
                account=account,
                other_account=other_account,
                db_other_account_id=db_other_account_id,
                db_other_amount=db_other_amount)
            if revertion:
                reverted = True
                result.append(revertion)
            # manage current_operation
        current = None
        if cls._needs_current(
                document=document,
                db_document=db_document,
                other_account=other_account,
                db_other_account_id=db_other_account_id,
                other_amount=other_amount,
                db_other_amount=db_other_amount):
            # create new operation
            current = AccountingService.simple_operation(
                user=user,
                current_datetime=current_datetime,
                concept=concept,
                detail=detail,
                account=account,
                movement_type=movement_type,
                amount=document.amount,
                other_account=other_account,
                other_amount=other_amount)
            if current:
                result.append(current)
        if needs_revertion:
            # inputs revertion after current
            revertion = cls._manage_input_revertion(
                user=user,
                document=document,
                db_document=db_document,
                movement_type=movement_type,
                current_datetime=current_datetime,
                account=account,
                other_account=other_account,
                db_other_account_id=db_other_account_id,
                db_other_amount=db_other_amount)
            if revertion:
                reverted = True
                result.append(revertion)
        if current:
            document.current_operation_id = current.pk
        elif reverted:
            document.current_operation_id = None
        return result

    @classmethod
    def _manage_output_revertion(
            cls, user, document, db_document, account, movement_type, current_datetime,
            other_account, db_other_account_id, db_other_amount):
        revertion = None
        reverted_account = account
        if movement_type == MOVEMENT_TYPE_OUTPUT:
            # revert outputs of previous operation
            if db_document.account_id != account.pk:
                if other_account and other_account.pk == db_document.account_id:
                    reverted_account = other_account
                else:
                    reverted_account = cls._load_locked_model_object(
                        pk=db_document.account_id, model_class=Account, allow_empty_pk=False)
            revertion = AccountingService.simple_operation(
                user=user,
                current_datetime=current_datetime,
                concept='Revertion of %s' % (db_document.document_type),
                detail='%s - Revertion of %s' % (document.date, db_document.name),
                account=reverted_account,
                movement_type=MOVEMENT_TYPE_INPUT,
                amount=db_document.amount)
        if movement_type == MOVEMENT_TYPE_INPUT:
            if db_other_account_id:
                if account and (account.pk == db_other_account_id):
                    reverted_account = account
                elif other_account and (other_account.pk == db_other_account_id):
                    reverted_account = other_account
                else:
                    reverted_account = cls._load_locked_model_object(
                        pk=db_other_account_id, model_class=Account, allow_empty_pk=False)
                # revert outputs of previous operation
                reverted_amount = db_document.amount
                if db_other_amount:
                    reverted_amount = db_other_amount
                revertion = AccountingService.simple_operation(
                    user=user,
                    current_datetime=current_datetime,
                    concept='Revertion of %s' % (db_document.document_type),
                    detail='%s - Revertion of %s' % (document.date, db_document.name),
                    account=reverted_account,
                    movement_type=MOVEMENT_TYPE_INPUT,
                    amount=reverted_amount)
        return revertion

    @classmethod
    def _manage_input_revertion(
            cls, user, document, db_document, account, movement_type, current_datetime,
            other_account, db_other_account_id, db_other_amount):
        revertion = None
        reverted_account = account
        if movement_type == MOVEMENT_TYPE_INPUT:
            # revert outputs of previous operation
            if db_document.account_id != account.pk:
                if other_account and other_account.pk == db_document.account_id:
                    reverted_account = other_account
                else:
                    reverted_account = cls._load_locked_model_object(
                        pk=db_document.account_id, model_class=Account, allow_empty_pk=False)
            revertion = AccountingService.simple_operation(
                user=user,
                current_datetime=current_datetime,
                concept='Revertion of %s' % (db_document.document_type),
                detail='%s - Revertion of %s' % (document.date, db_document.name),
                account=reverted_account,
                movement_type=MOVEMENT_TYPE_OUTPUT,
                amount=db_document.amount)
        if movement_type == MOVEMENT_TYPE_OUTPUT:
            if db_other_account_id:
                if account and (account.pk == db_other_account_id):
                    reverted_account = account
                elif other_account and (other_account.pk == db_other_account_id):
                    reverted_account = other_account
                else:
                    reverted_account = cls._load_locked_model_object(
                        pk=db_other_account_id, model_class=Account, allow_empty_pk=False)
                # revert outputs of previous operation
                reverted_amount = db_document.amount
                if db_other_amount:
                    reverted_amount = db_other_amount
                revertion = AccountingService.simple_operation(
                    user=user,
                    current_datetime=current_datetime,
                    concept='Revertion of %s' % (db_document.document_type),
                    detail='%s - Revertion of %s' % (document.date, db_document.name),
                    account=reverted_account,
                    movement_type=MOVEMENT_TYPE_OUTPUT,
                    amount=reverted_amount)
        return revertion

    @classmethod
    def _needs_current(
            cls, document, db_document,
            other_account=None, db_other_account_id=None, other_amount=None, db_other_amount=None):
        return document and (document.status == STATUS_READY) and (
            (not db_document)
            or (not (db_document.status == STATUS_READY))
            or (document.account_id != db_document.account_id)
            or (document.amount != db_document.amount)
            or (other_account and (other_account.pk != db_other_account_id))
            or (other_amount != db_other_amount))

    @classmethod
    def _needs_revertion(
            cls, document, db_document,
            other_account=None, db_other_account_id=None, other_amount=None, db_other_amount=None):
        return db_document and (db_document.status == STATUS_READY) and (
            (not (document.status == STATUS_READY))
            or (document.account_id != db_document.account_id)
            or (document.amount != db_document.amount)
            or (other_account and (other_account.pk != db_other_account_id))
            or (other_amount != db_other_amount))

    @classmethod
    def _finantial_history(cls, user, document, db_document, current_datetime):
        if cls._needs_finantial_history(document=document, db_document=db_document):
            old_status = None
            if db_document:
                old_status = db_document.status
            finantial_history = FinantialDocumentHistory(
                document=document,
                user=user,
                date=current_datetime,
                old_status=old_status,
                new_status=document.status)
            finantial_history.save()

    @classmethod
    def _needs_finantial_history(cls, document, db_document):
        return (not db_document) or (db_document.status != document.status)

    @classmethod
    def _validate_matches(cls, document, db_document, match_type):
        # verify not new
        if db_document and (db_document.status == STATUS_READY):
            # validate status change
            if document.status != STATUS_READY:
                # verifies matches
                if cls._document_has_matches(document=document, match_type=match_type):
                    raise ValidationError(ERROR_MATCH_STATUS)
            # validate amount change
            if db_document.amount > document.amount:
                # verifies matched amount
                if document.matched_amount > document.amount:
                    raise ValidationError(ERROR_MATCH_AMOUNT)

            # validate account changed for loans
            if match_type == MATCH_TYPE_ENTITY or match_type == MATCH_TYPE_ACCOUNT:
                if db_document.account_id != document.account_id:
                    # verifies matches
                    if cls._document_has_matches(document=document, match_type=match_type):
                        raise ValidationError(ERROR_MATCH_ACCOUNT)

                # validate loan_entity changed for loan entities
                if match_type == MATCH_TYPE_ENTITY:
                    if db_document.loan_entity_id != document.loan_entity_id:
                        # verifies matches
                        if cls._document_has_matches(document=document, match_type=match_type):
                            raise ValidationError(ERROR_MATCH_LOAN_ENTITY)

                # validate loan_account changed for loan accounts
                if match_type == MATCH_TYPE_ACCOUNT:
                    if db_document.loan_account_id != document.loan_account_id:
                        # verifies matches
                        if cls._document_has_matches(document=document, match_type=match_type):
                            raise ValidationError(ERROR_MATCH_LOAN_ACCOUNT)

            # validate currency changed for agency and provider
            if match_type == MATCH_TYPE_AGENCY or match_type == MATCH_TYPE_PROVIDER:
                if db_document.currency != document.currency:
                    # verifies matches
                    if cls._document_has_matches(document=document, match_type=match_type):
                        raise ValidationError(ERROR_MATCH_CURRENCY)

                # validate agency changed for agency docs
                if match_type == MATCH_TYPE_AGENCY:
                    if db_document.agency_id != document.agency_id:
                        # verifies matches
                        if cls._document_has_matches(document=document, match_type=match_type):
                            raise ValidationError(ERROR_MATCH_AGENCY)

                # validate provider changed for provider docs
                if match_type == MATCH_TYPE_PROVIDER:
                    if db_document.provider_id != document.provider_id:
                        # verifies matches
                        if cls._document_has_matches(document=document, match_type=match_type):
                            raise ValidationError(ERROR_MATCH_PROVIDER)

    @classmethod
    def _document_has_matches(cls, document, match_type):
        if match_type == MATCH_TYPE_ENTITY:
            return document.loanentitymatch_set.count() > 0
        if match_type == MATCH_TYPE_ACCOUNT:
            return document.loanaccountmatch_set.count() > 0
        if match_type == MATCH_TYPE_AGENCY:
            return document.agencydocumentmatch_set.count() > 0
        if match_type == MATCH_TYPE_PROVIDER:
            return document.providerdocumentmatch_set.count() > 0

    @classmethod
    def _process_match(cls, document_match, db_document_match, match_type):
        if db_document_match:
            # validate same documents
            cls._validate_match_same_documents(
                document_match=document_match,
                db_document_match=db_document_match,
                match_type=match_type)
            # verify amount changed
            if document_match.matched_amount == db_document_match.matched_amount:
                # do nothing
                return document_match

        # get loan match amount
        matched_amount = document_match.matched_amount
        if matched_amount <= 0:
            raise ValidationError(ERROR_AMOUNT_REQUIRED)
        # obtain credit document
        credit_document = cls._get_locked_match_related(
            document_match=document_match,
            match_type=match_type,
            is_credit=True)
        # verify status
        credit_msg = 'Loan Entity Deposit'
        if match_type == MATCH_TYPE_ACCOUNT:
            credit_msg = 'Loan Account Deposit'
        if match_type == MATCH_TYPE_AGENCY:
            credit_msg = 'Agency Credit Document'
        if match_type == MATCH_TYPE_PROVIDER:
            credit_msg = 'Provider Credit Document'
        if credit_document.status != STATUS_READY:
            raise ValidationError(ERROR_NOT_READY % credit_msg)
        # obtain debit document
        debit_document = cls._get_locked_match_related(
            document_match=document_match,
            match_type=match_type,
            is_credit=False)
        # verify status
        debit_msg = 'Loan Entity Withdraw'
        if match_type == MATCH_TYPE_ACCOUNT:
            debit_msg = 'Loan Account Withdraw'
        if match_type == MATCH_TYPE_AGENCY:
            debit_msg = 'Agency Debit Document'
        if match_type == MATCH_TYPE_PROVIDER:
            debit_msg = 'Provider Debit Document'
        if debit_document.status != STATUS_READY:
            raise ValidationError(ERROR_NOT_READY % debit_msg)
        # verify same match entity
        cls._validate_match_same_relateds(
            credit_document=credit_document,
            debit_document=debit_document,
            match_type=match_type)
        if match_type == MATCH_TYPE_ENTITY or match_type == MATCH_TYPE_ACCOUNT:
            # verify accounts
            if credit_document.account_id != debit_document.account_id:
                raise ValidationError(ERROR_DIFFERENT_DOCUMENTS % 'Accounts')
        # delta matched amount
        delta_amount = matched_amount
        if db_document_match:
            delta_amount -= db_document_match.matched_amount
        # verify credit document amount and matched amount
        if delta_amount > credit_document.amount - credit_document.matched_amount:
            raise ValidationError(ERROR_MATCH_OVERMATCHED % credit_msg)
        # verify debit document amount and matched amount
        if delta_amount > debit_document.amount - debit_document.matched_amount:
            raise ValidationError(ERROR_MATCH_OVERMATCHED % debit_msg)
        # save match
        return cls._save_match(
            document_match=document_match,
            credit_document=credit_document,
            debit_document=debit_document,
            delta_amount=delta_amount,
            match_type=match_type)

    @classmethod
    def _validate_match_same_relateds(cls, credit_document, debit_document, match_type):
        msg = 'Loan Entities'
        if match_type == MATCH_TYPE_ACCOUNT:
            msg = 'Loan Accounts'
        if match_type == MATCH_TYPE_AGENCY:
            msg = 'Agencies'
        if match_type == MATCH_TYPE_PROVIDER:
            msg = 'Providers'
        if cls._get_related_id(credit_document, match_type) \
                != cls._get_related_id(debit_document, match_type):
            raise ValidationError(ERROR_DIFFERENT_DOCUMENTS % msg)

    @classmethod
    def _validate_match_same_documents(
            cls, document_match, db_document_match, match_type):
        if match_type == MATCH_TYPE_ENTITY:
            if db_document_match.loan_entity_deposit_id != document_match.loan_entity_deposit_id:
                raise ValidationError(ERROR_DIFFERENT_DOCUMENTS % 'Loan Entity Deposit')
            if db_document_match.loan_entity_withdraw_id != document_match.loan_entity_withdraw_id:
                raise ValidationError(ERROR_DIFFERENT_DOCUMENTS % 'Loan Entity Withdraw')
        if match_type == MATCH_TYPE_ACCOUNT:
            if db_document_match.loan_account_deposit_id != document_match.loan_account_deposit_id:
                raise ValidationError(ERROR_DIFFERENT_DOCUMENTS % 'Loan Account Deposit')
            if db_document_match.loan_account_withdraw_id \
                    != document_match.loan_account_withdraw_id:
                raise ValidationError(ERROR_DIFFERENT_DOCUMENTS % 'Loan Account Withdraw')
        if match_type == MATCH_TYPE_AGENCY:
            if db_document_match.credit_document_id != document_match.credit_document_id:
                raise ValidationError(ERROR_DIFFERENT_DOCUMENTS % 'Agency Credit document')
            if db_document_match.debit_document_id != document_match.debit_document_id:
                raise ValidationError(ERROR_DIFFERENT_DOCUMENTS % 'Agency Debit Document')
        if match_type == MATCH_TYPE_PROVIDER:
            if db_document_match.credit_document_id != document_match.credit_document_id:
                raise ValidationError(ERROR_DIFFERENT_DOCUMENTS % 'Provider Credit document')
            if db_document_match.debit_document_id != document_match.debit_document_id:
                raise ValidationError(ERROR_DIFFERENT_DOCUMENTS % 'Provider Debit Document')

    @classmethod
    def _save_match(
            cls, document_match, credit_document, debit_document, delta_amount, match_type):
        # save match
        document_match.save()
        # documents matched_amount
        credit_document.fix_matched_amount()
        debit_document.fix_matched_amount()
        # loan_emtity matched amount
        cls._process_matched_amount(
            related_id=cls._get_related_id(credit_document, match_type),
            currency=credit_document.currency,
            delta_amount=delta_amount,
            match_type=match_type
        )
        return document_match

    @classmethod
    def _process_summary_amount(cls, document, db_document, match_type, is_credit=False):
        old_ready = False
        old_related_id = None
        old_currency = None
        old_amount = 0
        new_ready = False
        new_related_id = None
        new_currency = None
        new_amount = 0

        if db_document and db_document.status == STATUS_READY:
            old_ready = True
            old_related_id = cls._get_related_id(db_document, match_type)
            old_currency = db_document.currency
            old_amount = db_document.amount
        if document.status == STATUS_READY:
            new_ready = True
            new_related_id = cls._get_related_id(document, match_type)
            new_currency = document.currency
            new_amount = document.amount
        if old_ready:
            if new_ready:
                if (new_related_id == old_related_id) and (new_currency == old_currency):
                    if new_amount != old_amount:
                        # get locked related
                        related_summary = cls._get_locked_related_summary(
                            related_id=new_related_id,
                            currency=new_currency,
                            match_type=match_type)
                        # update amount
                        if is_credit:
                            related_summary.credit_amount += new_amount
                            related_summary.credit_amount -= old_amount
                        else:
                            related_summary.debit_amount += new_amount
                            related_summary.debit_amount -= old_amount
                        related_summary.save()
                else:
                    # get locked old related
                    related_summary = cls._get_locked_related_summary(
                        related_id=old_related_id,
                        currency=old_currency,
                        match_type=match_type)
                    # update amount
                    if is_credit:
                        related_summary.credit_amount -= old_amount
                    else:
                        related_summary.debit_amount -= old_amount
                    related_summary.save()

                    # get locked new related
                    related_summary = cls._get_locked_related_summary(
                        related_id=new_related_id,
                        currency=new_currency,
                        match_type=match_type)
                    # update credit amount
                    if is_credit:
                        related_summary.credit_amount += new_amount
                    else:
                        related_summary.debit_amount += new_amount
                    related_summary.save()
            else:
                # get locked old related
                related_summary = cls._get_locked_related_summary(
                    related_id=old_related_id,
                    currency=old_currency,
                    match_type=match_type)
                # update amount
                if is_credit:
                    related_summary.credit_amount -= old_amount
                else:
                    related_summary.debit_amount -= old_amount
                related_summary.save()
        elif new_ready:
            # get locked new related
            related_summary = cls._get_locked_related_summary(
                related_id=new_related_id,
                currency=new_currency,
                match_type=match_type)
            # update amount
            if is_credit:
                related_summary.credit_amount += new_amount
            else:
                related_summary.debit_amount += new_amount
            related_summary.save()

    @classmethod
    def _process_matched_amount(cls, related_id, currency, delta_amount, match_type):
        # get locked related
        related_summary = cls._get_locked_related_summary(
            related_id=related_id,
            currency=currency,
            match_type=match_type)
        # update amount
        related_summary.matched_amount += delta_amount
        related_summary.save()

    @classmethod
    def _get_related_id(cls, document, match_type):
        if match_type == MATCH_TYPE_ENTITY:
            return document.loan_entity_id
        if match_type == MATCH_TYPE_ACCOUNT:
            return document.loan_account_id
        if match_type == MATCH_TYPE_AGENCY:
            return document.agency_id
        if match_type == MATCH_TYPE_PROVIDER:
            return document.provider_id

    @classmethod
    def _get_locked_match_related(cls, document_match, match_type, is_credit):
        if match_type == MATCH_TYPE_ENTITY:
            if is_credit:
                return cls._load_locked_model_object(
                    pk=document_match.loan_entity_deposit_id, model_class=LoanEntityDeposit)
            else:
                return cls._load_locked_model_object(
                    pk=document_match.loan_entity_withdraw_id, model_class=LoanEntityWithdraw)
        if match_type == MATCH_TYPE_ACCOUNT:
            if is_credit:
                return cls._load_locked_model_object(
                    pk=document_match.loan_account_deposit_id, model_class=LoanAccountDeposit)
            else:
                return cls._load_locked_model_object(
                    pk=document_match.loan_account_withdraw_id, model_class=LoanAccountWithdraw)
        if match_type == MATCH_TYPE_AGENCY:
            if is_credit:
                return cls._load_locked_model_object(
                    pk=document_match.credit_document_id, model_class=AgencyCreditDocument)
            else:
                return cls._load_locked_model_object(
                    pk=document_match.debit_document_id, model_class=AgencyDebitDocument)
        if match_type == MATCH_TYPE_PROVIDER:
            if is_credit:
                return cls._load_locked_model_object(
                    pk=document_match.credit_document_id, model_class=ProviderCreditDocument)
            else:
                return cls._load_locked_model_object(
                    pk=document_match.debit_document_id, model_class=ProviderDebitDocument)

    @classmethod
    def _get_locked_related_summary(cls, related_id, currency, match_type):
        if match_type == MATCH_TYPE_ENTITY:
            # find or create related
            related_summary = LoanEntityCurrency.objects.get_or_create(
                loan_entity_id=related_id,
                currency=currency)
            # load locked
            return cls._load_locked_model_object(
                pk=related_summary[0].pk, model_class=LoanEntityCurrency)
        if match_type == MATCH_TYPE_ACCOUNT:
            # load locked
            return cls._load_locked_model_object(
                pk=related_id, model_class=LoanAccount)
        if match_type == MATCH_TYPE_AGENCY:
            # find or create related
            related_summary = AgencyCurrency.objects.get_or_create(
                agency_id=related_id,
                currency=currency)
            # load locked
            return cls._load_locked_model_object(
                pk=related_summary[0].pk, model_class=AgencyCurrency)
        if match_type == MATCH_TYPE_PROVIDER:
            # find or create related
            related_summary = ProviderCurrency.objects.get_or_create(
                provider_id=related_id,
                currency=currency)
            # load locked
            return cls._load_locked_model_object(
                pk=related_summary[0].pk, model_class=ProviderCurrency)
