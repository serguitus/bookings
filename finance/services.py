"""
Finance Service
"""

from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from accounting.constants import (
    MOVEMENT_TYPE_INPUT, MOVEMENT_TYPE_OUTPUT, ERROR_DIFFERENT_CURRENCY, ERROR_SAME_CURRENCY)
from accounting.models import Account
from accounting.services import AccountingService

from finance.constants import STATUS_READY
from finance.models import (
    Deposit, Withdraw, CurrencyExchange, Transfer,
    LoanEntityDeposit, LoanEntityWithdraw, LoanEntityMatch,
    LoanAccountDeposit, LoanAccountWithdraw, LoanAccountMatch,
    AgencyInvoice, AgencyPayment, AgencyDevolution, AgencyDiscount, AgencyDocumentMatch,
    ProviderInvoice, ProviderPayment, ProviderDevolution, ProviderDiscount, ProviderDocumentMatch,
    FinantialDocumentHistory, AccountingDocumentHistory)

class FinanceService(object):
    """
    Finance Service
    """

    LOAN_TYPE_ENTITY = 1
    LOAN_TYPE_ACCOUNT = 2

    @classmethod
    def save_deposit(cls, user, deposit):
        """
        Saves Deposit
        """
        with transaction.atomic(savepoint=False):
            # load and lock account
            account = cls._load_locked_model_object(
                pk=deposit.account_id, manager=Account.objects, allow_empty_pk=False)
            db_deposit = cls._load_locked_model_object(
                pk=deposit.pk, manager=Deposit.objects)
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
                pk=withdraw.account_id, manager=Account.objects, allow_empty_pk=False)
            db_withdraw = cls._load_locked_model_object(
                pk=withdraw.pk, manager=Withdraw.objects)
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
                pk=transfer.account_id, manager=Account.objects, allow_empty_pk=False)
            other_account = cls._load_locked_model_object(
                pk=transfer.transfer_account_id, manager=Account.objects,
                allow_empty_pk=False)
            # verify accounts
            if account.currency != other_account.currency:
                raise ValidationError(ERROR_DIFFERENT_CURRENCY % (account, other_account))
            db_transfer = cls._load_locked_model_object(
                pk=transfer.pk, manager=Transfer.objects)
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
                pk=currency_exchange.account_id, manager=Account.objects, allow_empty_pk=False)
            other_account = cls._load_locked_model_object(
                pk=currency_exchange.exchange_account_id, manager=Account.objects,
                allow_empty_pk=False)
            # verify accounts
            if account.currency == other_account.currency:
                raise ValidationError(ERROR_SAME_CURRENCY % (account, other_account))
            db_exchange = cls._load_locked_model_object(
                pk=currency_exchange.pk, manager=CurrencyExchange.objects)
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
                pk=loan_entity_deposit.account_id, manager=Account.objects, allow_empty_pk=False)
            db_loan_entity_deposit = cls._load_locked_model_object(
                pk=loan_entity_deposit.pk, manager=LoanEntityDeposit.objects)
            # process matches on status or amount change
            cls._process_loan_matches(
                document=loan_entity_deposit,
                db_document=db_loan_entity_deposit,
                loan_type=cls.LOAN_TYPE_ENTITY)
            # manage saving
            return cls._document_save(
                user=user,
                document=loan_entity_deposit,
                db_document=db_loan_entity_deposit,
                account=account,
                movement_type=MOVEMENT_TYPE_INPUT)

    @classmethod
    def save_loan_entity_withdraw(cls, user, loan_entity_withdraw):
        """
        Saves Loan Withdraw
        """
        with transaction.atomic(savepoint=False):
            # load and lock account
            account = cls._load_locked_model_object(
                pk=loan_entity_withdraw.account_id, manager=Account.objects, allow_empty_pk=False)
            db_loan_entity_withdraw = cls._load_locked_model_object(
                pk=loan_entity_withdraw.pk, manager=LoanEntityWithdraw.objects)
            # process matches on status or amount change
            cls._process_loan_matches(
                document=loan_entity_withdraw,
                db_document=db_loan_entity_withdraw,
                loan_type=cls.LOAN_TYPE_ENTITY)
            # manage saving
            return cls._document_save(
                user=user,
                document=loan_entity_withdraw,
                db_document=db_loan_entity_withdraw,
                account=account,
                movement_type=MOVEMENT_TYPE_OUTPUT)

    @classmethod
    def save_loan_entity_match(cls, loan_entity_match):
        """
        Save Loan Match
        """
        with transaction.atomic(savepoint=False):
            if not loan_entity_match.pk:
                # new match
                # save match
                cls._save_loan_entity_match(loan_entity_match=loan_entity_match)
            else:
                # db match
                # get db loan match
                db_loan_entity_match = LoanEntityMatch.objects.get(pk=loan_entity_match.pk)
                if not db_loan_entity_match:
                    raise ValidationError('Invalid Loan Entity Match PK')
                # validate same documents
                if db_loan_entity_match.loan_entity_deposit_id != loan_entity_match.loan_entity_deposit_id:
                    raise ValidationError('Invalid Loan Entity Deposit document')
                if db_loan_entity_match.loan_entity_withdraw_id != loan_entity_match.loan_entity_withdraw_id:
                    raise ValidationError('Invalid Loan Entity Withdraw document')
                # verify amount changed
                if loan_entity_match.amount != db_loan_entity_match.amount:
                    # save match
                    cls._save_loan_entity_match(loan_entity_match=loan_entity_match)

    @classmethod
    def delete_loan_entity_match(cls, loan_entity_match_id):
        """
        Delete Loan Entity Match
        """
        with transaction.atomic(savepoint=False):
            # get loan match
            loan_entity_match = LoanEntityMatch.objects.get(pk=loan_entity_match_id)
            if not loan_entity_match:
                raise ValidationError('Invalid Loan Entity Match PK')
            # get loan match amount
            amount = loan_entity_match.amount
            # obtain related documents and update matched_amount
            loan_entity_deposit = cls._load_locked_model_object(
                pk=loan_entity_match.loan_entity_deposit_id, manager=LoanEntityDeposit.objects)
            cls._update_matched(document=loan_entity_deposit, amount=amount, direction=-1)
            loan_entity_withdraw = cls._load_locked_model_object(
                pk=loan_entity_match.loan_entity_withdraw_id, manager=LoanEntityWithdraw.objects)
            cls._update_matched(document=loan_entity_withdraw, amount=amount, direction=-1)
            # delete loan_match
            loan_entity_match.delete()

    @classmethod
    def save_loan_account_deposit(cls, user, loan_account_deposit):
        """
        Saves Loan Account Deposit
        """
        with transaction.atomic(savepoint=False):
            # load and lock accounts
            account = cls._load_locked_model_object(
                pk=loan_account_deposit.account_id, manager=Account.objects, allow_empty_pk=False)
            other_account = cls._load_locked_model_object(
                pk=loan_account_deposit.loan_account_id, manager=Account.objects,
                allow_empty_pk=False)
            # verify accounts
            if account.currency != other_account.currency:
                raise ValidationError(ERROR_DIFFERENT_CURRENCY % (account, other_account))
            db_loan_account_deposit = cls._load_locked_model_object(
                pk=loan_account_deposit.pk, manager=LoanAccountDeposit.objects)
            # define db others
            db_other_account_id = None
            if db_loan_account_deposit:
                db_other_account_id = db_loan_account_deposit.loan_account_id
            # process matches on status or amount change
            cls._process_loan_matches(
                document=loan_account_deposit,
                db_document=db_loan_account_deposit,
                loan_type=cls.LOAN_TYPE_ACCOUNT)
            # manage saving
            return cls._document_save(
                user=user,
                document=loan_account_deposit,
                db_document=db_loan_account_deposit,
                account=account,
                movement_type=MOVEMENT_TYPE_INPUT,
                other_account=other_account,
                db_other_account_id=db_other_account_id)

    @classmethod
    def save_loan_account_withdraw(cls, user, loan_account_withdraw):
        """
        Saves Loan Account Withdraw
        """
        with transaction.atomic(savepoint=False):
            # load and lock accounts
            account = cls._load_locked_model_object(
                pk=loan_account_withdraw.account_id, manager=Account.objects, allow_empty_pk=False)
            other_account = cls._load_locked_model_object(
                pk=loan_account_withdraw.loan_account_id, manager=Account.objects,
                allow_empty_pk=False)
            # verify accounts
            if account.currency != other_account.currency:
                raise ValidationError(ERROR_DIFFERENT_CURRENCY % (account, other_account))
            db_loan_account_withdraw = cls._load_locked_model_object(
                pk=loan_account_withdraw.pk, manager=LoanAccountWithdraw.objects)
            # define db others
            db_other_account_id = None
            if db_loan_account_withdraw:
                db_other_account_id = db_loan_account_withdraw.loan_account_id
            # process matches on status or amount change
            cls._process_loan_matches(
                document=loan_account_withdraw,
                db_document=db_loan_account_withdraw,
                loan_type=cls.LOAN_TYPE_ACCOUNT)
            # manage saving
            return cls._document_save(
                user=user,
                document=loan_account_withdraw,
                db_document=db_loan_account_withdraw,
                account=account,
                movement_type=MOVEMENT_TYPE_OUTPUT,
                other_account=other_account,
                db_other_account_id=db_other_account_id)

    @classmethod
    def save_loan_account_match(cls, loan_account_match):
        """
        Save Loan Account Match
        """
        with transaction.atomic(savepoint=False):
            if not loan_account_match.pk:
                # new match
                # save match
                cls._save_loan_account_match(loan_account_match=loan_account_match)
            else:
                # db match
                # get db loan account match
                db_loan_account_match = LoanAccountMatch.objects.get(pk=loan_account_match.pk)
                if not db_loan_account_match:
                    raise ValidationError('Invalid Loan Account Match PK')
                # validate same documents
                if db_loan_account_match.loan_deposit_account_id != \
                        loan_account_match.loan_deposit_account_id:
                    raise ValidationError('Invalid Loan Account Deposit document')
                if db_loan_account_match.loan_withdraw_account_id != \
                        loan_account_match.loan_withdraw_account_id:
                    raise ValidationError('Invalid Loan Account Withdraw document')
                # verify amount changed
                if loan_account_match.amount != db_loan_account_match.amount:
                    # save match
                    cls._save_loan_account_match(loan_account_match=loan_account_match)

    @classmethod
    def delete_loan_account_match(cls, loan_account_match_id):
        """
        Delete Loan Account Match
        """
        with transaction.atomic(savepoint=False):
            # get loan account match
            loan_account_match = LoanAccountMatch.objects.get(pk=loan_account_match_id)
            if not loan_account_match:
                raise ValidationError('Invalid Loan Account_Match PK')
            # get loan account match amount
            amount = loan_account_match.amount
            # obtain related documents and update matched_amount
            loan_account_deposit = cls._load_locked_model_object(
                pk=loan_account_match.loan_account_deposit_id, manager=LoanAccountDeposit.objects)
            cls._update_matched(document=loan_account_deposit, amount=amount, direction=-1)
            loan_account_withdraw = cls._load_locked_model_object(
                pk=loan_account_match.loan_account_withdraw_id, manager=LoanAccountWithdraw.objects)
            cls._update_matched(document=loan_account_withdraw, amount=amount, direction=-1)
            # delete loan account match
            loan_account_match.delete()

    @classmethod
    def save_agency_invoice(cls, user, agency_invoice):
        pass

    @classmethod
    def save_agency_payment(cls, user, agency_payment):
        pass

    @classmethod
    def save_agency_devolution(cls, user, agency_devolution):
        pass

    @classmethod
    def save_agency_discount(cls, user, agency_discount):
        pass

    @classmethod
    def save_agency_match(cls, agency_match):
        """
        Save Agency Match
        """
        with transaction.atomic(savepoint=False):
            if not agency_match.pk:
                # new match
                # save match
                cls._save_agency_match(agency_match=agency_match)
            else:
                # db match
                # get db agency match
                db_agency_match = AgencyDocumentMatch.objects.get(pk=agency_match.pk)
                if not db_agency_match:
                    raise ValidationError('Invalid Agency Match PK')
                # validate same documents
                if db_agency_match.credit_document_id != agency_match.credit_document_id:
                    raise ValidationError('Invalid Agency Credit document')
                if db_agency_match.debit_document_id != agency_match.debit_document_id:
                    raise ValidationError('Invalid Agency Debit document')
                # verify amount changed
                if agency_match.amount != db_agency_match.amount:
                    # save match
                    cls._save_agency_match(agency_match=agency_match)

    @classmethod
    def delete_agency_match(cls, agency_match_id):
        """
        Delete Agency Match
        """
        with transaction.atomic(savepoint=False):
            # get agency match
            agency_match = AgencyDocumentMatch.objects.get(pk=agency_match_id)
            if not agency_match:
                raise ValidationError('Invalid Agency Match PK')
            # get agency match amount
            amount = agency_match.amount
            # obtain related documents and update matched_amount
            credit_document = cls._load_locked_agency_credit_document(
                pk=agency_match.credit_document_id)
            cls._update_matched(document=credit_document, amount=amount, direction=-1)
            debit_document = cls._load_locked_agency_debit_document(
                pk=agency_match.debit_document_id)
            cls._update_matched(document=debit_document, amount=amount, direction=-1)
            # delete agency_match
            agency_match.delete()

    @classmethod
    def save_provider_invoice(cls, user, provider_invoice):
        pass


    @classmethod
    def save_provider_payment(cls, user, provider_payment):
        pass

    @classmethod
    def save_provider_discount(cls, user, provider_discount):
        pass

    @classmethod
    def save_provider_devolution(cls, user, provider_devolution):
        pass

    @classmethod
    def save_provider_match(cls, provider_match):
        """
        Save Provider Match
        """
        with transaction.atomic(savepoint=False):
            if not provider_match.pk:
                # new match
                # save match
                cls._save_provider_match(provider_match=provider_match)
            else:
                # db match
                # get db provider match
                db_provider_match = ProviderDocumentMatch.objects.get(pk=provider_match.pk)
                if not db_provider_match:
                    raise ValidationError('Invalid Provider Match PK')
                # validate same documents
                if db_provider_match.credit_document_id != provider_match.credit_document_id:
                    raise ValidationError('Invalid Provider Credit document')
                if db_provider_match.debit_document_id != provider_match.debit_document_id:
                    raise ValidationError('Invalid Provider Debit document')
                # verify amount changed
                if provider_match.amount != db_provider_match.amount:
                    # save match
                    cls._save_provider_match(provider_match=provider_match)

    @classmethod
    def delete_provider_match(cls, provider_match_id):
        """
        Delete Provider Match
        """
        with transaction.atomic(savepoint=False):
            # get provider match
            provider_match = ProviderDocumentMatch.objects.get(pk=provider_match_id)
            if not provider_match:
                raise ValidationError('Invalid Provider Match PK')
            # get provider match amount
            amount = provider_match.amount
            # obtain related documents and update matched_amount
            credit_document = cls._load_locked_provider_credit_document(
                pk=provider_match.credit_document_id)
            cls._update_matched(document=credit_document, amount=amount, direction=-1)
            debit_document = cls._load_locked_provider_debit_document(
                pk=provider_match.debit_document_id)
            cls._update_matched(document=debit_document, amount=amount, direction=-1)
            # delete provider_match
            provider_match.delete()

    @classmethod
    def _load_locked_model_object(cls, pk, manager, allow_empty_pk=True):
        db_model_object = None
        # verify if not new
        if pk:
            # load agency_invoice from db
            db_model_object = manager.select_for_update().get(pk=pk)
            if not db_model_object:
                raise ValidationError('Invalid Model Object PK')
        elif not allow_empty_pk:
            raise ValidationError('Empty Model Object PK')
        return db_model_object

    @classmethod
    def _document_save(
            cls, user, document, db_document, account, movement_type,
            other_account=None, db_other_account_id=None, other_amount=None, db_other_amount=None):
        document.currency = account.currency
        document.fill_data()
        concept = document.document_type
        detail = document.name
        current_datetime=timezone.now()
        # manage operations
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
        document.concept = concept
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
        if movement_type is MOVEMENT_TYPE_OUTPUT:
            # revert outputs of previous operation
            if db_document.account_id != account.pk:
                if other_account and other_account.pk == db_document.account_id:
                    reverted_account = other_account
                else:
                    reverted_account = cls._load_locked_model_object(
                        pk=db_document.account_id, manager=Account.objects, allow_empty_pk=False)
            revertion = AccountingService.simple_operation(
                user=user,
                current_datetime=current_datetime,
                concept='Revertion of %s' % (db_document.document_type),
                detail='%s - Revertion of %s' % (document.date, db_document.name),
                account=reverted_account,
                movement_type=MOVEMENT_TYPE_INPUT,
                amount=db_document.amount)
        if movement_type is MOVEMENT_TYPE_INPUT:
            if db_other_account_id:
                if account and (account.pk == db_other_account_id):
                    reverted_account = account
                elif other_account and (other_account.pk == db_other_account_id):
                    reverted_account = other_account
                else:
                    reverted_account = cls._load_locked_model_object(
                        pk=db_other_account_id, manager=Account.objects, allow_empty_pk=False)
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
        if movement_type is MOVEMENT_TYPE_INPUT:
            # revert outputs of previous operation
            if db_document.account_id != account.pk:
                if other_account and other_account.pk == db_document.account_id:
                    reverted_account = other_account
                else:
                    reverted_account = cls._load_locked_model_object(
                        pk=db_document.account_id, manager=Account.objects, allow_empty_pk=False)
            revertion = AccountingService.simple_operation(
                user=user,
                current_datetime=current_datetime,
                concept='Revertion of %s' % (db_document.document_type),
                detail='%s - Revertion of %s' % (document.date, db_document.name),
                account=reverted_account,
                movement_type=MOVEMENT_TYPE_OUTPUT,
                amount=db_document.amount)
        if movement_type is MOVEMENT_TYPE_OUTPUT:
            if db_other_account_id:
                if account and (account.pk == db_other_account_id):
                    reverted_account = account
                elif other_account and (other_account.pk == db_other_account_id):
                    reverted_account = other_account
                else:
                    reverted_account = cls._load_locked_model_object(
                        pk=db_other_account_id, manager=Account.objects, allow_empty_pk=False)
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
        return document and (document.status is STATUS_READY) and (
            (not db_document)
            or (not (db_document.status is STATUS_READY))
            or (document.account_id != db_document.account_id)
            or (document.amount != db_document.amount)
            or (other_account and (other_account.pk != db_other_account_id))
            or (other_amount != db_other_amount))

    @classmethod
    def _needs_revertion(
            cls, document, db_document,
            other_account=None, db_other_account_id=None, other_amount=None, db_other_amount=None):
        return db_document and (db_document.status is STATUS_READY) and (
            (not (document.status is STATUS_READY))
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
    def _process_loan_matches(cls, document, db_document, loan_type):
        # verify not new
        if db_document and (db_document.status == STATUS_READY):
            # process status change
            if document.status != STATUS_READY:
                # verifies matches
                if cls._loan_has_matches(document=document, loan_type=loan_type):
                    raise ValidationError(
                        'Can not change status from Ready if Loan document has matches')
            # process amount change
            if db_document.amount > document.amount:
                # verifies matched amount
                if document.matched_amount > document.amount:
                    raise ValidationError('Can not decrease amount below matched amount')

    @classmethod
    def _loan_has_matches(cls, document, loan_type):
        if loan_type == cls.LOAN_TYPE_ENTITY:
            return document.loanentitymatch_set.count() > 0
        if loan_type == cls.LOAN_TYPE_ACCOUNT:
            return document.loanaccountmatch_set.count() > 0

    @classmethod
    def _save_loan_entity_match(cls, loan_entity_match):
        # get loan match amount
        amount = loan_entity_match.amount
        if amount <= 0:
            raise ValidationError('Amount must be above 0')
        # obtain related documents and update matched_amount
        loan_entity_deposit = cls._load_locked_model_object(
            pk=loan_entity_match.loan_entity_deposit_id, manager=LoanEntityDeposit.objects)
        # verify status
        if loan_entity_deposit.status != STATUS_READY:
            raise ValidationError('Loan Entity Deposit Status must be Ready')
        loan_entity_withdraw = cls._load_locked_model_object(
            pk=loan_entity_match.loan_entity_withdraw_id, manager=LoanEntityWithdraw.objects)
        # verify status
        if loan_entity_withdraw.status != STATUS_READY:
            raise ValidationError('Loan Entity Withdraw Status must be Ready')
        # verify accounts
        if loan_entity_deposit.account_id != loan_entity_withdraw.account_id:
            raise ValidationError('Documents Accounts must be the same')
        cls._update_matched(document=loan_entity_deposit, amount=loan_entity_match.amount, direction=1)
        cls._update_matched(document=loan_entity_withdraw, amount=loan_entity_match.amount, direction=1)
        # save loan_match
        loan_entity_match.save()

    @classmethod
    def _save_loan_account_match(cls, loan_account_match):
        # get loan account_match amount
        amount = loan_account_match.amount
        if amount <= 0:
            raise ValidationError('Amount must be above 0')
        # obtain related documents and update matched_amount
        loan_account_deposit = cls._load_locked_model_object(
            pk=loan_account_match.loan_account_deposit_id, manager=LoanAccountDeposit.objects)
        # verify status
        if loan_account_deposit.status != STATUS_READY:
            raise ValidationError('Loan Account Deposit Status must be Ready')
        loan_account_withdraw = cls._load_locked_model_object(
            pk=loan_account_match.loan_account_withdraw_id, manager=LoanAccountWithdraw.objects)
        # verify status
        if loan_account_withdraw.status != STATUS_READY:
            raise ValidationError('Loan Account Withdraw Status must be Ready')
        # verify accounts
        if loan_account_deposit.account_id != loan_account_withdraw.account_id \
            or loan_account_deposit.withdraw_account_id != loan_account_withdraw.deposit_account_id:
            raise ValidationError('Documents Accounts must be the same')
        cls._update_matched(
            document=loan_account_deposit, amount=loan_account_match.amount, direction=1)
        cls._update_matched(
            document=loan_account_withdraw, amount=loan_account_match.amount, direction=1)
        # save loan account match
        loan_account_match.save()

    @classmethod
    def _save_agency_match(cls, agency_match):
        # get agency match amount
        amount = agency_match.amount
        if amount <= 0:
            raise ValidationError('Amount must be above 0')
        # obtain related documents and update matched_amount
        credit_document = cls._load_locked_agency_credit_document(agency_match.credit_document_id)
        # verify status
        if credit_document.status != STATUS_READY:
            raise ValidationError('Credit Document Status must be Ready')
        debit_document = cls._load_locked_agency_debit_document(agency_match.debit_document_id)
        # verify status
        if debit_document.status != STATUS_READY:
            raise ValidationError('Debit Document Status must be Ready')
        # verify agencies
        if credit_document.agency_id != debit_document.agency_id:
            raise ValidationError('Documents Agencies must be the same')
        cls._update_matched(document=credit_document, amount=agency_match.amount, direction=1)
        cls._update_matched(document=debit_document, amount=agency_match.amount, direction=1)
        # save agency_match
        agency_match.save()

    @classmethod
    def _save_provider_match(cls, provider_match):
        # get provider match amount
        amount = provider_match.amount
        if amount <= 0:
            raise ValidationError('Amount must be above 0')
        # obtain related documents and update matched_amount
        credit_document = cls._load_locked_provider_credit_document(
            pk=provider_match.credit_document_id)
        # verify status
        if credit_document.status != STATUS_READY:
            raise ValidationError('Credit Document Status must be Ready')
        debit_document = cls._load_locked_provider_debit_document(
            pk=provider_match.debit_document_id)
        # verify status
        if debit_document.status != STATUS_READY:
            raise ValidationError('Debit Document Status must be Ready')
        # verify providers
        if credit_document.provider_id != debit_document.provider_id:
            raise ValidationError('Documents Providers must be the same')
        cls._update_matched(document=credit_document, amount=provider_match.amount, direction=1)
        cls._update_matched(document=debit_document, amount=provider_match.amount, direction=1)
        # save provider_match
        provider_match.save()

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

    @classmethod
    def _load_locked_agency_credit_document(cls, pk):
        try:
            payment = cls._load_locked_model_object(
                pk=pk, manager=AgencyPayment.objects)
            return payment
        except:
            discount = cls._load_locked_model_object(
                pk=pk, manager=AgencyDiscount.objects)
            return discount

    @classmethod
    def _load_locked_agency_debit_document(cls, pk):
        try:
            invoice = cls._load_locked_model_object(
                pk=pk, manager=AgencyInvoice.objects)
            return invoice
        except:
            devolution = cls._load_locked_model_object(
                pk=pk, manager=AgencyDevolution.objects)
            return devolution

    @classmethod
    def _load_locked_provider_credit_document(cls, pk):
        try:
            payment = cls._load_locked_model_object(
                pk=pk, manager=ProviderPayment.objects)
            return payment
        except:
            discount = cls._load_locked_model_object(
                pk=pk, manager=ProviderDiscount.objects)
            return discount

    @classmethod
    def _load_locked_provider_debit_document(cls, pk):
        try:
            invoice = cls._load_locked_model_object(
                pk=pk, manager=ProviderInvoice.objects)
            return invoice
        except:
            devolution = cls._load_locked_model_object(
                pk=pk, manager=ProviderDevolution.objects)
            return devolution
