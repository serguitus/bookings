"""
Finance Service
"""

from datetime import date, datetime

from django.core.exceptions import ValidationError
from django.db import transaction

from accounting.constants import MOVEMENT_TYPE_DEPOSIT, MOVEMENT_TYPE_WITHDRAW
from accounting.services import AccountingService

from finance.constants import STATUS_READY
from finance.models import Deposit, Withdraw, LoanDeposit, LoanWithdraw, LoanMatch, \
    FinantialDocumentHistory, AccountingDocumentHistory


class FinanceService(object):
    """
    Finance Service
    """

    @classmethod
    def save_deposit(cls, user, deposit):
        """
        Saves Deposit
        """
        with transaction.atomic():
            # load and lock account
            account = cls._load_locked_account(account_id=deposit.account_id)
            today = date.today()
            concept = 'Deposit'
            detail = '%s - Deposit on %s of %s %s ' % (
                today, account, deposit.amount, account.currency)
            db_deposit = cls._load_locked_deposit(deposit=deposit)
            # manage saving
            cls._document_save(
                user=user,
                document=deposit,
                db_document=db_deposit,
                account=account,
                concept=concept,
                detail=detail,
                movement_type=MOVEMENT_TYPE_DEPOSIT)

    @classmethod
    def save_withdraw(cls, user, withdraw):
        """
        Saves Withdraw
        """
        with transaction.atomic():
            # load and lock account
            account = cls._load_locked_account(account_id=withdraw.account_id)
            today = date.today()
            concept = 'Withdraw'
            detail = '%s - Withdraw from %s of %s %s ' % (
                today, account, withdraw.amount, account.currency)
            db_withdraw = cls._load_locked_withdraw(withdraw=withdraw)
            # manage saving
            cls._document_save(
                user=user,
                document=withdraw,
                db_document=db_withdraw,
                account=account,
                concept=concept,
                detail=detail,
                movement_type=MOVEMENT_TYPE_WITHDRAW)

    @classmethod
    def save_loan_deposit(cls, user, loan_deposit):
        """
        Saves Loan Deposit
        """
        with transaction.atomic():
            # load and lock account
            account = cls._load_locked_account(account_id=loan_deposit.account_id)
            today = date.today()
            concept = 'Loan Deposit'
            detail = '%s - Loan Deposit to %s of %s %s ' % (
                today, account, loan_deposit.amount, account.currency)
            db_loan_deposit = cls._load_locked_loan_deposit(loan_deposit=loan_deposit)
            # process matches on amount or status change
            cls._process_loan_matches(document=loan_deposit, db_document=db_loan_deposit)
            # manage saving
            cls._document_save(
                user=user,
                document=loan_deposit,
                db_document=db_loan_deposit,
                account=account,
                concept=concept,
                detail=detail,
                movement_type=MOVEMENT_TYPE_DEPOSIT)

    @classmethod
    def save_loan_withdraw(cls, user, loan_withdraw):
        """
        Saves Loan Withdraw
        """
        with transaction.atomic():
            # load and lock account
            account = cls._load_locked_account(account_id=loan_withdraw.account_id)
            today = date.today()
            concept = 'Loan Withdraw'
            detail = '%s - Loan Withdraw from %s of %s %s ' % (
                today, account, loan_withdraw.amount, account.currency)
            db_loan_withdraw = cls._load_locked_loan_withdraw(loan_withdraw=loan_withdraw)
            # process matches on amount or status change
            cls._process_loan_matches(document=loan_withdraw, db_document=db_loan_withdraw)
            # manage saving
            cls._document_save(
                user=user,
                document=loan_withdraw,
                db_document=db_loan_withdraw,
                account=account,
                concept=concept,
                detail=detail,
                movement_type=MOVEMENT_TYPE_WITHDRAW)

    @classmethod
    def save_loan_match(cls, loan_match):
        """
        Save Loan Match
        """
        with transaction.atomic():
            if not loan_match.pk:
                # new match
                # save match
                cls._save_loan_match(loan_match=loan_match)
            else:
                # db match
                # get db loan match
                db_loan_match = LoanMatch.objects.get(pk=loan_match.pk)
                if not db_loan_match:
                    raise ValidationError('Invalid Loan Match PK')
                # validate same documents
                if db_loan_match.loan_deposit_id != loan_match.loan_deposit_id:
                    raise ValidationError('Invalid Loan Deposit document')
                if db_loan_match.loan_withdraw_id != loan_match.loan_withdraw_id:
                    raise ValidationError('Invalid Loan Withdraw document')
                # save match
                cls._save_loan_match(loan_match=loan_match)

    @classmethod
    def delete_loan_match(cls, loan_match_id):
        """
        Delete Loan Match
        """
        with transaction.atomic():
            # get loan match
            loan_match = LoanMatch.objects.get(pk=loan_match_id)
            if not loan_match:
                raise ValidationError('Invalid Loan Match PK')
            # get loan match amount
            amount = loan_match.amount
            # obtain related documents and update matched_amount
            loan_deposit = cls._load_locked_loan_deposit(loan_match.loan_deposit_id)
            cls._update_matched(document=loan_deposit, amount=amount, direction=-1)
            loan_withdraw = cls._load_locked_loan_withdraw(loan_match.loan_withdraw_id)
            cls._update_matched(document=loan_withdraw, amount=amount, direction=-1)
            # delete loan_match
            loan_match.delete()

    @classmethod
    def save_agency_invoice(cls, user, invoice):
        pass

    @classmethod
    def save_agency_payment(cls, user, payment):
        pass

    @classmethod
    def save_agency_devolution(cls, user, devolution):
        pass

    @classmethod
    def save_agency_discount(cls, user, discount):
        pass

    @classmethod
    def save_provider_invoice(cls, user, invoice):
        pass


    @classmethod
    def save_provider_payment(cls, user, payment):
        pass

    @classmethod
    def save_provider_discount(cls, user, discount):
        pass

    @classmethod
    def save_provider_devolution(cls, user, devolution):
        pass

    @classmethod
    def _load_locked_account(cls, account_id):
        account = AccountingService.find_and_lock_account_by_id(
            account_id=account_id)
        if not account:
            raise ValidationError('Invalid Document Account PK')
        return account

    @classmethod
    def _load_locked_deposit(cls, deposit):
        db_deposit = None
        # verify if not new
        if deposit and deposit.pk:
            # load deposit from db
            db_deposit = Deposit.objects.select_for_update().get(pk=deposit.pk)
            if not db_deposit:
                raise ValidationError('Invalid Deposit PK')
        return db_deposit

    @classmethod
    def _load_locked_withdraw(cls, withdraw):
        db_withdraw = None
        # verify if not new
        if withdraw and withdraw.pk:
            # load withdraw from db
            db_withdraw = Withdraw.objects.select_for_update().get(pk=withdraw.pk)
            if not db_withdraw:
                raise ValidationError('Invalid Withdraw PK')
        return db_withdraw

    @classmethod
    def _load_locked_loan_deposit(cls, loan_deposit):
        db_loan_deposit = None
        # verify if not new
        if loan_deposit and loan_deposit.pk:
            # load loan deposit from db
            db_loan_deposit = LoanDeposit.objects.select_for_update().get(pk=loan_deposit.pk)
            if not db_loan_deposit:
                raise ValidationError('Invalid Loan Deposit PK')
        return db_loan_deposit

    @classmethod
    def _load_locked_loan_withdraw(cls, loan_withdraw):
        db_loan_withdraw = None
        # verify if not new
        if loan_withdraw and loan_withdraw.pk:
            # load loan withdraw from db
            db_loan_withdraw = LoanWithdraw.objects.select_for_update().get(pk=loan_withdraw.pk)
            if not db_loan_withdraw:
                raise ValidationError('Invalid Loan Withdraw PK')
        return db_loan_withdraw

    @classmethod
    def _document_save(cls, user, document, db_document, account, concept, detail, movement_type):
        document.currency = account.currency
        now = datetime.now()
        # manage operations
        operations = cls._manage_operations(
            user=user,
            document=document,
            db_document=db_document,
            current_datetime=now,
            concept=concept,
            detail=detail,
            account=account,
            movement_type=movement_type)
        # save documment
        document.name = detail
        document.save()
        # manage accounting history
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
            current_datetime=now)

    @classmethod
    def _manage_operations(
            cls, user, document, db_document, account, concept, detail, movement_type, \
            current_datetime):
        result = []
        revertion = None
        current = None
        # verify previous operation revertion
        if cls._needs_revertion(document=document, db_document=db_document):
            # revert previous operation
            revertion = cls._revert_operation(
                user=user,
                document=db_document,
                current_datetime=current_datetime)
            if revertion:
                document.current_operation_id = None
                result.append(revertion)
        # manage current_operation
        current = cls._current_operation(
            user=user,
            document=document,
            current_datetime=current_datetime,
            concept=concept,
            detail=detail,
            account=account,
            movement_type=movement_type)
        if current:
            document.current_operation_id = current.pk
            result.append(current)
        return result

    @classmethod
    def _needs_revertion(cls, document, db_document):
        return db_document and db_document.current_operation \
            and (document.status != STATUS_READY \
                or document.account_id != db_document.accont_id \
                or document.amount != db_document.amount)

    @classmethod
    def _revert_operation(cls, user, document, current_datetime):
        operation = None
        if document and document.current_operation:
            operation = AccountingService.revert_operation(
                user=user,
                operation_id=document.current_operation_id,
                current_datetime=current_datetime)
        return operation

    @classmethod
    def _current_operation(
            cls, user, document, current_datetime, concept, detail, account, movement_type):
        operation = None
        if document and document.status == STATUS_READY:
            # create new operation
            operation = AccountingService.simple_operation(
                user=user,
                current_datetime=current_datetime,
                concept=concept,
                detail=detail,
                account=account,
                movement_type=movement_type,
                amount=document.amount)
        return operation

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
    def _process_loan_matches(cls, document, db_document):
        if db_document \
            and (db_document.status == STATUS_READY) \
            and (document.status != STATUS_READY):
            # verifies matches
            if cls._loan_has_matches(document=document):
                raise ValidationError('Can not change status from Ready if Loan document has matches')

    @classmethod
    def _loan_has_matches(cls, document):
        return document.loan_match_set.count() > 0

    @classmethod
    def _save_loan_match(cls, loan_match):
        # get loan match amount
        amount = loan_match.amount
        if amount <= 0:
            raise ValidationError('Amount must be above 0')
        # obtain related documents and update matched_amount
        loan_deposit = cls._load_locked_loan_deposit(loan_match.loan_deposit_id)
        # verify status
        if loan_deposit.status != STATUS_READY:
            raise ValidationError('Loan Deposit Status mus be Ready')
        loan_withdraw = cls._load_locked_loan_withdraw(loan_match.loan_withdraw_id)
        # verify status
        if loan_withdraw.status != STATUS_READY:
            raise ValidationError('Loan Withdraw Status must be Ready')
        # verify accounts
        if loan_deposit.account_id != loan_withdraw.account_id:
            raise ValidationError('Documents Accounts must be the same')
        cls._update_matched(document=loan_deposit, amount=loan_match.amount, direction=1)
        cls._update_matched(document=loan_withdraw, amount=loan_match.amount, direction=1)
        # save loan_match
        loan_match.save()

    @classmethod
    def _update_matched(cls, document, amount, direction):
        # find matches and cancel them
        if direction > 0:
            document.matched_amount = document.matched_amount + amount
            if document.amount < document.matched_amount:
                raise ValidationError('Invalid Match Amount')
            document.save()
        if direction < 0:
            document.matched_amount = document.matched_amount - amount
            if document.matched_amount < 0:
                raise ValidationError('Invalid Match Amount')
            document.save()
