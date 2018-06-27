from datetime import timedelta

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone

from accounting.constants import (
    MOVEMENT_TYPE_INPUT, MOVEMENT_TYPE_OUTPUT, CURRENCY_CUC, CURRENCY_USD, ERROR_DIFFERENT_CURRENCY)
from accounting.models import Account, Operation

from finance.constants import STATUS_DRAFT, STATUS_READY, DOC_TYPE_TRANSFER
from finance.models import Transfer
from finance.services import FinanceService
from finance.tests.utils import FinanceBaseTestCase


class FinanceServiceTestCase(FinanceBaseTestCase):

    test_user = None

    def setUp(self):
        self.test_user = User.objects.create(
            username="Test User")

    def test_save_transfer_status_draft(self):
        """
        Does draft transfer
        """
        test_account1 = Account.objects.create(
            name='Test Account1',
            currency=CURRENCY_CUC)
        test_balance1 = test_account1.balance
        test_account2 = Account.objects.create(
            name='Test Account2',
            currency=CURRENCY_CUC,
            balance=1000)
        test_balance2 = test_account2.balance

        test_date = timezone.now()
        test_amount = 100
        test_status = STATUS_DRAFT

        transfer = Transfer(
            date=test_date,
            account=test_account1,
            transfer_account=test_account2,
            amount=test_amount,
            status=test_status)

        transfer = FinanceService.save_transfer(
            user=self.test_user,
            transfer=transfer)

        # account balance unchanged
        self.assertAccount(test_account=test_account1, test_balance=test_balance1)
        self.assertAccount(test_account=test_account2, test_balance=test_balance2)

        # document data auto filled
        self.assertDocument(transfer, DOC_TYPE_TRANSFER, test_account1.currency)

        # one finantial history created
        finantials = transfer.finantialdocumenthistory_set
        self.assertEqual(finantials.count(), 1)

        # finantial history info
        finantial = finantials.first()
        self.assertFinantialHistory(
            test_finantial_history=finantial, test_document=transfer, test_user=self.test_user,
            test_old_status=None, test_new_status=test_status)

        # no accounting history created
        accountings = transfer.accountingdocumenthistory_set
        self.assertEqual(accountings.count(), 0)

    def test_save_transfer_status_ready(self):
        """
        Does ready transfer
        """
        test_account1 = Account.objects.create(
            name='Test Account1',
            currency=CURRENCY_CUC)
        test_balance1 = test_account1.balance
        test_account2 = Account.objects.create(
            name='Test Account2',
            currency=CURRENCY_CUC,
            balance=1000)
        test_balance2 = test_account2.balance

        test_date = timezone.now()
        test_amount = 100
        test_status = STATUS_READY

        transfer = Transfer(
            date=test_date,
            account=test_account1,
            transfer_account=test_account2,
            amount=test_amount,
            status=test_status)

        transfer = FinanceService.save_transfer(
            user=self.test_user,
            transfer=transfer)

        # account balance incremented
        self.assertAccount(test_account=test_account1, test_balance=test_balance1 + test_amount)
        self.assertAccount(test_account=test_account2, test_balance=test_balance2 - test_amount)

        # document data auto filled
        self.assertDocument(transfer, DOC_TYPE_TRANSFER, test_account1.currency)

        # one finantial history created
        finantials = transfer.finantialdocumenthistory_set
        self.assertEqual(finantials.count(), 1)

        # finantial history info
        finantial = finantials.first()
        self.assertFinantialHistory(
            test_finantial_history=finantial, test_document=transfer, test_user=self.test_user,
            test_old_status=None, test_new_status=test_status)

        # one accounting history created
        accountings = transfer.accountingdocumenthistory_set
        self.assertEqual(accountings.count(), 1)

        # accounting history info
        accounting = accountings.first()
        operation = Operation.objects.get(pk=accounting.operation_id)

        # one movement created
        movements = operation.operationmovement_set
        self.assertEqual(movements.count(), 2)

        # movement info
        movement = movements.first()
        self.assertMovement(
            test_movement=movement, test_account=test_account1,
            test_movement_type=MOVEMENT_TYPE_INPUT, test_amount=test_amount)

        # movement info
        movement = movements.last()
        self.assertMovement(
            test_movement=movement, test_account=test_account2,
            test_movement_type=MOVEMENT_TYPE_OUTPUT, test_amount=test_amount)

    def test_save_transfer_draft_then_ready(self):
        """
        Does draft transfer and then change to ready
        """
        test_account1 = Account.objects.create(
            name='Test Account1',
            currency=CURRENCY_CUC)
        test_balance1 = test_account1.balance
        test_account2 = Account.objects.create(
            name='Test Account2',
            currency=CURRENCY_CUC,
            balance=1000)
        test_balance2 = test_account2.balance

        test_date = timezone.now()
        test_amount = 100
        test_status1 = STATUS_DRAFT

        transfer = Transfer(
            date=test_date,
            account=test_account1,
            transfer_account=test_account2,
            amount=test_amount,
            status=test_status1)

        transfer = FinanceService.save_transfer(
            user=self.test_user,
            transfer=transfer)

        # account balance unchanged
        self.assertAccount(test_account=test_account1, test_balance=test_balance1)
        self.assertAccount(test_account=test_account2, test_balance=test_balance2)

        # document data auto filled
        self.assertDocument(transfer, DOC_TYPE_TRANSFER, test_account1.currency)

        # one finantial history created
        finantials = transfer.finantialdocumenthistory_set
        self.assertEqual(finantials.count(), 1)

        # finantial history info
        finantial = finantials.first()
        self.assertFinantialHistory(
            test_finantial_history=finantial, test_document=transfer, test_user=self.test_user,
            test_old_status=None, test_new_status=test_status1)

        # no accounting history created
        accountings = transfer.accountingdocumenthistory_set
        self.assertEqual(accountings.count(), 0)

        test_status2 = STATUS_READY

        transfer.status = test_status2

        transfer = FinanceService.save_transfer(
            user=self.test_user,
            transfer=transfer)

        # account balance incremented
        self.assertAccount(test_account=test_account1, test_balance=test_balance1 + test_amount)
        self.assertAccount(test_account=test_account2, test_balance=test_balance2 - test_amount)

        # document data auto filled
        self.assertDocument(transfer, DOC_TYPE_TRANSFER, test_account1.currency)

        # now two finantial history created
        finantials = transfer.finantialdocumenthistory_set
        self.assertEqual(finantials.count(), 2)

        # new finantial history info
        finantial = finantials.last()
        self.assertFinantialHistory(
            test_finantial_history=finantial, test_document=transfer, test_user=self.test_user,
            test_old_status=test_status1, test_new_status=test_status2)

        # one accounting history created
        accountings = transfer.accountingdocumenthistory_set
        self.assertEqual(accountings.count(), 1)

        # accounting history info
        accounting = accountings.first()
        operation = Operation.objects.get(pk=accounting.operation_id)

        # one movement created
        movements = operation.operationmovement_set
        self.assertEqual(movements.count(), 2)

        # movement info
        movement = movements.first()
        self.assertMovement(
            test_movement=movement, test_account=test_account1,
            test_movement_type=MOVEMENT_TYPE_INPUT, test_amount=test_amount)
        # movement info
        movement = movements.last()
        self.assertMovement(
            test_movement=movement, test_account=test_account2,
            test_movement_type=MOVEMENT_TYPE_OUTPUT, test_amount=test_amount)


    def test_save_transfer_ready_then_draft(self):
        """
        Does ready transfer and then change to draft
        """
        test_account1 = Account.objects.create(
            name='Test Account1',
            currency=CURRENCY_CUC)
        test_balance1 = test_account1.balance
        test_account2 = Account.objects.create(
            name='Test Account2',
            currency=CURRENCY_CUC,
            balance=1000)
        test_balance2 = test_account2.balance

        test_date = timezone.now()
        test_amount = 100
        test_status1 = STATUS_READY

        transfer = Transfer(
            date=test_date,
            account=test_account1,
            transfer_account=test_account2,
            amount=test_amount,
            status=test_status1)

        transfer = FinanceService.save_transfer(
            user=self.test_user,
            transfer=transfer)

        # account balance incremented
        self.assertAccount(test_account=test_account1, test_balance=test_balance1 + test_amount)
        self.assertAccount(test_account=test_account2, test_balance=test_balance2 - test_amount)

        # document data auto filled
        self.assertDocument(transfer, DOC_TYPE_TRANSFER, test_account1.currency)

        # one finantial history created
        finantials = transfer.finantialdocumenthistory_set
        self.assertEqual(finantials.count(), 1)

        # finantial history info
        finantial = finantials.first()
        self.assertFinantialHistory(
            test_finantial_history=finantial, test_document=transfer, test_user=self.test_user,
            test_old_status=None, test_new_status=test_status1)

        # one accounting history created
        accountings = transfer.accountingdocumenthistory_set
        self.assertEqual(accountings.count(), 1)

        # accounting history info
        accounting = accountings.first()
        operation = Operation.objects.get(pk=accounting.operation_id)

        # one movement created
        movements = operation.operationmovement_set
        self.assertEqual(movements.count(), 2)

        # movement info
        movement = movements.first()
        self.assertMovement(
            test_movement=movement, test_account=test_account1,
            test_movement_type=MOVEMENT_TYPE_INPUT, test_amount=test_amount)
        movement = movements.last()
        self.assertMovement(
            test_movement=movement, test_account=test_account2,
            test_movement_type=MOVEMENT_TYPE_OUTPUT, test_amount=test_amount)

        test_status2 = STATUS_DRAFT

        transfer.status = test_status2

        transfer = FinanceService.save_transfer(
            user=self.test_user,
            transfer=transfer)

        # account balance unchanged
        self.assertAccount(test_account=test_account1, test_balance=test_balance1)
        self.assertAccount(test_account=test_account2, test_balance=test_balance2)

        # document data auto filled
        self.assertDocument(transfer, DOC_TYPE_TRANSFER, test_account1.currency)

        # now two finantial history created
        finantials = transfer.finantialdocumenthistory_set
        self.assertEqual(finantials.count(), 2)

        # new finantial history info
        finantial = finantials.last()
        self.assertFinantialHistory(
            test_finantial_history=finantial, test_document=transfer, test_user=self.test_user,
            test_old_status=test_status1, test_new_status=test_status2)

        # extra accounting history created
        accountings = transfer.accountingdocumenthistory_set
        self.assertEqual(accountings.count(), 3)
        elements = accountings.all()

        # accounting history info
        accounting = elements[1]
        operation = Operation.objects.get(pk=accounting.operation_id)
        # one movement created
        movements = operation.operationmovement_set
        self.assertEqual(movements.count(), 1)
        # movement info
        movement = movements.first()
        self.assertMovement(
            test_movement=movement, test_account=test_account2,
            test_movement_type=MOVEMENT_TYPE_INPUT, test_amount=test_amount)

        # accounting history info
        accounting = elements[2]
        operation = Operation.objects.get(pk=accounting.operation_id)
        # one movement created
        movements = operation.operationmovement_set
        self.assertEqual(movements.count(), 1)
        # movement info
        movement = movements.first()
        self.assertMovement(
            test_movement=movement, test_account=test_account1,
            test_movement_type=MOVEMENT_TYPE_OUTPUT, test_amount=test_amount)

    def test_save_transfer_ready_then_draft_account(self):
        """
        Does ready transfer and then change to draft and account
        """
        test_account1 = Account.objects.create(
            name='Test Account1',
            currency=CURRENCY_CUC)
        test_balance1 = test_account1.balance
        test_account2 = Account.objects.create(
            name='Test Account2',
            currency=CURRENCY_CUC,
            balance=1000)
        test_balance2 = test_account2.balance

        test_date = timezone.now()
        test_amount = 100
        test_status1 = STATUS_READY

        transfer = Transfer(
            date=test_date,
            account=test_account1,
            transfer_account=test_account2,
            amount=test_amount,
            status=test_status1)

        transfer = FinanceService.save_transfer(
            user=self.test_user,
            transfer=transfer)

        # account balance changed
        self.assertAccount(test_account=test_account1, test_balance=test_balance1 + test_amount)
        self.assertAccount(test_account=test_account2, test_balance=test_balance2 - test_amount)

        # document data auto filled
        self.assertDocument(transfer, DOC_TYPE_TRANSFER, test_account1.currency)

        # one finantial history created
        finantials = transfer.finantialdocumenthistory_set
        self.assertEqual(finantials.count(), 1)

        # finantial history info
        finantial = finantials.first()
        self.assertFinantialHistory(
            test_finantial_history=finantial, test_document=transfer, test_user=self.test_user,
            test_old_status=None, test_new_status=test_status1)

        # one accounting history created
        accountings = transfer.accountingdocumenthistory_set
        self.assertEqual(accountings.count(), 1)

        # accounting history info
        accounting = accountings.first()
        operation = Operation.objects.get(pk=accounting.operation_id)

        # one movement created
        movements = operation.operationmovement_set
        self.assertEqual(movements.count(), 2)

        # movement info
        movement = movements.first()
        self.assertMovement(
            test_movement=movement, test_account=test_account1,
            test_movement_type=MOVEMENT_TYPE_INPUT, test_amount=test_amount)
        # movement info
        movement = movements.last()
        self.assertMovement(
            test_movement=movement, test_account=test_account2,
            test_movement_type=MOVEMENT_TYPE_OUTPUT, test_amount=test_amount)

        test_status2 = STATUS_DRAFT

        test_account3 = Account.objects.create(
            name='Test Account3',
            currency=CURRENCY_USD)
        test_balance3 = test_account3.balance
        test_account4 = Account.objects.create(
            name='Test Account4',
            currency=CURRENCY_USD,
            balance=500)
        test_balance4 = test_account4.balance

        transfer.status = test_status2
        transfer.account = test_account3
        transfer.transfer_account = test_account4

        transfer = FinanceService.save_transfer(
            user=self.test_user,
            transfer=transfer)

        # account balance unchanged
        self.assertAccount(test_account=test_account1, test_balance=test_balance1)
        self.assertAccount(test_account=test_account2, test_balance=test_balance2)
        self.assertAccount(test_account=test_account3, test_balance=test_balance3)
        self.assertAccount(test_account=test_account4, test_balance=test_balance4)

        # document data auto filled
        self.assertDocument(transfer, DOC_TYPE_TRANSFER, test_account3.currency)

        # now two finantial history created
        finantials = transfer.finantialdocumenthistory_set
        self.assertEqual(finantials.count(), 2)

        # new finantial history info
        finantial = finantials.last()
        self.assertFinantialHistory(
            test_finantial_history=finantial, test_document=transfer, test_user=self.test_user,
            test_old_status=test_status1, test_new_status=test_status2)

        # extra accounting history created
        accountings = transfer.accountingdocumenthistory_set
        self.assertEqual(accountings.count(), 3)

        elements = accountings.all()

        # accounting history info
        accounting = elements[1]
        operation = Operation.objects.get(pk=accounting.operation_id)
        # one movement created
        movements = operation.operationmovement_set
        self.assertEqual(movements.count(), 1)
        # movement info
        movement = movements.first()
        self.assertMovement(
            test_movement=movement, test_account=test_account2,
            test_movement_type=MOVEMENT_TYPE_INPUT, test_amount=test_amount)

        # accounting history info
        accounting = elements[2]
        operation = Operation.objects.get(pk=accounting.operation_id)
        # one movement created
        movements = operation.operationmovement_set
        self.assertEqual(movements.count(), 1)
        # movement info
        movement = movements.first()
        self.assertMovement(
            test_movement=movement, test_account=test_account1,
            test_movement_type=MOVEMENT_TYPE_OUTPUT, test_amount=test_amount)

    def test_save_transfer_draft_then_amount(self):
        """
        Does draft transfer and then change amount
        """
        test_account1 = Account.objects.create(
            name='Test Account1',
            currency=CURRENCY_CUC)
        test_balance1 = test_account1.balance
        test_account2 = Account.objects.create(
            name='Test Account2',
            currency=CURRENCY_CUC,
            balance=1000)
        test_balance2 = test_account2.balance

        test_date = timezone.now()
        test_amount1 = 100
        test_status = STATUS_DRAFT

        transfer = Transfer(
            date=test_date,
            account=test_account1,
            transfer_account=test_account2,
            amount=test_amount1,
            status=test_status)

        transfer = FinanceService.save_transfer(
            user=self.test_user,
            transfer=transfer)

        # account balance unchanged
        self.assertAccount(test_account=test_account1, test_balance=test_balance1)
        self.assertAccount(test_account=test_account2, test_balance=test_balance2)

        # document data auto filled
        self.assertDocument(transfer, DOC_TYPE_TRANSFER, test_account1.currency)

        # one finantial history created
        finantials = transfer.finantialdocumenthistory_set
        self.assertEqual(finantials.count(), 1)

        # finantial history info
        finantial = finantials.first()
        self.assertFinantialHistory(
            test_finantial_history=finantial, test_document=transfer, test_user=self.test_user,
            test_old_status=None, test_new_status=test_status)

        # no accounting history created
        accountings = transfer.accountingdocumenthistory_set
        self.assertEqual(accountings.count(), 0)

        test_amount2 = 50

        transfer.amount = test_amount2

        transfer = FinanceService.save_transfer(
            user=self.test_user,
            transfer=transfer)

        # account balance unchanged
        self.assertAccount(test_account=test_account1, test_balance=test_balance1)
        self.assertAccount(test_account=test_account2, test_balance=test_balance2)

        # document data auto filled
        self.assertDocument(transfer, DOC_TYPE_TRANSFER, test_account1.currency)

        # no aditional finantial history
        finantials = transfer.finantialdocumenthistory_set
        self.assertEqual(finantials.count(), 1)

        # no accounting history created
        accountings = transfer.accountingdocumenthistory_set
        self.assertEqual(accountings.count(), 0)

    def test_save_transfer_ready_then_amount(self):
        """
        Does ready transfer and then change amount
        """
        test_account1 = Account.objects.create(
            name='Test Account1',
            currency=CURRENCY_CUC)
        test_balance1 = test_account1.balance
        test_account2 = Account.objects.create(
            name='Test Account2',
            currency=CURRENCY_CUC,
            balance=1000)
        test_balance2 = test_account2.balance

        test_date = timezone.now()
        test_amount1 = 100
        test_status = STATUS_READY

        transfer = Transfer(
            date=test_date,
            account=test_account1,
            transfer_account=test_account2,
            amount=test_amount1,
            status=test_status)

        transfer = FinanceService.save_transfer(
            user=self.test_user,
            transfer=transfer)

        # account balance incremented
        self.assertAccount(test_account=test_account1, test_balance=test_balance1 + test_amount1)
        self.assertAccount(test_account=test_account2, test_balance=test_balance2 - test_amount1)

        # document data auto filled
        self.assertDocument(transfer, DOC_TYPE_TRANSFER, test_account1.currency)

        # one finantial history created
        finantials = transfer.finantialdocumenthistory_set
        self.assertEqual(finantials.count(), 1)

        # finantial history info
        finantial = finantials.first()
        self.assertFinantialHistory(
            test_finantial_history=finantial, test_document=transfer, test_user=self.test_user,
            test_old_status=None, test_new_status=test_status)

        # one accounting history created
        accountings = transfer.accountingdocumenthistory_set
        self.assertEqual(accountings.count(), 1)

        # accounting history info
        accounting = accountings.first()
        operation = Operation.objects.get(pk=accounting.operation_id)

        # one movement created
        movements = operation.operationmovement_set
        self.assertEqual(movements.count(), 2)

        # movement info
        movement = movements.first()
        self.assertMovement(
            test_movement=movement, test_account=test_account1,
            test_movement_type=MOVEMENT_TYPE_INPUT, test_amount=test_amount1)
        # movement info
        movement = movements.last()
        self.assertMovement(
            test_movement=movement, test_account=test_account2,
            test_movement_type=MOVEMENT_TYPE_OUTPUT, test_amount=test_amount1)

        test_amount2 = 50

        transfer.amount = test_amount2

        transfer = FinanceService.save_transfer(
            user=self.test_user,
            transfer=transfer)

        # account balance updated
        self.assertAccount(test_account=test_account1, test_balance=test_balance1 + test_amount2)
        self.assertAccount(test_account=test_account2, test_balance=test_balance2 - test_amount2)

        # document data auto filled
        self.assertDocument(transfer, DOC_TYPE_TRANSFER, test_account1.currency)

        # no aditional finantial history
        finantials = transfer.finantialdocumenthistory_set
        self.assertEqual(finantials.count(), 1)

        # two accounting history created
        accountings = transfer.accountingdocumenthistory_set
        self.assertEqual(accountings.count(), 4)

        elements = accountings.all()

        # accounting history info
        accounting = elements[1]
        operation = Operation.objects.get(pk=accounting.operation_id)
        # one movement created
        movements = operation.operationmovement_set
        self.assertEqual(movements.count(), 1)
        # movement info
        movement = movements.first()
        self.assertMovement(
            test_movement=movement, test_account=test_account2,
            test_movement_type=MOVEMENT_TYPE_INPUT, test_amount=test_amount1)

        # accounting history info
        accounting = elements[2]
        operation = Operation.objects.get(pk=accounting.operation_id)
        # 2 movement created
        movements = operation.operationmovement_set
        self.assertEqual(movements.count(), 2)
        # movement info
        movement = movements.first()
        self.assertMovement(
            test_movement=movement, test_account=test_account1,
            test_movement_type=MOVEMENT_TYPE_INPUT, test_amount=test_amount2)
        # movement info
        movement = movements.last()
        self.assertMovement(
            test_movement=movement, test_account=test_account2,
            test_movement_type=MOVEMENT_TYPE_OUTPUT, test_amount=test_amount2)

        # accounting history info
        accounting = elements[3]
        operation = Operation.objects.get(pk=accounting.operation_id)
        # 2 movement created
        movements = operation.operationmovement_set
        self.assertEqual(movements.count(), 1)
        # movement info
        movement = movements.first()
        self.assertMovement(
            test_movement=movement, test_account=test_account1,
            test_movement_type=MOVEMENT_TYPE_OUTPUT, test_amount=test_amount1)

    def test_save_transfer_draft_then_account(self):
        """
        Does draft transfer and then change account
        """
        test_account1 = Account.objects.create(
            name='Test Account1',
            currency=CURRENCY_CUC)
        test_balance1 = test_account1.balance
        test_account2 = Account.objects.create(
            name='Test Account2',
            currency=CURRENCY_CUC,
            balance=1000)
        test_balance2 = test_account2.balance

        test_date = timezone.now()
        test_amount = 100
        test_status = STATUS_DRAFT

        transfer = Transfer(
            date=test_date,
            account=test_account1,
            transfer_account=test_account2,
            amount=test_amount,
            status=test_status)

        transfer = FinanceService.save_transfer(
            user=self.test_user,
            transfer=transfer)

        # account balance unchanged
        self.assertAccount(test_account=test_account1, test_balance=test_balance1)
        self.assertAccount(test_account=test_account2, test_balance=test_balance2)

        # document data auto filled
        self.assertDocument(transfer, DOC_TYPE_TRANSFER, test_account1.currency)

        # one finantial history created
        finantials = transfer.finantialdocumenthistory_set
        self.assertEqual(finantials.count(), 1)

        # finantial history info
        finantial = finantials.first()
        self.assertFinantialHistory(
            test_finantial_history=finantial, test_document=transfer, test_user=self.test_user,
            test_old_status=None, test_new_status=test_status)

        # no accounting history created
        accountings = transfer.accountingdocumenthistory_set
        self.assertEqual(accountings.count(), 0)

        test_account3 = Account.objects.create(
            name='Test Account3',
            currency=CURRENCY_USD)
        test_balance3 = test_account3.balance
        test_account4 = Account.objects.create(
            name='Test Account4',
            currency=CURRENCY_USD,
            balance=500)
        test_balance4 = test_account4.balance

        transfer.account = test_account3
        transfer.transfer_account = test_account4

        transfer = FinanceService.save_transfer(
            user=self.test_user,
            transfer=transfer)

        # account balance unchanged
        self.assertAccount(test_account=test_account1, test_balance=test_balance1)
        self.assertAccount(test_account=test_account2, test_balance=test_balance2)
        self.assertAccount(test_account=test_account3, test_balance=test_balance3)
        self.assertAccount(test_account=test_account4, test_balance=test_balance4)

        # document data auto filled
        self.assertDocument(transfer, DOC_TYPE_TRANSFER, test_account3.currency)

        # no aditional finantial history
        finantials = transfer.finantialdocumenthistory_set
        self.assertEqual(finantials.count(), 1)

        # no accounting history created
        accountings = transfer.accountingdocumenthistory_set
        self.assertEqual(accountings.count(), 0)

    def test_save_transfer_ready_then_account(self):
        """
        Does ready transfer and then change account
        """
        test_account1 = Account.objects.create(
            name='Test Account1',
            currency=CURRENCY_CUC)
        test_balance1 = test_account1.balance
        test_account2 = Account.objects.create(
            name='Test Account2',
            currency=CURRENCY_CUC,
            balance=1000)
        test_balance2 = test_account2.balance

        test_date = timezone.now()
        test_amount = 100
        test_status = STATUS_READY

        transfer = Transfer(
            date=test_date,
            account=test_account1,
            transfer_account=test_account2,
            amount=test_amount,
            status=test_status)

        transfer = FinanceService.save_transfer(
            user=self.test_user,
            transfer=transfer)

        # account balance incremented
        self.assertAccount(test_account=test_account1, test_balance=test_balance1 + test_amount)
        self.assertAccount(test_account=test_account2, test_balance=test_balance2 - test_amount)

        # document data auto filled
        self.assertDocument(transfer, DOC_TYPE_TRANSFER, test_account1.currency)

        # one finantial history created
        finantials = transfer.finantialdocumenthistory_set
        self.assertEqual(finantials.count(), 1)

        # finantial history info
        finantial = finantials.first()
        self.assertFinantialHistory(
            test_finantial_history=finantial, test_document=transfer, test_user=self.test_user,
            test_old_status=None, test_new_status=test_status)

        # one accounting history created
        accountings = transfer.accountingdocumenthistory_set
        self.assertEqual(accountings.count(), 1)

        # accounting history info
        accounting = accountings.first()
        operation = Operation.objects.get(pk=accounting.operation_id)
        # one movement created
        movements = operation.operationmovement_set
        self.assertEqual(movements.count(), 2)
        # movement info
        movement = movements.first()
        self.assertMovement(
            test_movement=movement, test_account=test_account1,
            test_movement_type=MOVEMENT_TYPE_INPUT, test_amount=test_amount)
        # movement info
        movement = movements.last()
        self.assertMovement(
            test_movement=movement, test_account=test_account2,
            test_movement_type=MOVEMENT_TYPE_OUTPUT, test_amount=test_amount)

        test_account3 = Account.objects.create(
            name='Test Account3',
            currency=CURRENCY_USD)
        test_balance3 = test_account3.balance
        test_account4 = Account.objects.create(
            name='Test Account4',
            currency=CURRENCY_USD,
            balance=500)
        test_balance4 = test_account4.balance

        transfer.account = test_account3
        transfer.transfer_account = test_account4

        transfer = FinanceService.save_transfer(
            user=self.test_user,
            transfer=transfer)

        # account balance updated
        self.assertAccount(test_account=test_account1, test_balance=test_balance1)
        self.assertAccount(test_account=test_account2, test_balance=test_balance2)
        self.assertAccount(test_account=test_account3, test_balance=test_balance3 + test_amount)
        self.assertAccount(test_account=test_account4, test_balance=test_balance4 - test_amount)

        # document data auto filled
        self.assertDocument(transfer, DOC_TYPE_TRANSFER, test_account3.currency)

        # no aditional finantial history
        finantials = transfer.finantialdocumenthistory_set
        self.assertEqual(finantials.count(), 1)

        # 3 accounting history created
        accountings = transfer.accountingdocumenthistory_set
        self.assertEqual(accountings.count(), 4)

        elements = accountings.all()

        # accounting history info
        accounting = elements[1]
        operation = Operation.objects.get(pk=accounting.operation_id)
        # one movement created
        movements = operation.operationmovement_set
        self.assertEqual(movements.count(), 1)
        # movement info
        movement = movements.first()
        self.assertMovement(
            test_movement=movement, test_account=test_account2,
            test_movement_type=MOVEMENT_TYPE_INPUT, test_amount=test_amount)

        # accounting history info
        accounting = elements[2]
        operation = Operation.objects.get(pk=accounting.operation_id)
        # 2 movement created
        movements = operation.operationmovement_set
        self.assertEqual(movements.count(), 2)
        # movement info
        movement = movements.first()
        self.assertMovement(
            test_movement=movement, test_account=test_account3,
            test_movement_type=MOVEMENT_TYPE_INPUT, test_amount=test_amount)
        # movement info
        movement = movements.last()
        self.assertMovement(
            test_movement=movement, test_account=test_account4,
            test_movement_type=MOVEMENT_TYPE_OUTPUT, test_amount=test_amount)

        # accounting history info
        accounting = elements[3]
        operation = Operation.objects.get(pk=accounting.operation_id)
        # 2 movement created
        movements = operation.operationmovement_set
        self.assertEqual(movements.count(), 1)
        # movement info
        movement = movements.first()
        self.assertMovement(
            test_movement=movement, test_account=test_account1,
            test_movement_type=MOVEMENT_TYPE_OUTPUT, test_amount=test_amount)

    def test_save_transfer_ready_then_amount_account(self):
        """
        Does ready transfer and then change amount and account
        """
        test_account1 = Account.objects.create(
            name='Test Account1',
            currency=CURRENCY_CUC)
        test_balance1 = test_account1.balance
        test_account2 = Account.objects.create(
            name='Test Account2',
            currency=CURRENCY_CUC,
            balance=1000)
        test_balance2 = test_account2.balance

        test_date = timezone.now()
        test_amount1 = 100
        test_status = STATUS_READY

        transfer = Transfer(
            date=test_date,
            account=test_account1,
            transfer_account=test_account2,
            amount=test_amount1,
            status=test_status)

        transfer = FinanceService.save_transfer(
            user=self.test_user,
            transfer=transfer)

        # account balance incremented
        self.assertAccount(test_account=test_account1, test_balance=test_balance1 + test_amount1)
        self.assertAccount(test_account=test_account2, test_balance=test_balance2 - test_amount1)

        # document data auto filled
        self.assertDocument(transfer, DOC_TYPE_TRANSFER, test_account1.currency)

        # one finantial history created
        finantials = transfer.finantialdocumenthistory_set
        self.assertEqual(finantials.count(), 1)

        # finantial history info
        finantial = finantials.first()
        self.assertFinantialHistory(
            test_finantial_history=finantial, test_document=transfer, test_user=self.test_user,
            test_old_status=None, test_new_status=test_status)

        # one accounting history created
        accountings = transfer.accountingdocumenthistory_set
        self.assertEqual(accountings.count(), 1)

        # accounting history info
        accounting = accountings.first()
        operation = Operation.objects.get(pk=accounting.operation_id)
        # one movement created
        movements = operation.operationmovement_set
        self.assertEqual(movements.count(), 2)
        # movement info
        movement = movements.first()
        self.assertMovement(
            test_movement=movement, test_account=test_account1,
            test_movement_type=MOVEMENT_TYPE_INPUT, test_amount=test_amount1)
        # movement info
        movement = movements.last()
        self.assertMovement(
            test_movement=movement, test_account=test_account2,
            test_movement_type=MOVEMENT_TYPE_OUTPUT, test_amount=test_amount1)

        test_account3 = Account.objects.create(
            name='Test Account3',
            currency=CURRENCY_USD)
        test_balance3 = test_account3.balance
        test_account4 = Account.objects.create(
            name='Test Account4',
            currency=CURRENCY_USD,
            balance=500)
        test_balance4 = test_account4.balance

        test_amount2 = 50

        transfer.account = test_account3
        transfer.transfer_account = test_account4
        transfer.amount = test_amount2

        transfer = FinanceService.save_transfer(
            user=self.test_user,
            transfer=transfer)

        # account balance updated
        self.assertAccount(test_account=test_account1, test_balance=test_balance1)
        self.assertAccount(test_account=test_account2, test_balance=test_balance2)
        self.assertAccount(test_account=test_account3, test_balance=test_balance3 + test_amount2)
        self.assertAccount(test_account=test_account4, test_balance=test_balance4 - test_amount2)

        # document data auto filled
        self.assertDocument(transfer, DOC_TYPE_TRANSFER, test_account3.currency)

        # no aditional finantial history
        finantials = transfer.finantialdocumenthistory_set
        self.assertEqual(finantials.count(), 1)

        # 3 accounting history created
        accountings = transfer.accountingdocumenthistory_set
        self.assertEqual(accountings.count(), 4)

        elements = accountings.all()

        # accounting history info
        accounting = elements[1]
        operation = Operation.objects.get(pk=accounting.operation_id)
        # one movement created
        movements = operation.operationmovement_set
        self.assertEqual(movements.count(), 1)
        # movement info
        movement = movements.first()
        self.assertMovement(
            test_movement=movement, test_account=test_account2,
            test_movement_type=MOVEMENT_TYPE_INPUT, test_amount=test_amount1)

        # accounting history info
        accounting = elements[2]
        operation = Operation.objects.get(pk=accounting.operation_id)
        # 2 movement created
        movements = operation.operationmovement_set
        self.assertEqual(movements.count(), 2)
        # movement info
        movement = movements.first()
        self.assertMovement(
            test_movement=movement, test_account=test_account3,
            test_movement_type=MOVEMENT_TYPE_INPUT, test_amount=test_amount2)
        # movement info
        movement = movements.last()
        self.assertMovement(
            test_movement=movement, test_account=test_account4,
            test_movement_type=MOVEMENT_TYPE_OUTPUT, test_amount=test_amount2)

        # accounting history info
        accounting = elements[3]
        operation = Operation.objects.get(pk=accounting.operation_id)
        # 2 movement created
        movements = operation.operationmovement_set
        self.assertEqual(movements.count(), 1)
        # movement info
        movement = movements.first()
        self.assertMovement(
            test_movement=movement, test_account=test_account1,
            test_movement_type=MOVEMENT_TYPE_OUTPUT, test_amount=test_amount1)

    def test_save_transfer_draft_then_date(self):
        """
        Does draft transfer and then change date
        """
        test_account1 = Account.objects.create(
            name='Test Account1',
            currency=CURRENCY_CUC)
        test_balance1 = test_account1.balance
        test_account2 = Account.objects.create(
            name='Test Account2',
            currency=CURRENCY_CUC,
            balance=1000)
        test_balance2 = test_account2.balance

        test_date1 = timezone.now()
        test_amount = 100
        test_status = STATUS_DRAFT

        transfer = Transfer(
            date=test_date1,
            account=test_account1,
            transfer_account=test_account2,
            amount=test_amount,
            status=test_status)

        transfer = FinanceService.save_transfer(
            user=self.test_user,
            transfer=transfer)

        test_name1 = transfer.name

        # account balance unchanged
        self.assertAccount(test_account=test_account1, test_balance=test_balance1)
        self.assertAccount(test_account=test_account2, test_balance=test_balance2)

        # document data auto filled
        self.assertDocument(transfer, DOC_TYPE_TRANSFER, test_account1.currency)

        # one finantial history created
        finantials = transfer.finantialdocumenthistory_set
        self.assertEqual(finantials.count(), 1)

        # finantial history info
        finantial = finantials.first()
        self.assertFinantialHistory(
            test_finantial_history=finantial, test_document=transfer, test_user=self.test_user,
            test_old_status=None, test_new_status=test_status)

        # no accounting history created
        accountings = transfer.accountingdocumenthistory_set
        self.assertEqual(accountings.count(), 0)

        test_date2 = test_date1 - timedelta(days=5)

        transfer.date = test_date2

        transfer = FinanceService.save_transfer(
            user=self.test_user,
            transfer=transfer)

        test_name2 = transfer.name

        # name changed
        self.assertNotEqual(test_name1, test_name2)

        # account balance unchanged
        self.assertAccount(test_account=test_account1, test_balance=test_balance1)
        self.assertAccount(test_account=test_account2, test_balance=test_balance2)

        # document data auto filled
        self.assertDocument(transfer, DOC_TYPE_TRANSFER, test_account1.currency)

        # no finantial history created
        finantials = transfer.finantialdocumenthistory_set
        self.assertEqual(finantials.count(), 1)

        # no accounting history created
        accountings = transfer.accountingdocumenthistory_set
        self.assertEqual(accountings.count(), 0)

    def test_save_transfer_ready_then_date(self):
        """
        Does ready transfer and then change to draft
        """
        test_account1 = Account.objects.create(
            name='Test Account1',
            currency=CURRENCY_CUC)
        test_balance1 = test_account1.balance
        test_account2 = Account.objects.create(
            name='Test Account2',
            currency=CURRENCY_CUC,
            balance=1000)
        test_balance2 = test_account2.balance

        test_date1 = timezone.now()
        test_amount = 100
        test_status = STATUS_READY

        transfer = Transfer(
            date=test_date1,
            account=test_account1,
            transfer_account=test_account2,
            amount=test_amount,
            status=test_status)

        transfer = FinanceService.save_transfer(
            user=self.test_user,
            transfer=transfer)

        test_name1 = transfer.name

        # account balance incremented
        self.assertAccount(test_account=test_account1, test_balance=test_balance1 + test_amount)
        self.assertAccount(test_account=test_account2, test_balance=test_balance2 - test_amount)

        # document data auto filled
        self.assertDocument(transfer, DOC_TYPE_TRANSFER, test_account1.currency)

        # one finantial history created
        finantials = transfer.finantialdocumenthistory_set
        self.assertEqual(finantials.count(), 1)

        # finantial history info
        finantial = finantials.first()
        self.assertFinantialHistory(
            test_finantial_history=finantial, test_document=transfer, test_user=self.test_user,
            test_old_status=None, test_new_status=test_status)

        # one accounting history created
        accountings = transfer.accountingdocumenthistory_set
        self.assertEqual(accountings.count(), 1)

        # accounting history info
        accounting = accountings.first()
        operation = Operation.objects.get(pk=accounting.operation_id)
        # one movement created
        movements = operation.operationmovement_set
        self.assertEqual(movements.count(), 2)
        # movement info
        movement = movements.first()
        self.assertMovement(
            test_movement=movement, test_account=test_account1,
            test_movement_type=MOVEMENT_TYPE_INPUT, test_amount=test_amount)
        # movement info
        movement = movements.last()
        self.assertMovement(
            test_movement=movement, test_account=test_account2,
            test_movement_type=MOVEMENT_TYPE_OUTPUT, test_amount=test_amount)

        test_date2 = test_date1 - timedelta(days=5)

        transfer.date = test_date2

        transfer = FinanceService.save_transfer(
            user=self.test_user,
            transfer=transfer)

        test_name2 = transfer.name

        # name changed
        self.assertNotEqual(test_name1, test_name2)

        # account balance remains changed
        self.assertAccount(test_account=test_account1, test_balance=test_balance1 + test_amount)
        self.assertAccount(test_account=test_account2, test_balance=test_balance2 - test_amount)

        # document data auto filled
        self.assertDocument(transfer, DOC_TYPE_TRANSFER, test_account1.currency)

        # same finantial history
        finantials = transfer.finantialdocumenthistory_set
        self.assertEqual(finantials.count(), 1)

        # same accounting history
        accountings = transfer.accountingdocumenthistory_set
        self.assertEqual(accountings.count(), 1)

    def test_save_transfer_different_currency(self):
        """
        Does transfer with different accounts currency
        """
        test_account1 = Account.objects.create(
            name='Test Account1',
            currency=CURRENCY_CUC)
        test_balance1 = test_account1.balance
        test_account2 = Account.objects.create(
            name='Test Account2',
            currency=CURRENCY_USD,
            balance=1000)
        test_balance2 = test_account2.balance

        test_date = timezone.now()
        test_amount = 100
        test_status = STATUS_READY

        transfer = Transfer(
            date=test_date,
            account=test_account1,
            transfer_account=test_account2,
            amount=test_amount,
            status=test_status)

        with self.assertRaisesMessage(
            ValidationError, ERROR_DIFFERENT_CURRENCY % (test_account1, test_account2)) as ex:
            transfer = FinanceService.save_transfer(
                user=self.test_user,
                transfer=transfer)

        # account balance unchanged
        #self.assertAccount(test_account=test_account1, test_balance=test_balance1)
        #self.assertAccount(test_account=test_account2, test_balance=test_balance2)
