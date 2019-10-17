from datetime import timedelta

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone

from accounting.constants import (
    MOVEMENT_TYPE_INPUT, MOVEMENT_TYPE_OUTPUT, CURRENCY_CUC, CURRENCY_USD, ERROR_SAME_CURRENCY)
from accounting.models import Account, Operation

from finance.constants import STATUS_DRAFT, STATUS_READY, DOC_TYPE_CURRENCY_EXCHANGE
from finance.models import CurrencyExchange
from finance.services import FinanceServices
from finance.tests.utils import FinanceBaseTestCase


class FinanceServicesTestCase(FinanceBaseTestCase):

    test_user = None

    def setUp(self):
        self.test_user = User.objects.create(
            username="Test User")

    def test_save_currency_exchange_status_draft(self):
        """
        Does draft currency_exchange
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
        test_amount1 = 100
        test_amount2 = 50
        test_status = STATUS_DRAFT

        currency_exchange = CurrencyExchange(
            date=test_date,
            account=test_account1,
            exchange_account=test_account2,
            amount=test_amount1,
            exchange_amount=test_amount2,
            status=test_status)

        currency_exchange = FinanceServices.save_currency_exchange(
            user=self.test_user,
            currency_exchange=currency_exchange)

        # account balance unchanged
        self.assertAccount(test_account=test_account1, test_balance=test_balance1)
        self.assertAccount(test_account=test_account2, test_balance=test_balance2)

        # document data auto filled
        self.assertDocument(currency_exchange, DOC_TYPE_CURRENCY_EXCHANGE, test_account1.currency)

        # one finantial history created
        finantials = currency_exchange.finantialdocumenthistory_set
        self.assertEqual(finantials.count(), 1)

        # finantial history info
        finantial = finantials.first()
        self.assertFinantialHistory(
            test_finantial_history=finantial, test_document=currency_exchange, test_user=self.test_user,
            test_old_status=None, test_new_status=test_status)

        # no accounting history created
        accountings = currency_exchange.accountingdocumenthistory_set
        self.assertEqual(accountings.count(), 0)

    def test_save_currency_exchange_status_ready(self):
        """
        Does ready currency_exchange
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
        test_amount1 = 100
        test_amount2 = 50
        test_status = STATUS_READY

        currency_exchange = CurrencyExchange(
            date=test_date,
            account=test_account1,
            exchange_account=test_account2,
            amount=test_amount1,
            exchange_amount=test_amount2,
            status=test_status)

        currency_exchange = FinanceServices.save_currency_exchange(
            user=self.test_user,
            currency_exchange=currency_exchange)

        # account balance incremented
        self.assertAccount(test_account=test_account1, test_balance=test_balance1 + test_amount1)
        self.assertAccount(test_account=test_account2, test_balance=test_balance2 - test_amount2)

        # document data auto filled
        self.assertDocument(currency_exchange, DOC_TYPE_CURRENCY_EXCHANGE, test_account1.currency)

        # one finantial history created
        finantials = currency_exchange.finantialdocumenthistory_set
        self.assertEqual(finantials.count(), 1)

        # finantial history info
        finantial = finantials.first()
        self.assertFinantialHistory(
            test_finantial_history=finantial, test_document=currency_exchange, test_user=self.test_user,
            test_old_status=None, test_new_status=test_status)

        # one accounting history created
        accountings = currency_exchange.accountingdocumenthistory_set
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
            test_movement_type=MOVEMENT_TYPE_OUTPUT, test_amount=test_amount2)

    def test_save_currency_exchange_draft_then_ready(self):
        """
        Does draft currency_exchange and then change to ready
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
        test_amount1 = 100
        test_amount2 = 50
        test_status1 = STATUS_DRAFT

        currency_exchange = CurrencyExchange(
            date=test_date,
            account=test_account1,
            exchange_account=test_account2,
            amount=test_amount1,
            exchange_amount=test_amount2,
            status=test_status1)

        currency_exchange = FinanceServices.save_currency_exchange(
            user=self.test_user,
            currency_exchange=currency_exchange)

        # account balance unchanged
        self.assertAccount(test_account=test_account1, test_balance=test_balance1)
        self.assertAccount(test_account=test_account2, test_balance=test_balance2)

        # document data auto filled
        self.assertDocument(currency_exchange, DOC_TYPE_CURRENCY_EXCHANGE, test_account1.currency)

        # one finantial history created
        finantials = currency_exchange.finantialdocumenthistory_set
        self.assertEqual(finantials.count(), 1)

        # finantial history info
        finantial = finantials.first()
        self.assertFinantialHistory(
            test_finantial_history=finantial, test_document=currency_exchange, test_user=self.test_user,
            test_old_status=None, test_new_status=test_status1)

        # no accounting history created
        accountings = currency_exchange.accountingdocumenthistory_set
        self.assertEqual(accountings.count(), 0)

        test_status2 = STATUS_READY

        currency_exchange.status = test_status2

        currency_exchange = FinanceServices.save_currency_exchange(
            user=self.test_user,
            currency_exchange=currency_exchange)

        # account balance incremented
        self.assertAccount(test_account=test_account1, test_balance=test_balance1 + test_amount1)
        self.assertAccount(test_account=test_account2, test_balance=test_balance2 - test_amount2)

        # document data auto filled
        self.assertDocument(currency_exchange, DOC_TYPE_CURRENCY_EXCHANGE, test_account1.currency)

        # now two finantial history created
        finantials = currency_exchange.finantialdocumenthistory_set
        self.assertEqual(finantials.count(), 2)

        # new finantial history info
        finantial = finantials.last()
        self.assertFinantialHistory(
            test_finantial_history=finantial, test_document=currency_exchange, test_user=self.test_user,
            test_old_status=test_status1, test_new_status=test_status2)
        # one accounting history created
        accountings = currency_exchange.accountingdocumenthistory_set
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
            test_movement_type=MOVEMENT_TYPE_OUTPUT, test_amount=test_amount2)


    def test_save_currency_exchange_ready_then_draft(self):
        """
        Does ready currency_exchange and then change to draft
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
        test_amount1 = 100
        test_amount2 = 50
        test_status1 = STATUS_READY

        currency_exchange = CurrencyExchange(
            date=test_date,
            account=test_account1,
            exchange_account=test_account2,
            amount=test_amount1,
            exchange_amount=test_amount2,
            status=test_status1)

        currency_exchange = FinanceServices.save_currency_exchange(
            user=self.test_user,
            currency_exchange=currency_exchange)

        # account balance incremented
        self.assertAccount(test_account=test_account1, test_balance=test_balance1 + test_amount1)
        self.assertAccount(test_account=test_account2, test_balance=test_balance2 - test_amount2)

        # document data auto filled
        self.assertDocument(currency_exchange, DOC_TYPE_CURRENCY_EXCHANGE, test_account1.currency)

        # one finantial history created
        finantials = currency_exchange.finantialdocumenthistory_set
        self.assertEqual(finantials.count(), 1)

        # finantial history info
        finantial = finantials.first()
        self.assertFinantialHistory(
            test_finantial_history=finantial, test_document=currency_exchange, test_user=self.test_user,
            test_old_status=None, test_new_status=test_status1)

        # one accounting history created
        accountings = currency_exchange.accountingdocumenthistory_set
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
        movement = movements.last()
        self.assertMovement(
            test_movement=movement, test_account=test_account2,
            test_movement_type=MOVEMENT_TYPE_OUTPUT, test_amount=test_amount2)

        test_status2 = STATUS_DRAFT

        currency_exchange.status = test_status2

        currency_exchange = FinanceServices.save_currency_exchange(
            user=self.test_user,
            currency_exchange=currency_exchange)

        # account balance unchanged
        self.assertAccount(test_account=test_account1, test_balance=test_balance1)
        self.assertAccount(test_account=test_account2, test_balance=test_balance2)

        # document data auto filled
        self.assertDocument(currency_exchange, DOC_TYPE_CURRENCY_EXCHANGE, test_account1.currency)

        # now two finantial history created
        finantials = currency_exchange.finantialdocumenthistory_set
        self.assertEqual(finantials.count(), 2)

        # new finantial history info
        finantial = finantials.last()
        self.assertFinantialHistory(
            test_finantial_history=finantial, test_document=currency_exchange, test_user=self.test_user,
            test_old_status=test_status1, test_new_status=test_status2)

        # extra accounting history created
        accountings = currency_exchange.accountingdocumenthistory_set
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
            test_movement_type=MOVEMENT_TYPE_INPUT, test_amount=test_amount2)

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
            test_movement_type=MOVEMENT_TYPE_OUTPUT, test_amount=test_amount1)

    def test_save_currency_exchange_ready_then_draft_account(self):
        """
        Does ready currency_exchange and then change to draft and account
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
        test_amount1 = 100
        test_amount2 = 50
        test_status1 = STATUS_READY

        currency_exchange = CurrencyExchange(
            date=test_date,
            account=test_account1,
            exchange_account=test_account2,
            amount=test_amount1,
            exchange_amount=test_amount2,
            status=test_status1)

        currency_exchange = FinanceServices.save_currency_exchange(
            user=self.test_user,
            currency_exchange=currency_exchange)

        # account balance changed
        self.assertAccount(test_account=test_account1, test_balance=test_balance1 + test_amount1)
        self.assertAccount(test_account=test_account2, test_balance=test_balance2 - test_amount2)

        # document data auto filled
        self.assertDocument(currency_exchange, DOC_TYPE_CURRENCY_EXCHANGE, test_account1.currency)

        # one finantial history created
        finantials = currency_exchange.finantialdocumenthistory_set
        self.assertEqual(finantials.count(), 1)

        # finantial history info
        finantial = finantials.first()
        self.assertFinantialHistory(
            test_finantial_history=finantial, test_document=currency_exchange, test_user=self.test_user,
            test_old_status=None, test_new_status=test_status1)

        # one accounting history created
        accountings = currency_exchange.accountingdocumenthistory_set
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
            test_movement_type=MOVEMENT_TYPE_OUTPUT, test_amount=test_amount2)

        test_status2 = STATUS_DRAFT

        test_account3 = Account.objects.create(
            name='Test Account3',
            currency=CURRENCY_USD)
        test_balance3 = test_account3.balance
        test_account4 = Account.objects.create(
            name='Test Account4',
            currency=CURRENCY_CUC,
            balance=500)
        test_balance4 = test_account4.balance

        currency_exchange.status = test_status2
        currency_exchange.account = test_account3
        currency_exchange.exchange_account = test_account4

        currency_exchange = FinanceServices.save_currency_exchange(
            user=self.test_user,
            currency_exchange=currency_exchange)

        # account balance unchanged
        self.assertAccount(test_account=test_account1, test_balance=test_balance1)
        self.assertAccount(test_account=test_account2, test_balance=test_balance2)
        self.assertAccount(test_account=test_account3, test_balance=test_balance3)
        self.assertAccount(test_account=test_account4, test_balance=test_balance4)

        # document data auto filled
        self.assertDocument(currency_exchange, DOC_TYPE_CURRENCY_EXCHANGE, test_account3.currency)

        # now two finantial history created
        finantials = currency_exchange.finantialdocumenthistory_set
        self.assertEqual(finantials.count(), 2)

        # new finantial history info
        finantial = finantials.last()
        self.assertFinantialHistory(
            test_finantial_history=finantial, test_document=currency_exchange, test_user=self.test_user,
            test_old_status=test_status1, test_new_status=test_status2)

        # extra accounting history created
        accountings = currency_exchange.accountingdocumenthistory_set
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
            test_movement_type=MOVEMENT_TYPE_INPUT, test_amount=test_amount2)

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
            test_movement_type=MOVEMENT_TYPE_OUTPUT, test_amount=test_amount1)

    def test_save_currency_exchange_draft_then_amount(self):
        """
        Does draft currency_exchange and then change amount
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
        test_amount1 = 100
        test_amount2 = 50
        test_status = STATUS_DRAFT

        currency_exchange = CurrencyExchange(
            date=test_date,
            account=test_account1,
            exchange_account=test_account2,
            amount=test_amount1,
            exchange_amount=test_amount2,
            status=test_status)

        currency_exchange = FinanceServices.save_currency_exchange(
            user=self.test_user,
            currency_exchange=currency_exchange)

        # account balance unchanged
        self.assertAccount(test_account=test_account1, test_balance=test_balance1)
        self.assertAccount(test_account=test_account2, test_balance=test_balance2)

        # document data auto filled
        self.assertDocument(currency_exchange, DOC_TYPE_CURRENCY_EXCHANGE, test_account1.currency)

        # one finantial history created
        finantials = currency_exchange.finantialdocumenthistory_set
        self.assertEqual(finantials.count(), 1)

        # finantial history info
        finantial = finantials.first()
        self.assertFinantialHistory(
            test_finantial_history=finantial, test_document=currency_exchange, test_user=self.test_user,
            test_old_status=None, test_new_status=test_status)

        # no accounting history created
        accountings = currency_exchange.accountingdocumenthistory_set
        self.assertEqual(accountings.count(), 0)

        test_amount3 = 400
        test_amount4 = 200

        currency_exchange.amount = test_amount3
        currency_exchange.exchange_amount = test_amount4

        currency_exchange = FinanceServices.save_currency_exchange(
            user=self.test_user,
            currency_exchange=currency_exchange)

        # account balance unchanged
        self.assertAccount(test_account=test_account1, test_balance=test_balance1)
        self.assertAccount(test_account=test_account2, test_balance=test_balance2)

        # document data auto filled
        self.assertDocument(currency_exchange, DOC_TYPE_CURRENCY_EXCHANGE, test_account1.currency)

        # no aditional finantial history
        finantials = currency_exchange.finantialdocumenthistory_set
        self.assertEqual(finantials.count(), 1)

        # no accounting history created
        accountings = currency_exchange.accountingdocumenthistory_set
        self.assertEqual(accountings.count(), 0)

    def test_save_currency_exchange_ready_then_amount(self):
        """
        Does ready currency_exchange and then change amount
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
        test_amount1 = 100
        test_amount2 = 50
        test_status = STATUS_READY

        currency_exchange = CurrencyExchange(
            date=test_date,
            account=test_account1,
            exchange_account=test_account2,
            amount=test_amount1,
            exchange_amount=test_amount2,
            status=test_status)

        currency_exchange = FinanceServices.save_currency_exchange(
            user=self.test_user,
            currency_exchange=currency_exchange)

        # account balance incremented
        self.assertAccount(test_account=test_account1, test_balance=test_balance1 + test_amount1)
        self.assertAccount(test_account=test_account2, test_balance=test_balance2 - test_amount2)

        # document data auto filled
        self.assertDocument(currency_exchange, DOC_TYPE_CURRENCY_EXCHANGE, test_account1.currency)

        # one finantial history created
        finantials = currency_exchange.finantialdocumenthistory_set
        self.assertEqual(finantials.count(), 1)

        # finantial history info
        finantial = finantials.first()
        self.assertFinantialHistory(
            test_finantial_history=finantial, test_document=currency_exchange, test_user=self.test_user,
            test_old_status=None, test_new_status=test_status)

        # one accounting history created
        accountings = currency_exchange.accountingdocumenthistory_set
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
            test_movement_type=MOVEMENT_TYPE_OUTPUT, test_amount=test_amount2)

        test_amount3 = 400
        test_amount4 = 200

        currency_exchange.amount = test_amount3
        currency_exchange.exchange_amount = test_amount4

        currency_exchange = FinanceServices.save_currency_exchange(
            user=self.test_user,
            currency_exchange=currency_exchange)

        # account balance updated
        self.assertAccount(test_account=test_account1, test_balance=test_balance1 + test_amount3)
        self.assertAccount(test_account=test_account2, test_balance=test_balance2 - test_amount4)

        # document data auto filled
        self.assertDocument(currency_exchange, DOC_TYPE_CURRENCY_EXCHANGE, test_account1.currency)

        # no aditional finantial history
        finantials = currency_exchange.finantialdocumenthistory_set
        self.assertEqual(finantials.count(), 1)

        # two accounting history created
        accountings = currency_exchange.accountingdocumenthistory_set
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
            test_movement_type=MOVEMENT_TYPE_INPUT, test_amount=test_amount2)

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
            test_movement_type=MOVEMENT_TYPE_INPUT, test_amount=test_amount3)
        # movement info
        movement = movements.last()
        self.assertMovement(
            test_movement=movement, test_account=test_account2,
            test_movement_type=MOVEMENT_TYPE_OUTPUT, test_amount=test_amount4)

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

    def test_save_currency_exchange_draft_then_account(self):
        """
        Does draft currency_exchange and then change account
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
        test_amount1 = 100
        test_amount2 = 50
        test_status = STATUS_DRAFT

        currency_exchange = CurrencyExchange(
            date=test_date,
            account=test_account1,
            exchange_account=test_account2,
            amount=test_amount1,
            exchange_amount=test_amount2,
            status=test_status)

        currency_exchange = FinanceServices.save_currency_exchange(
            user=self.test_user,
            currency_exchange=currency_exchange)

        # account balance unchanged
        self.assertAccount(test_account=test_account1, test_balance=test_balance1)
        self.assertAccount(test_account=test_account2, test_balance=test_balance2)

        # document data auto filled
        self.assertDocument(currency_exchange, DOC_TYPE_CURRENCY_EXCHANGE, test_account1.currency)

        # one finantial history created
        finantials = currency_exchange.finantialdocumenthistory_set
        self.assertEqual(finantials.count(), 1)

        # finantial history info
        finantial = finantials.first()
        self.assertFinantialHistory(
            test_finantial_history=finantial, test_document=currency_exchange, test_user=self.test_user,
            test_old_status=None, test_new_status=test_status)

        # no accounting history created
        accountings = currency_exchange.accountingdocumenthistory_set
        self.assertEqual(accountings.count(), 0)

        test_account3 = Account.objects.create(
            name='Test Account3',
            currency=CURRENCY_USD)
        test_balance3 = test_account3.balance
        test_account4 = Account.objects.create(
            name='Test Account4',
            currency=CURRENCY_CUC,
            balance=500)
        test_balance4 = test_account4.balance

        currency_exchange.account = test_account3
        currency_exchange.exchange_account = test_account4

        currency_exchange = FinanceServices.save_currency_exchange(
            user=self.test_user,
            currency_exchange=currency_exchange)

        # account balance unchanged
        self.assertAccount(test_account=test_account1, test_balance=test_balance1)
        self.assertAccount(test_account=test_account2, test_balance=test_balance2)
        self.assertAccount(test_account=test_account3, test_balance=test_balance3)
        self.assertAccount(test_account=test_account4, test_balance=test_balance4)

        # document data auto filled
        self.assertDocument(currency_exchange, DOC_TYPE_CURRENCY_EXCHANGE, test_account3.currency)

        # no aditional finantial history
        finantials = currency_exchange.finantialdocumenthistory_set
        self.assertEqual(finantials.count(), 1)

        # no accounting history created
        accountings = currency_exchange.accountingdocumenthistory_set
        self.assertEqual(accountings.count(), 0)

    def test_save_currency_exchange_ready_then_account(self):
        """
        Does ready currency_exchange and then change account
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
        test_amount1 = 100
        test_amount2 = 50
        test_status = STATUS_READY

        currency_exchange = CurrencyExchange(
            date=test_date,
            account=test_account1,
            exchange_account=test_account2,
            amount=test_amount1,
            exchange_amount=test_amount2,
            status=test_status)

        currency_exchange = FinanceServices.save_currency_exchange(
            user=self.test_user,
            currency_exchange=currency_exchange)

        # account balance incremented
        self.assertAccount(test_account=test_account1, test_balance=test_balance1 + test_amount1)
        self.assertAccount(test_account=test_account2, test_balance=test_balance2 - test_amount2)

        # document data auto filled
        self.assertDocument(currency_exchange, DOC_TYPE_CURRENCY_EXCHANGE, test_account1.currency)

        # one finantial history created
        finantials = currency_exchange.finantialdocumenthistory_set
        self.assertEqual(finantials.count(), 1)

        # finantial history info
        finantial = finantials.first()
        self.assertFinantialHistory(
            test_finantial_history=finantial, test_document=currency_exchange, test_user=self.test_user,
            test_old_status=None, test_new_status=test_status)

        # one accounting history created
        accountings = currency_exchange.accountingdocumenthistory_set
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
            test_movement_type=MOVEMENT_TYPE_OUTPUT, test_amount=test_amount2)

        test_account3 = Account.objects.create(
            name='Test Account3',
            currency=CURRENCY_USD)
        test_balance3 = test_account3.balance
        test_account4 = Account.objects.create(
            name='Test Account4',
            currency=CURRENCY_CUC,
            balance=500)
        test_balance4 = test_account4.balance

        currency_exchange.account = test_account3
        currency_exchange.exchange_account = test_account4

        currency_exchange = FinanceServices.save_currency_exchange(
            user=self.test_user,
            currency_exchange=currency_exchange)

        # account balance updated
        self.assertAccount(test_account=test_account1, test_balance=test_balance1)
        self.assertAccount(test_account=test_account2, test_balance=test_balance2)
        self.assertAccount(test_account=test_account3, test_balance=test_balance3 + test_amount1)
        self.assertAccount(test_account=test_account4, test_balance=test_balance4 - test_amount2)

        # document data auto filled
        self.assertDocument(currency_exchange, DOC_TYPE_CURRENCY_EXCHANGE, test_account3.currency)

        # no aditional finantial history
        finantials = currency_exchange.finantialdocumenthistory_set
        self.assertEqual(finantials.count(), 1)

        # 3 accounting history created
        accountings = currency_exchange.accountingdocumenthistory_set
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
            test_movement_type=MOVEMENT_TYPE_INPUT, test_amount=test_amount2)

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
            test_movement_type=MOVEMENT_TYPE_INPUT, test_amount=test_amount1)
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

    def test_save_currency_exchange_ready_then_amount_account(self):
        """
        Does ready currency_exchange and then change amount and account
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
        test_amount1 = 100
        test_amount2 = 50
        test_status = STATUS_READY

        currency_exchange = CurrencyExchange(
            date=test_date,
            account=test_account1,
            exchange_account=test_account2,
            amount=test_amount1,
            exchange_amount=test_amount2,
            status=test_status)

        currency_exchange = FinanceServices.save_currency_exchange(
            user=self.test_user,
            currency_exchange=currency_exchange)

        # account balance incremented
        self.assertAccount(test_account=test_account1, test_balance=test_balance1 + test_amount1)
        self.assertAccount(test_account=test_account2, test_balance=test_balance2 - test_amount2)

        # document data auto filled
        self.assertDocument(currency_exchange, DOC_TYPE_CURRENCY_EXCHANGE, test_account1.currency)

        # one finantial history created
        finantials = currency_exchange.finantialdocumenthistory_set
        self.assertEqual(finantials.count(), 1)

        # finantial history info
        finantial = finantials.first()
        self.assertFinantialHistory(
            test_finantial_history=finantial, test_document=currency_exchange, test_user=self.test_user,
            test_old_status=None, test_new_status=test_status)

        # one accounting history created
        accountings = currency_exchange.accountingdocumenthistory_set
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
            test_movement_type=MOVEMENT_TYPE_OUTPUT, test_amount=test_amount2)

        test_account3 = Account.objects.create(
            name='Test Account3',
            currency=CURRENCY_USD)
        test_balance3 = test_account3.balance
        test_account4 = Account.objects.create(
            name='Test Account4',
            currency=CURRENCY_CUC,
            balance=500)
        test_balance4 = test_account4.balance

        test_amount3 = 400
        test_amount4 = 200

        currency_exchange.account = test_account3
        currency_exchange.exchange_account = test_account4
        currency_exchange.amount = test_amount3
        currency_exchange.exchange_amount = test_amount4

        currency_exchange = FinanceServices.save_currency_exchange(
            user=self.test_user,
            currency_exchange=currency_exchange)

        # account balance updated
        self.assertAccount(test_account=test_account1, test_balance=test_balance1)
        self.assertAccount(test_account=test_account2, test_balance=test_balance2)
        self.assertAccount(test_account=test_account3, test_balance=test_balance3 + test_amount3)
        self.assertAccount(test_account=test_account4, test_balance=test_balance4 - test_amount4)

        # document data auto filled
        self.assertDocument(currency_exchange, DOC_TYPE_CURRENCY_EXCHANGE, test_account3.currency)

        # no aditional finantial history
        finantials = currency_exchange.finantialdocumenthistory_set
        self.assertEqual(finantials.count(), 1)

        # 3 accounting history created
        accountings = currency_exchange.accountingdocumenthistory_set
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
            test_movement_type=MOVEMENT_TYPE_INPUT, test_amount=test_amount2)

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
            test_movement_type=MOVEMENT_TYPE_INPUT, test_amount=test_amount3)
        # movement info
        movement = movements.last()
        self.assertMovement(
            test_movement=movement, test_account=test_account4,
            test_movement_type=MOVEMENT_TYPE_OUTPUT, test_amount=test_amount4)

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

    def test_save_currency_exchange_draft_then_date(self):
        """
        Does draft currency_exchange and then change date
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

        test_date1 = timezone.now()
        test_amount1 = 100
        test_amount2 = 50
        test_status = STATUS_DRAFT

        currency_exchange = CurrencyExchange(
            date=test_date1,
            account=test_account1,
            exchange_account=test_account2,
            amount=test_amount1,
            exchange_amount=test_amount2,
            status=test_status)

        currency_exchange = FinanceServices.save_currency_exchange(
            user=self.test_user,
            currency_exchange=currency_exchange)

        test_name1 = currency_exchange.name

        # account balance unchanged
        self.assertAccount(test_account=test_account1, test_balance=test_balance1)
        self.assertAccount(test_account=test_account2, test_balance=test_balance2)

        # document data auto filled
        self.assertDocument(currency_exchange, DOC_TYPE_CURRENCY_EXCHANGE, test_account1.currency)

        # one finantial history created
        finantials = currency_exchange.finantialdocumenthistory_set
        self.assertEqual(finantials.count(), 1)

        # finantial history info
        finantial = finantials.first()
        self.assertFinantialHistory(
            test_finantial_history=finantial, test_document=currency_exchange, test_user=self.test_user,
            test_old_status=None, test_new_status=test_status)

        # no accounting history created
        accountings = currency_exchange.accountingdocumenthistory_set
        self.assertEqual(accountings.count(), 0)

        test_date2 = test_date1 - timedelta(days=5)

        currency_exchange.date = test_date2

        currency_exchange = FinanceServices.save_currency_exchange(
            user=self.test_user,
            currency_exchange=currency_exchange)

        test_name2 = currency_exchange.name

        # name changed
        self.assertNotEqual(test_name1, test_name2)

        # account balance unchanged
        self.assertAccount(test_account=test_account1, test_balance=test_balance1)
        self.assertAccount(test_account=test_account2, test_balance=test_balance2)

        # document data auto filled
        self.assertDocument(currency_exchange, DOC_TYPE_CURRENCY_EXCHANGE, test_account1.currency)

        # no finantial history created
        finantials = currency_exchange.finantialdocumenthistory_set
        self.assertEqual(finantials.count(), 1)

        # no accounting history created
        accountings = currency_exchange.accountingdocumenthistory_set
        self.assertEqual(accountings.count(), 0)

    def test_save_currency_exchange_ready_then_date(self):
        """
        Does ready currency_exchange and then change to draft
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

        test_date1 = timezone.now()
        test_amount1 = 100
        test_amount2 = 50
        test_status = STATUS_READY

        currency_exchange = CurrencyExchange(
            date=test_date1,
            account=test_account1,
            exchange_account=test_account2,
            amount=test_amount1,
            exchange_amount=test_amount2,
            status=test_status)

        currency_exchange = FinanceServices.save_currency_exchange(
            user=self.test_user,
            currency_exchange=currency_exchange)

        test_name1 = currency_exchange.name

        # account balance incremented
        self.assertAccount(test_account=test_account1, test_balance=test_balance1 + test_amount1)
        self.assertAccount(test_account=test_account2, test_balance=test_balance2 - test_amount2)

        # document data auto filled
        self.assertDocument(currency_exchange, DOC_TYPE_CURRENCY_EXCHANGE, test_account1.currency)

        # one finantial history created
        finantials = currency_exchange.finantialdocumenthistory_set
        self.assertEqual(finantials.count(), 1)

        # finantial history info
        finantial = finantials.first()
        self.assertFinantialHistory(
            test_finantial_history=finantial, test_document=currency_exchange, test_user=self.test_user,
            test_old_status=None, test_new_status=test_status)

        # one accounting history created
        accountings = currency_exchange.accountingdocumenthistory_set
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
            test_movement_type=MOVEMENT_TYPE_OUTPUT, test_amount=test_amount2)

        test_date2 = test_date1 - timedelta(days=5)

        currency_exchange.date = test_date2

        currency_exchange = FinanceServices.save_currency_exchange(
            user=self.test_user,
            currency_exchange=currency_exchange)

        test_name2 = currency_exchange.name

        # name changed
        self.assertNotEqual(test_name1, test_name2)

        # account balance remains changed
        self.assertAccount(test_account=test_account1, test_balance=test_balance1 + test_amount1)
        self.assertAccount(test_account=test_account2, test_balance=test_balance2 - test_amount2)

        # document data auto filled
        self.assertDocument(currency_exchange, DOC_TYPE_CURRENCY_EXCHANGE, test_account1.currency)

        # same finantial history
        finantials = currency_exchange.finantialdocumenthistory_set
        self.assertEqual(finantials.count(), 1)

        # same accounting history
        accountings = currency_exchange.accountingdocumenthistory_set
        self.assertEqual(accountings.count(), 1)

    def test_save_currency_exchange_same_currency(self):
        """
        Does currency_exchange with same accounts currency
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
        test_amount2 = 50
        test_status = STATUS_READY

        currency_exchange = CurrencyExchange(
            date=test_date,
            account=test_account1,
            exchange_account=test_account2,
            amount=test_amount1,
            exchange_amount=test_amount2,
            status=test_status)

        with self.assertRaisesMessage(
            ValidationError, ERROR_SAME_CURRENCY % (test_account1, test_account2)) as ex:
            currency_exchange = FinanceServices.save_currency_exchange(
                user=self.test_user,
                currency_exchange=currency_exchange)

        # account balance unchanged
        # self.assertAccount(test_account=test_account1, test_balance=test_balance1)
        # self.assertAccount(test_account=test_account2, test_balance=test_balance2)
