from datetime import timedelta

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone

from accounting.constants import (
    MOVEMENT_TYPE_INPUT, MOVEMENT_TYPE_OUTPUT, CURRENCY_CUC, CURRENCY_USD)
from accounting.models import Account, Operation

from finance.constants import STATUS_DRAFT, STATUS_READY, DOC_TYPE_WITHDRAW
from finance.models import Withdraw
from finance.services import FinanceService
from finance.tests.utils import FinanceBaseTestCase


class FinanceServiceTestCase(FinanceBaseTestCase):

    test_user = None

    def setUp(self):
        self.test_user = User.objects.create(
            username="Test User")

    def test_save_withdraw_status_draft(self):
        """
        Does draft withdraw
        """
        test_account = Account.objects.create(
            name='Test Account',
            currency=CURRENCY_CUC,
            balance=1000)
        test_balance = test_account.balance

        test_date = timezone.now()
        test_amount = 100
        test_status = STATUS_DRAFT

        withdraw = Withdraw(
            date=test_date,
            account=test_account,
            amount=test_amount,
            status=test_status)

        withdraw = FinanceService.save_withdraw(
            user=self.test_user,
            withdraw=withdraw)

        # account balance unchanged
        self.assertAccount(test_account=test_account, test_balance=test_balance)

        # document data auto filled
        self.assertDocument(withdraw, DOC_TYPE_WITHDRAW, test_account.currency)

        # one finantial history created
        finantials = withdraw.finantialdocumenthistory_set
        self.assertEqual(finantials.count(), 1)

        # finantial history info
        finantial = finantials.first()
        self.assertFinantialHistory(
            test_finantial_history=finantial, test_document=withdraw, test_user=self.test_user,
            test_old_status=None, test_new_status=test_status)

        # no accounting history created
        accountings = withdraw.accountingdocumenthistory_set
        self.assertEqual(accountings.count(), 0)

    def test_save_withdraw_status_ready(self):
        """
        Does ready withdraw
        """
        test_account = Account.objects.create(
            name='Test Account',
            currency=CURRENCY_CUC,
            balance=1000)
        test_balance = test_account.balance

        test_date = timezone.now()
        test_amount = 100
        test_status = STATUS_READY

        withdraw = Withdraw(
            date=test_date,
            account=test_account,
            amount=test_amount,
            status=test_status)

        withdraw = FinanceService.save_withdraw(
            user=self.test_user,
            withdraw=withdraw)

        # account balance decremented
        self.assertAccount(test_account=test_account, test_balance=test_balance - test_amount)

        # document data auto filled
        self.assertDocument(withdraw, DOC_TYPE_WITHDRAW, test_account.currency)

        # one finantial history created
        finantials = withdraw.finantialdocumenthistory_set
        self.assertEqual(finantials.count(), 1)

        # finantial history info
        finantial = finantials.first()
        self.assertFinantialHistory(
            test_finantial_history=finantial, test_document=withdraw, test_user=self.test_user,
            test_old_status=None, test_new_status=test_status)

        # one accounting history created
        accountings = withdraw.accountingdocumenthistory_set
        self.assertEqual(accountings.count(), 1)

        # accounting history info
        accounting = accountings.first()
        operation = Operation.objects.get(pk=accounting.operation_id)

        # one movement created
        movements = operation.operationmovement_set
        self.assertEqual(movements.count(), 1)

        # movement info
        movement = movements.first()
        self.assertMovement(
            test_movement=movement, test_account=test_account,
            test_movement_type=MOVEMENT_TYPE_OUTPUT, test_amount=test_amount)

    def test_save_withdraw_draft_then_ready(self):
        """
        Does draft withdraw and then change to ready
        """
        test_account = Account.objects.create(
            name='Test Account',
            currency=CURRENCY_CUC,
            balance=1000)
        test_balance = test_account.balance

        test_date = timezone.now()
        test_amount = 100
        test_status1 = STATUS_DRAFT

        withdraw = Withdraw(
            date=test_date,
            account=test_account,
            amount=test_amount,
            status=test_status1)

        withdraw = FinanceService.save_withdraw(
            user=self.test_user,
            withdraw=withdraw)

        # account balance unchanged
        self.assertAccount(test_account=test_account, test_balance=test_balance)

        # document data auto filled
        self.assertDocument(withdraw, DOC_TYPE_WITHDRAW, test_account.currency)

        # one finantial history created
        finantials = withdraw.finantialdocumenthistory_set
        self.assertEqual(finantials.count(), 1)

        # finantial history info
        finantial = finantials.first()
        self.assertFinantialHistory(
            test_finantial_history=finantial, test_document=withdraw, test_user=self.test_user,
            test_old_status=None, test_new_status=test_status1)

        # no accounting history created
        accountings = withdraw.accountingdocumenthistory_set
        self.assertEqual(accountings.count(), 0)

        test_status2 = STATUS_READY

        withdraw.status = test_status2

        withdraw = FinanceService.save_withdraw(
            user=self.test_user,
            withdraw=withdraw)

        # account balance incremented
        self.assertAccount(test_account=test_account, test_balance=test_balance - test_amount)

        # document data auto filled
        self.assertDocument(withdraw, DOC_TYPE_WITHDRAW, test_account.currency)

        # now two finantial history created
        finantials = withdraw.finantialdocumenthistory_set
        self.assertEqual(finantials.count(), 2)

        # new finantial history info
        finantial = finantials.last()
        self.assertFinantialHistory(
            test_finantial_history=finantial, test_document=withdraw, test_user=self.test_user,
            test_old_status=test_status1, test_new_status=test_status2)

        # one accounting history created
        accountings = withdraw.accountingdocumenthistory_set
        self.assertEqual(accountings.count(), 1)

        # accounting history info
        accounting = accountings.first()
        operation = Operation.objects.get(pk=accounting.operation_id)

        # one movement created
        movements = operation.operationmovement_set
        self.assertEqual(movements.count(), 1)

        # movement info
        movement = movements.first()
        self.assertMovement(
            test_movement=movement, test_account=test_account,
            test_movement_type=MOVEMENT_TYPE_OUTPUT, test_amount=test_amount)

    def test_save_withdraw_ready_then_draft(self):
        """
        Does ready withdraw and then change to draft
        """
        test_account = Account.objects.create(
            name='Test Account',
            currency=CURRENCY_CUC,
            balance=1000)
        test_balance = test_account.balance

        test_date = timezone.now()
        test_amount = 100
        test_status1 = STATUS_READY

        withdraw = Withdraw(
            date=test_date,
            account=test_account,
            amount=test_amount,
            status=test_status1)

        withdraw = FinanceService.save_withdraw(
            user=self.test_user,
            withdraw=withdraw)

        # account balance incremented
        self.assertAccount(test_account=test_account, test_balance=test_balance - test_amount)

        # document data auto filled
        self.assertDocument(withdraw, DOC_TYPE_WITHDRAW, test_account.currency)

        # one finantial history created
        finantials = withdraw.finantialdocumenthistory_set
        self.assertEqual(finantials.count(), 1)

        # finantial history info
        finantial = finantials.first()
        self.assertFinantialHistory(
            test_finantial_history=finantial, test_document=withdraw, test_user=self.test_user,
            test_old_status=None, test_new_status=test_status1)

        # one accounting history created
        accountings = withdraw.accountingdocumenthistory_set
        self.assertEqual(accountings.count(), 1)

        # accounting history info
        accounting = accountings.first()
        operation = Operation.objects.get(pk=accounting.operation_id)

        # one movement created
        movements = operation.operationmovement_set
        self.assertEqual(movements.count(), 1)

        # movement info
        movement = movements.first()
        self.assertMovement(
            test_movement=movement, test_account=test_account,
            test_movement_type=MOVEMENT_TYPE_OUTPUT, test_amount=test_amount)

        test_status2 = STATUS_DRAFT

        withdraw.status = test_status2

        withdraw = FinanceService.save_withdraw(
            user=self.test_user,
            withdraw=withdraw)

        # account balance unchanged
        self.assertAccount(test_account=test_account, test_balance=test_balance)

        # document data auto filled
        self.assertDocument(withdraw, DOC_TYPE_WITHDRAW, test_account.currency)

        # now two finantial history created
        finantials = withdraw.finantialdocumenthistory_set
        self.assertEqual(finantials.count(), 2)

        # new finantial history info
        finantial = finantials.last()
        self.assertFinantialHistory(
            test_finantial_history=finantial, test_document=withdraw, test_user=self.test_user,
            test_old_status=test_status1, test_new_status=test_status2)

        # extra accounting history created
        accountings = withdraw.accountingdocumenthistory_set
        self.assertEqual(accountings.count(), 2)

        # accounting history info
        accounting = accountings.last()
        operation = Operation.objects.get(pk=accounting.operation_id)

        # one movement created
        movements = operation.operationmovement_set
        self.assertEqual(movements.count(), 1)

        # movement info
        movement = movements.first()
        self.assertMovement(
            test_movement=movement, test_account=test_account,
            test_movement_type=MOVEMENT_TYPE_INPUT, test_amount=test_amount)

    def test_save_withdraw_ready_then_draft_account(self):
        """
        Does ready withdraw and then change to draft and account
        """
        test_account1 = Account.objects.create(
            name='Test Account1',
            currency=CURRENCY_CUC,
            balance=1000)
        test_balance1 = test_account1.balance

        test_date = timezone.now()
        test_amount = 100
        test_status1 = STATUS_READY

        withdraw = Withdraw(
            date=test_date,
            account=test_account1,
            amount=test_amount,
            status=test_status1)

        withdraw = FinanceService.save_withdraw(
            user=self.test_user,
            withdraw=withdraw)

        # account balance incremented
        self.assertAccount(test_account=test_account1, test_balance=test_balance1 - test_amount)

        # document data auto filled
        self.assertDocument(withdraw, DOC_TYPE_WITHDRAW, test_account1.currency)

        # one finantial history created
        finantials = withdraw.finantialdocumenthistory_set
        self.assertEqual(finantials.count(), 1)

        # finantial history info
        finantial = finantials.first()
        self.assertFinantialHistory(
            test_finantial_history=finantial, test_document=withdraw, test_user=self.test_user,
            test_old_status=None, test_new_status=test_status1)

        # one accounting history created
        accountings = withdraw.accountingdocumenthistory_set
        self.assertEqual(accountings.count(), 1)

        # accounting history info
        accounting = accountings.first()
        operation = Operation.objects.get(pk=accounting.operation_id)

        # one movement created
        movements = operation.operationmovement_set
        self.assertEqual(movements.count(), 1)

        # movement info
        movement = movements.first()
        self.assertMovement(
            test_movement=movement, test_account=test_account1,
            test_movement_type=MOVEMENT_TYPE_OUTPUT, test_amount=test_amount)

        test_status2 = STATUS_DRAFT

        test_account2 = Account.objects.create(
            name='Test Account2',
            currency=CURRENCY_USD,
            balance=500)
        test_balance2 = test_account2.balance

        withdraw.status = test_status2
        withdraw.account = test_account2

        withdraw = FinanceService.save_withdraw(
            user=self.test_user,
            withdraw=withdraw)

        # account balance unchanged
        self.assertAccount(test_account=test_account1, test_balance=test_balance1)
        self.assertAccount(test_account=test_account2, test_balance=test_balance2)

        # document data auto filled
        self.assertDocument(withdraw, DOC_TYPE_WITHDRAW, test_account2.currency)

        # now two finantial history created
        finantials = withdraw.finantialdocumenthistory_set
        self.assertEqual(finantials.count(), 2)

        # new finantial history info
        finantial = finantials.last()
        self.assertFinantialHistory(
            test_finantial_history=finantial, test_document=withdraw, test_user=self.test_user,
            test_old_status=test_status1, test_new_status=test_status2)

        # extra accounting history created
        accountings = withdraw.accountingdocumenthistory_set
        self.assertEqual(accountings.count(), 2)

        # accounting history info
        accounting = accountings.last()
        operation = Operation.objects.get(pk=accounting.operation_id)

        # one movement created
        movements = operation.operationmovement_set
        self.assertEqual(movements.count(), 1)

        # movement info
        movement = movements.first()
        self.assertMovement(
            test_movement=movement, test_account=test_account1,
            test_movement_type=MOVEMENT_TYPE_INPUT, test_amount=test_amount)

    def test_save_withdraw_draft_then_amount(self):
        """
        Does draft withdraw and then change amount
        """
        test_account = Account.objects.create(
            name='Test Account',
            currency=CURRENCY_CUC,
            balance=1000)
        test_balance = test_account.balance

        test_date = timezone.now()
        test_amount1 = 100
        test_status = STATUS_DRAFT

        withdraw = Withdraw(
            date=test_date,
            account=test_account,
            amount=test_amount1,
            status=test_status)

        withdraw = FinanceService.save_withdraw(
            user=self.test_user,
            withdraw=withdraw)

        # account balance unchanged
        self.assertAccount(test_account=test_account, test_balance=test_balance)

        # document data auto filled
        self.assertDocument(withdraw, DOC_TYPE_WITHDRAW, test_account.currency)

        # one finantial history created
        finantials = withdraw.finantialdocumenthistory_set
        self.assertEqual(finantials.count(), 1)

        # finantial history info
        finantial = finantials.first()
        self.assertFinantialHistory(
            test_finantial_history=finantial, test_document=withdraw, test_user=self.test_user,
            test_old_status=None, test_new_status=test_status)

        # no accounting history created
        accountings = withdraw.accountingdocumenthistory_set
        self.assertEqual(accountings.count(), 0)

        test_amount2 = 50

        withdraw.amount = test_amount2

        withdraw = FinanceService.save_withdraw(
            user=self.test_user,
            withdraw=withdraw)

        # account balance unchanged
        self.assertAccount(test_account=test_account, test_balance=test_balance)

        # document data auto filled
        self.assertDocument(withdraw, DOC_TYPE_WITHDRAW, test_account.currency)

        # no aditional finantial history
        finantials = withdraw.finantialdocumenthistory_set
        self.assertEqual(finantials.count(), 1)

        # no accounting history created
        accountings = withdraw.accountingdocumenthistory_set
        self.assertEqual(accountings.count(), 0)

    def test_save_withdraw_ready_then_amount(self):
        """
        Does ready withdraw and then change amount
        """
        test_account = Account.objects.create(
            name='Test Account',
            currency=CURRENCY_CUC,
            balance=1000)
        test_balance = test_account.balance

        test_date = timezone.now()
        test_amount1 = 100
        test_status = STATUS_READY

        withdraw = Withdraw(
            date=test_date,
            account=test_account,
            amount=test_amount1,
            status=test_status)

        withdraw = FinanceService.save_withdraw(
            user=self.test_user,
            withdraw=withdraw)

        # account balance incremented
        self.assertAccount(test_account=test_account, test_balance=test_balance - test_amount1)

        # document data auto filled
        self.assertDocument(withdraw, DOC_TYPE_WITHDRAW, test_account.currency)

        # one finantial history created
        finantials = withdraw.finantialdocumenthistory_set
        self.assertEqual(finantials.count(), 1)

        # finantial history info
        finantial = finantials.first()
        self.assertFinantialHistory(
            test_finantial_history=finantial, test_document=withdraw, test_user=self.test_user,
            test_old_status=None, test_new_status=test_status)

        # one accounting history created
        accountings = withdraw.accountingdocumenthistory_set
        self.assertEqual(accountings.count(), 1)

        # accounting history info
        accounting = accountings.first()
        operation = Operation.objects.get(pk=accounting.operation_id)

        # one movement created
        movements = operation.operationmovement_set
        self.assertEqual(movements.count(), 1)

        # movement info
        movement = movements.first()
        self.assertMovement(
            test_movement=movement, test_account=test_account,
            test_movement_type=MOVEMENT_TYPE_OUTPUT, test_amount=test_amount1)

        test_amount2 = 50

        withdraw.amount = test_amount2

        withdraw = FinanceService.save_withdraw(
            user=self.test_user,
            withdraw=withdraw)

        # account balance updated
        self.assertAccount(test_account=test_account, test_balance=test_balance - test_amount2)

        # document data auto filled
        self.assertDocument(withdraw, DOC_TYPE_WITHDRAW, test_account.currency)

        # no aditional finantial history
        finantials = withdraw.finantialdocumenthistory_set
        self.assertEqual(finantials.count(), 1)

        # two accounting history created
        accountings = withdraw.accountingdocumenthistory_set
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
            test_movement=movement, test_account=test_account,
            test_movement_type=MOVEMENT_TYPE_INPUT, test_amount=test_amount1)

        # accounting history info
        accounting = elements[2]
        operation = Operation.objects.get(pk=accounting.operation_id)

        # one movement created
        movements = operation.operationmovement_set
        self.assertEqual(movements.count(), 1)

        # movement info
        movement = movements.first()
        self.assertMovement(
            test_movement=movement, test_account=test_account,
            test_movement_type=MOVEMENT_TYPE_OUTPUT, test_amount=test_amount2)

    def test_save_withdraw_draft_then_account(self):
        """
        Does draft withdraw and then change account
        """
        test_account1 = Account.objects.create(
            name='Test Account1',
            currency=CURRENCY_CUC,
            balance=1000)
        test_balance1 = test_account1.balance

        test_date = timezone.now()
        test_amount = 100
        test_status = STATUS_DRAFT

        withdraw = Withdraw(
            date=test_date,
            account=test_account1,
            amount=test_amount,
            status=test_status)

        withdraw = FinanceService.save_withdraw(
            user=self.test_user,
            withdraw=withdraw)

        # account balance unchanged
        self.assertAccount(test_account=test_account1, test_balance=test_balance1)

        # document data auto filled
        self.assertDocument(withdraw, DOC_TYPE_WITHDRAW, test_account1.currency)

        # one finantial history created
        finantials = withdraw.finantialdocumenthistory_set
        self.assertEqual(finantials.count(), 1)

        # finantial history info
        finantial = finantials.first()
        self.assertFinantialHistory(
            test_finantial_history=finantial, test_document=withdraw, test_user=self.test_user,
            test_old_status=None, test_new_status=test_status)

        # no accounting history created
        accountings = withdraw.accountingdocumenthistory_set
        self.assertEqual(accountings.count(), 0)

        test_account2 = Account.objects.create(
            name='Test Account2',
            currency=CURRENCY_USD,
            balance=500)
        test_balance2 = test_account2.balance

        withdraw.account = test_account2

        withdraw = FinanceService.save_withdraw(
            user=self.test_user,
            withdraw=withdraw)

        # account balance unchanged
        self.assertAccount(test_account=test_account2, test_balance=test_balance2)

        # document data auto filled
        self.assertDocument(withdraw, DOC_TYPE_WITHDRAW, test_account2.currency)

        # no aditional finantial history
        finantials = withdraw.finantialdocumenthistory_set
        self.assertEqual(finantials.count(), 1)

        # no accounting history created
        accountings = withdraw.accountingdocumenthistory_set
        self.assertEqual(accountings.count(), 0)

    def test_save_withdraw_ready_then_account(self):
        """
        Does ready withdraw and then change account
        """
        test_account1 = Account.objects.create(
            name='Test Account1',
            currency=CURRENCY_CUC,
            balance=1000)
        test_balance1 = test_account1.balance

        test_date = timezone.now()
        test_amount = 100
        test_status = STATUS_READY

        withdraw = Withdraw(
            date=test_date,
            account=test_account1,
            amount=test_amount,
            status=test_status)

        withdraw = FinanceService.save_withdraw(
            user=self.test_user,
            withdraw=withdraw)

        # account balance incremented
        self.assertAccount(test_account=test_account1, test_balance=test_balance1 - test_amount)

        # document data auto filled
        self.assertDocument(withdraw, DOC_TYPE_WITHDRAW, test_account1.currency)

        # one finantial history created
        finantials = withdraw.finantialdocumenthistory_set
        self.assertEqual(finantials.count(), 1)

        # finantial history info
        finantial = finantials.first()
        self.assertFinantialHistory(
            test_finantial_history=finantial, test_document=withdraw, test_user=self.test_user,
            test_old_status=None, test_new_status=test_status)

        # one accounting history created
        accountings = withdraw.accountingdocumenthistory_set
        self.assertEqual(accountings.count(), 1)

        # accounting history info
        accounting = accountings.first()
        operation = Operation.objects.get(pk=accounting.operation_id)

        # one movement created
        movements = operation.operationmovement_set
        self.assertEqual(movements.count(), 1)

        # movement info
        movement = movements.first()
        self.assertMovement(
            test_movement=movement, test_account=test_account1,
            test_movement_type=MOVEMENT_TYPE_OUTPUT, test_amount=test_amount)

        test_account2 = Account.objects.create(
            name='Test Account2',
            currency=CURRENCY_USD,
            balance=500)
        test_balance2 = test_account2.balance

        withdraw.account = test_account2

        withdraw = FinanceService.save_withdraw(
            user=self.test_user,
            withdraw=withdraw)

        # account balance updated
        self.assertAccount(test_account=test_account1, test_balance=test_balance1)
        self.assertAccount(test_account=test_account2, test_balance=test_balance2 - test_amount)

        # document data auto filled
        self.assertDocument(withdraw, DOC_TYPE_WITHDRAW, test_account2.currency)

        # no aditional finantial history
        finantials = withdraw.finantialdocumenthistory_set
        self.assertEqual(finantials.count(), 1)

        # two accounting history created
        accountings = withdraw.accountingdocumenthistory_set
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
            test_movement=movement, test_account=test_account1,
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
            test_movement=movement, test_account=test_account2,
            test_movement_type=MOVEMENT_TYPE_OUTPUT, test_amount=test_amount)

    def test_save_withdraw_ready_then_amount_account(self):
        """
        Does ready withdraw and then change amount and account
        """
        test_account1 = Account.objects.create(
            name='Test Account1',
            currency=CURRENCY_CUC,
            balance=1000)
        test_balance1 = test_account1.balance

        test_date = timezone.now()
        test_amount1 = 100
        test_status = STATUS_READY

        withdraw = Withdraw(
            date=test_date,
            account=test_account1,
            amount=test_amount1,
            status=test_status)

        withdraw = FinanceService.save_withdraw(
            user=self.test_user,
            withdraw=withdraw)

        # account balance incremented
        self.assertAccount(test_account=test_account1, test_balance=test_balance1 - test_amount1)

        # document data auto filled
        self.assertDocument(withdraw, DOC_TYPE_WITHDRAW, test_account1.currency)

        # one finantial history created
        finantials = withdraw.finantialdocumenthistory_set
        self.assertEqual(finantials.count(), 1)

        # finantial history info
        finantial = finantials.first()
        self.assertFinantialHistory(
            test_finantial_history=finantial, test_document=withdraw, test_user=self.test_user,
            test_old_status=None, test_new_status=test_status)

        # one accounting history created
        accountings = withdraw.accountingdocumenthistory_set
        self.assertEqual(accountings.count(), 1)

        # accounting history info
        accounting = accountings.first()
        operation = Operation.objects.get(pk=accounting.operation_id)

        # one movement created
        movements = operation.operationmovement_set
        self.assertEqual(movements.count(), 1)

        # movement info
        movement = movements.first()
        self.assertMovement(
            test_movement=movement, test_account=test_account1,
            test_movement_type=MOVEMENT_TYPE_OUTPUT, test_amount=test_amount1)

        test_account2 = Account.objects.create(
            name='Test Account2',
            currency=CURRENCY_USD,
            balance=500)
        test_balance2 = test_account2.balance

        test_amount2 = 50

        withdraw.account = test_account2
        withdraw.amount = test_amount2

        withdraw = FinanceService.save_withdraw(
            user=self.test_user,
            withdraw=withdraw)

        # account balance updated
        self.assertAccount(test_account=test_account1, test_balance=test_balance1)
        self.assertAccount(test_account=test_account2, test_balance=test_balance2 - test_amount2)

        # document data auto filled
        self.assertDocument(withdraw, DOC_TYPE_WITHDRAW, test_account2.currency)

        # no aditional finantial history
        finantials = withdraw.finantialdocumenthistory_set
        self.assertEqual(finantials.count(), 1)

        # two accounting history created
        accountings = withdraw.accountingdocumenthistory_set
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
            test_movement=movement, test_account=test_account1,
            test_movement_type=MOVEMENT_TYPE_INPUT, test_amount=test_amount1)

        # accounting history info
        accounting = elements[2]
        operation = Operation.objects.get(pk=accounting.operation_id)

        # one movement created
        movements = operation.operationmovement_set
        self.assertEqual(movements.count(), 1)

        # movement info
        movement = movements.first()
        self.assertMovement(
            test_movement=movement, test_account=test_account2,
            test_movement_type=MOVEMENT_TYPE_OUTPUT, test_amount=test_amount2)

    def test_save_withdraw_draft_then_date(self):
        """
        Does draft withdraw and then change date
        """
        test_account = Account.objects.create(
            name='Test Account',
            currency=CURRENCY_CUC,
            balance=1000)
        test_balance = test_account.balance

        test_date1 = timezone.now()
        test_amount = 100
        test_status = STATUS_DRAFT

        withdraw = Withdraw(
            date=test_date1,
            account=test_account,
            amount=test_amount,
            status=test_status)

        withdraw = FinanceService.save_withdraw(
            user=self.test_user,
            withdraw=withdraw)

        test_name1 = withdraw.name

        # account balance unchanged
        self.assertAccount(test_account=test_account, test_balance=test_balance)

        # document data auto filled
        self.assertDocument(withdraw, DOC_TYPE_WITHDRAW, test_account.currency)

        # one finantial history created
        finantials = withdraw.finantialdocumenthistory_set
        self.assertEqual(finantials.count(), 1)

        # finantial history info
        finantial = finantials.first()
        self.assertFinantialHistory(
            test_finantial_history=finantial, test_document=withdraw, test_user=self.test_user,
            test_old_status=None, test_new_status=test_status)

        # no accounting history created
        accountings = withdraw.accountingdocumenthistory_set
        self.assertEqual(accountings.count(), 0)

        test_date2 = test_date1 - timedelta(days=5)

        withdraw.date = test_date2

        withdraw = FinanceService.save_withdraw(
            user=self.test_user,
            withdraw=withdraw)

        test_name2 = withdraw.name

        # name changed
        self.assertNotEqual(test_name1, test_name2)

        # account balance unchanged
        self.assertAccount(test_account=test_account, test_balance=test_balance)

        # document data auto filled
        self.assertDocument(withdraw, DOC_TYPE_WITHDRAW, test_account.currency)

        # no finantial history created
        finantials = withdraw.finantialdocumenthistory_set
        self.assertEqual(finantials.count(), 1)

        # no accounting history created
        accountings = withdraw.accountingdocumenthistory_set
        self.assertEqual(accountings.count(), 0)

    def test_save_withdraw_ready_then_date(self):
        """
        Does ready withdraw and then change to draft
        """
        test_account = Account.objects.create(
            name='Test Account',
            currency=CURRENCY_CUC,
            balance=1000)
        test_balance = test_account.balance

        test_date1 = timezone.now()
        test_amount = 100
        test_status = STATUS_READY

        withdraw = Withdraw(
            date=test_date1,
            account=test_account,
            amount=test_amount,
            status=test_status)

        withdraw = FinanceService.save_withdraw(
            user=self.test_user,
            withdraw=withdraw)

        test_name1 = withdraw.name

        # account balance incremented
        self.assertAccount(test_account=test_account, test_balance=test_balance - test_amount)

        # document data auto filled
        self.assertDocument(withdraw, DOC_TYPE_WITHDRAW, test_account.currency)

        # one finantial history created
        finantials = withdraw.finantialdocumenthistory_set
        self.assertEqual(finantials.count(), 1)

        # finantial history info
        finantial = finantials.first()
        self.assertFinantialHistory(
            test_finantial_history=finantial, test_document=withdraw, test_user=self.test_user,
            test_old_status=None, test_new_status=test_status)

        # one accounting history created
        accountings = withdraw.accountingdocumenthistory_set
        self.assertEqual(accountings.count(), 1)

        # accounting history info
        accounting = accountings.first()
        operation = Operation.objects.get(pk=accounting.operation_id)

        # one movement created
        movements = operation.operationmovement_set
        self.assertEqual(movements.count(), 1)

        # movement info
        movement = movements.first()
        self.assertMovement(
            test_movement=movement, test_account=test_account,
            test_movement_type=MOVEMENT_TYPE_OUTPUT, test_amount=test_amount)

        test_date2 = test_date1 - timedelta(days=5)

        withdraw.date = test_date2

        withdraw = FinanceService.save_withdraw(
            user=self.test_user,
            withdraw=withdraw)

        test_name2 = withdraw.name

        # name changed
        self.assertNotEqual(test_name1, test_name2)

        # account balance remains changed
        self.assertAccount(test_account=test_account, test_balance=test_balance - test_amount)

        # document data auto filled
        self.assertDocument(withdraw, DOC_TYPE_WITHDRAW, test_account.currency)

        # same finantial history
        finantials = withdraw.finantialdocumenthistory_set
        self.assertEqual(finantials.count(), 1)

        # same accounting history
        accountings = withdraw.accountingdocumenthistory_set
        self.assertEqual(accountings.count(), 1)
