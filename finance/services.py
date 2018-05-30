
from django.core.exceptions import ValidationError
from django.db import transaction

from accounting.models import *
from accounting.services import AccountingService
from finance.models import *


class FinanceService(object):

    @classmethod
    def validateDocumentCancelled(cls, document):
        if document.status != STATUS_CANCELLED:
            raise ValidationError('Document Not Cancelled')

    @classmethod
    def validateDocumentNotCancelled(cls, document):
        if document.status == STATUS_CANCELLED:
            raise ValidationError('Document Cancelled')
           
    @classmethod
    def findDocumentById(cls, document_id):
        with transaction.atomic():
            document = (
                FinantialDocument.objects.get(id=document_id)
            )
            if not document:
                raise ValidationError('Document Not Fount : %s' % (document_id))
            return document

    @classmethod
    def findAndLockDocumentById(cls, document_id):
        with transaction.atomic():
            document = (
                FinantialDocument.objects.select_for_update().get(id=document_id)
            )
            if not document:
                raise ValidationError('Document Not Fount : %s' % (document_id))
            return document

    @classmethod
    def cancelDocument(cls, user, document):
        cls.validateDocumentNotCancelled(document=document)
        document.status = STATUS_CANCELLED
        with transaction.atomic():
            # verify accounting document
            if (document is AccountingDocument):
                document.current_operation = cls._revertAccountingDocumentOperation(user, document, CONCEPT_CANCELLATION)
            document.save()
            # verify matching document
            if (document is MatchingDocument):
                cls._cancelMatching(document)
           
    @classmethod
    def revertDocumentCancellation(cls, user, document):
        cls.validateDocumentCancelled(document=document)
        document.cancelled = True
        with transaction.atomic():
            if document is AccountingDocument:
                document.current_operation = cls._revertAccountingDocumentOperation(user, document, CONCEPT_REVERT_CANCELLATION)
            document.save()
            # verify matching document
            if (document is MatchingDocument):
                cls._restoreMatching(document)

    @classmethod
    def save_deposit(cls, user, deposit):
        with transaction.atomic():
            # validate currencies
            account = AccountingService.find_and_lock_account_by_id(deposit.deposit_account_id)
            if not account
                raise ValidationError('Invalid Account for Deposit')
            if account.currency != deposit.currency:
                raise ValidationError('Deposit Currency (%s) and Account Currency (%s) must be equals' % (deposit.currency, account.currency))
            date = now()
            concept = 'Deposit on Account'
            detail = 'Date %s - Deposit on %s of %s %s ' % (date, account, deposit.amount, deposit.currency)
            # verify if new
            if deposit.id == None:
                    if cls.document_needs_operation(deposit):
                        # create new operation
                        operation = Operation(
                            user = user,
                            date = date,
                            concept = concept,
                            detail = detail)
                        operation.save()
                        # create operation movement
                        AccountingService.add_operation_movement(
                            operation = operation,
                            account = account,
                            movement_type = MOVEMENT_TYPE_DEPOSIT,
                            amount = deposit.amount)
                        deposit.current_operation_id = operation.id
                    # save deposit
                    deposit.save()
                    # manage finantial history
                    finantial_history = FinantialDocumentHistory(
                        document = deposit,
                        user = user,
                        date = date,
                        old_status = None,
                        new_status = deposit.status)
                    finantial_history.save()
                    if deposit.current_operation_id:
                        # manage accounting history
                        accounting_history = AccountingDocumentHistory(
                            document = deposit,
                            operation = operation)
                        accounting_history.save()
            else:
                # verify need of new operation
                if cls.deposit_accounting_changed(deposit):
                    with transaction.atomic():
                        # save deposit
                        deposit.save()
                        # create operation reverting current operation

                        # add to 

                        if cls.document_needs_operation(deposit):
                            # create new operation
                            operation = Operation(user = user, date = date,  concept = concept, detail = detail)
                            operation.save()
                            # create operation movement
                            account = AccountingService.find_and_lock_account_by_id(deposit.account.id)
                            AccountingService.add_operation_movement(operation = operation, account = account, movement_type = MOVEMENT_TYPE_DEPOSIT, amount = deposit.amount)

    @classmethod
    def document_needs_operation(cls, document):
        return document.status == STATUS_READY

    @classmethod
    def deposit_accounting_changed(cls, deposit):
        # load deposit from db
        db_deposit = Deposit.objects.get(id = deposit.id)
        return deposit.deposit_account.id != db_deposit.deposit_accont.id or deposit.amount != db_deposit.amount

    @classmethod
    def saveWithdraw(cls, user, withdraw):

    @classmethod
    def saveLoan(cls, user, loan):

    @classmethod
    def saveLoanDevolution(cls, user, devolution):

    @classmethod
    def saveInvoiceToAgency(cls, user, invoice):

    @classmethod
    def savePaymentFromProvider(cls, user, payment):

    @classmethod
    def saveDiscountToAgency(cls, user, discount):

    @classmethod
    def saveDevolutionToAgency(cls, user, devolution):

    @classmethod
    def saveInvoiceFromProvider(cls, user, invoice):

    @classmethod
    def savePaymentToProvider(cls, user, payment):

    @classmethod
    def saveDiscountFromProvider(cls, user, discount):

    @classmethod
    def saveDevolutionFromProvider(cls, user, devolution):




    @classmethod
    def _buildDocumentDetail(cls, document):
        return document.name

    @classmethod
    def _revertAccountingDocumentOperation(cls, user, document, concept):
        current_operation= document.current_operation
        with transaction.atomic():
            operation = Operation(
                user=user,
                date=now(),
                concept=concept,
                detail=cls._buildDocumentDetail(document),
            )
            operation.save()
            # add to document account history

            # barrer movimientos de operacion
            for ():
                reverted_movement_type
                movement = Movement(
                    operation=operation,
                    movement_type=reverted_movement_type,
                    account=account,
                    amount=amount,
                )
                movement.save()

            return operation

    @classmethod
    def _cancelDocumentMatching(cls, document):
        # find matches and cancel them

        for ():
            # cancel and update documents unmatched

        # verify if loan
        # verify if loan devolution
        # verify if agency debit
        # verify if agency credit
        return document

    @classmethod
    def _restoreDocumentMatching(cls, document):
        # find matches and try to restore them
        for ():
            # try to restore and update documents unmatched


        return document

           
