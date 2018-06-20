from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from django.test import TestCase
from django.utils import timezone

from accounting.constants import (
    MOVEMENT_TYPE_INPUT, MOVEMENT_TYPE_OUTPUT, CURRENCY_CUC, CURRENCY_USD,
    ERROR_UNKNOWN_MOVEMENT_TYPE, ERROR_ACCOUNT_REQUIRED, ERROR_DISABLED,
    ERROR_AMOUNT_REQUIRED, ERROR_NOT_BALANCE, ERROR_DIFFERENT_CURRENCY, ERROR_SAME_CURRENCY)
from accounting.models import Account
from accounting.services import AccountingService


class AccountingBaseTestCase(TestCase):

    def assertAccount(self, test_account, test_balance):
        test_account.refresh_from_db()
        self.assertEqual(test_account.balance, test_balance)

    def assertMovement(self, test_movement, test_account, test_movement_type, test_amount):
        self.assertEqual(test_movement.account_id, test_account.pk)
        self.assertEqual(test_movement.movement_type, test_movement_type)
        self.assertEqual(test_movement.amount, test_amount)

class AccountingServicesTestCase(AccountingBaseTestCase):

    test_user = None

    def setUp(self):
        self.test_user = User.objects.create(
            username='Test User')

    def test_simple_operation_deposit(self):
        """
        Does deposit of 100 on TA1
        """
        test_account = Account.objects.create(
            name='Test Account',
            currency=CURRENCY_CUC)
        test_balance = test_account.balance

        test_current_datetime = timezone.now()
        test_concept = 'Deposit'
        test_detail = 'Testing'
        test_movement_type = MOVEMENT_TYPE_INPUT
        test_amount = 100

        operation = AccountingService.simple_operation(
            user=self.test_user,
            current_datetime=test_current_datetime,
            concept=test_concept,
            detail=test_detail,
            account=test_account,
            movement_type=test_movement_type,
            amount=test_amount)

        # account balance incremented
        self.assertAccount(test_account=test_account, test_balance=test_balance + test_amount)

        # one movement created
        movements = operation.operationmovement_set
        self.assertEqual(movements.count(), 1)

        # movement info
        movement = movements.first()
        self.assertMovement(
            test_movement=movement, test_account=test_account,
            test_movement_type=test_movement_type, test_amount=test_amount)

    def test_simple_operation_with_invalid_movement_type(self):
        """
        Does unknown movement type
        """
        test_account = Account.objects.create(name="Test Account", currency=CURRENCY_CUC)
        test_balance = test_account.balance

        test_current_datetime = timezone.now()
        test_concept = 'Deposit'
        test_detail = "Testing"
        test_movement_type = 'unknown'
        test_amount = 100

        with self.assertRaisesMessage(
            ValidationError, ERROR_UNKNOWN_MOVEMENT_TYPE % (test_movement_type)) as ex:
            operation = AccountingService.simple_operation(
                user=self.test_user,
                current_datetime=test_current_datetime,
                concept=test_concept,
                detail=test_detail,
                account=test_account,
                movement_type=test_movement_type,
                amount=test_amount)

        # account balance unchanged
        self.assertAccount(test_account=test_account, test_balance=test_balance)

    def test_simple_operation_without_account(self):
        """
        Does deposit without account
        """
        test_current_datetime = timezone.now()
        test_concept = 'Deposit'
        test_detail = "Testing"
        test_movement_type = MOVEMENT_TYPE_INPUT
        test_amount = 100

        with self.assertRaisesMessage(ValidationError, ERROR_ACCOUNT_REQUIRED):
            operation = AccountingService.simple_operation(
                user=self.test_user,
                current_datetime=test_current_datetime,
                concept=test_concept,
                detail=test_detail,
                account=None,
                movement_type=test_movement_type,
                amount=test_amount)

    def test_simple_operation_deposit_on_disabled(self):
        """
        Does deposit on disabled account
        """
        test_account = Account.objects.create(
            name="Test Account",
            currency=CURRENCY_CUC,
            enabled=False)
        test_balance = test_account.balance

        test_current_datetime = timezone.now()
        test_concept = 'Deposit'
        test_detail = "Testing"
        test_movement_type = MOVEMENT_TYPE_INPUT
        test_amount = 100

        with self.assertRaisesMessage(ValidationError, ERROR_DISABLED % test_account):
            operation = AccountingService.simple_operation(
                user=self.test_user,
                current_datetime=test_current_datetime,
                concept=test_concept,
                detail=test_detail,
                account=test_account,
                movement_type=test_movement_type,
                amount=test_amount)

        # account balance unchanged
        self.assertAccount(test_account=test_account, test_balance=test_balance)

    def test_simple_operation_with_no_amount(self):
        """
        Does Deposit with zero amount
        """
        test_account = Account.objects.create(name="Test Account", currency=CURRENCY_CUC)
        test_balance = test_account.balance

        test_current_datetime = timezone.now()
        test_concept = 'Deposit'
        test_detail = "Testing"
        test_movement_type = MOVEMENT_TYPE_INPUT
        test_amount = 0

        with self.assertRaisesMessage(ValidationError, ERROR_AMOUNT_REQUIRED) as ex:
            operation = AccountingService.simple_operation(
                user=self.test_user,
                current_datetime=test_current_datetime,
                concept=test_concept,
                detail=test_detail,
                account=test_account,
                movement_type=test_movement_type,
                amount=test_amount)

        # account balance unchanged
        self.assertAccount(test_account=test_account, test_balance=test_balance)

    def test_simple_operation_withdraw_on_low_balance(self):
        """
        Does withdraw on low balance account
        """
        test_account = Account.objects.create(
            name="Test Account",
            currency=CURRENCY_CUC,
            balance=50)
        test_balance = test_account.balance

        test_current_datetime = timezone.now()
        test_concept = 'Withdraw'
        test_detail = "Testing"
        test_movement_type = MOVEMENT_TYPE_OUTPUT
        test_amount = 100

        with self.assertRaisesMessage(
            ValidationError,
            ERROR_NOT_BALANCE % (test_account, test_account.balance, test_amount)):
            operation = AccountingService.simple_operation(
                user=self.test_user,
                current_datetime=test_current_datetime,
                concept=test_concept,
                detail=test_detail,
                account=test_account,
                movement_type=test_movement_type,
                amount=test_amount)

        # account balance unchanged
        self.assertAccount(test_account=test_account, test_balance=test_balance)

    def test_simple_operation_transfer(self):
        """
        Does transfer to TA1 from TA2 of 50
        """
        test_account1 = Account.objects.create(name="Test Account 1", currency=CURRENCY_CUC)
        test_balance1 = test_account1.balance

        test_account2 = Account.objects.create(
            name='Test Account 2',
            currency=CURRENCY_CUC,
            balance=100)
        test_balance2 = test_account2.balance

        test_current_datetime = timezone.now()
        test_concept = 'Transfer'
        test_detail = "Testing"
        test_movement_type = MOVEMENT_TYPE_INPUT
        test_amount = 50

        operation = AccountingService.simple_operation(
            user=self.test_user,
            current_datetime=test_current_datetime,
            concept=test_concept,
            detail=test_detail,
            account=test_account1,
            movement_type=test_movement_type,
            amount=test_amount,
            other_account=test_account2)

        # account balance incremented
        self.assertAccount(test_account=test_account1, test_balance=test_balance1 + test_amount)
        # account balance decremented
        self.assertAccount(test_account=test_account2, test_balance=test_balance2 - test_amount)

        # two movement created
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

    def test_simple_operation_transfer_on_different_currency(self):
        """
        Does transfer with different accounts currency
        """
        test_account1 = Account.objects.create(name="Test Account 1", currency=CURRENCY_USD)
        test_balance1 = test_account1.balance

        test_account2 = Account.objects.create(
            name='Test Account 2',
            currency=CURRENCY_CUC,
            balance=100)
        test_balance2 = test_account2.balance

        test_current_datetime = timezone.now()
        test_concept = 'Transfer'
        test_detail = "Testing"
        test_movement_type = MOVEMENT_TYPE_INPUT
        test_amount = 50

        with self.assertRaisesMessage(
            ValidationError, ERROR_DIFFERENT_CURRENCY % (test_account1, test_account2)) as ex:
            operation = AccountingService.simple_operation(
                user=self.test_user,
                current_datetime=test_current_datetime,
                concept=test_concept,
                detail=test_detail,
                account=test_account1,
                movement_type=test_movement_type,
                amount=test_amount,
                other_account=test_account2)

        # account balance unchanged
        self.assertAccount(test_account=test_account1, test_balance=test_balance1)
        self.assertAccount(test_account=test_account2, test_balance=test_balance2)

    def test_simple_operation_transfer_with_low_balance(self):
        """
        Does transfer with low balance
        """
        test_account1 = Account.objects.create(name="Test Account 1", currency=CURRENCY_CUC)
        test_balance1 = test_account1.balance

        test_account2 = Account.objects.create(
            name='Test Account 2',
            currency=CURRENCY_CUC,
            balance=50)
        test_balance2 = test_account2.balance

        test_current_datetime = timezone.now()
        test_concept = 'Transfer'
        test_detail = "Testing"
        test_movement_type = MOVEMENT_TYPE_INPUT
        test_amount = 100

        with self.assertRaisesMessage(
            ValidationError,
            ERROR_NOT_BALANCE % (test_account2, test_account2.balance, test_amount)) as ex:
            operation = AccountingService.simple_operation(
                user=self.test_user,
                current_datetime=test_current_datetime,
                concept=test_concept,
                detail=test_detail,
                account=test_account1,
                movement_type=test_movement_type,
                amount=test_amount,
                other_account=test_account2)

        # account balance unchanged
        self.assertAccount(test_account=test_account1, test_balance=test_balance1)
        self.assertAccount(test_account=test_account2, test_balance=test_balance2)

    def test_simple_operation_currency_exchange(self):
        """
        Does exchange to TA1 (100) from TA2 (50)
        """
        test_account1 = Account.objects.create(name="Test Account 1", currency=CURRENCY_USD)
        test_balance1 = test_account1.balance

        test_account2 = Account.objects.create(
            name='Test Account 2',
            currency=CURRENCY_CUC,
            balance=100)
        test_balance2 = test_account2.balance

        test_current_datetime = timezone.now()
        test_concept = 'Currency Exchange'
        test_detail = "Testing"
        test_movement_type = MOVEMENT_TYPE_INPUT
        test_amount1 = 100
        test_amount2 = 50

        operation = AccountingService.simple_operation(
            user=self.test_user,
            current_datetime=test_current_datetime,
            concept=test_concept,
            detail=test_detail,
            account=test_account1,
            movement_type=test_movement_type,
            amount=test_amount1,
            other_account=test_account2,
            other_amount=test_amount2)

        # account balance incremented
        self.assertAccount(test_account=test_account1, test_balance=test_balance1 + test_amount1)
        # account balance decremented
        self.assertAccount(test_account=test_account2, test_balance=test_balance2 - test_amount2)

        # two movement created
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

    def test_simple_operation_currency_exchange_with_same_currency(self):
        """
        Does exchange with same accounts currency
        """
        test_account1 = Account.objects.create(name="Test Account 1", currency=CURRENCY_CUC)
        test_balance1 = test_account1.balance

        test_account2 = Account.objects.create(
            name='Test Account 2',
            currency=CURRENCY_CUC,
            balance=100)
        test_balance2 = test_account2.balance

        test_current_datetime = timezone.now()
        test_concept = 'Currency Exchange'
        test_detail = "Testing"
        test_movement_type = MOVEMENT_TYPE_INPUT
        test_amount1 = 100
        test_amount2 = 50

        with self.assertRaisesMessage(
            ValidationError, ERROR_SAME_CURRENCY % (test_account1, test_account2)) as ex:
            operation = AccountingService.simple_operation(
                user=self.test_user,
                current_datetime=test_current_datetime,
                concept=test_concept,
                detail=test_detail,
                account=test_account1,
                movement_type=test_movement_type,
                amount=test_amount1,
                other_account=test_account2,
                other_amount=test_amount2)

        # account balance unchanged
        self.assertAccount(test_account=test_account1, test_balance=test_balance1)
        self.assertAccount(test_account=test_account2, test_balance=test_balance2)

    def test_simple_operation_currency_exchange_with_low_balance(self):
        """
        Does exchange with same accounts currency
        """
        test_account1 = Account.objects.create(name="Test Account 1", currency=CURRENCY_USD)
        test_balance1 = test_account1.balance

        test_account2 = Account.objects.create(
            name='Test Account 2',
            currency=CURRENCY_CUC,
            balance=50)
        test_balance2 = test_account2.balance

        test_current_datetime = timezone.now()
        test_concept = 'Currency Exchange'
        test_detail = "Testing"
        test_movement_type = MOVEMENT_TYPE_INPUT
        test_amount1 = 200
        test_amount2 = 100

        with self.assertRaisesMessage(
            ValidationError,
            ERROR_NOT_BALANCE % (test_account2, test_account2.balance, test_amount2)) as ex:
            operation = AccountingService.simple_operation(
                user=self.test_user,
                current_datetime=test_current_datetime,
                concept=test_concept,
                detail=test_detail,
                account=test_account1,
                movement_type=test_movement_type,
                amount=test_amount1,
                other_account=test_account2,
                other_amount=test_amount2)

        # account balance unchanged
        self.assertAccount(test_account=test_account1, test_balance=test_balance1)
        self.assertAccount(test_account=test_account2, test_balance=test_balance2)

    def test_create_account_duplicate(self):
        """
        Does accounts with same name and currency
        """
        test_account1 = Account.objects.create(name="Test Account 1", currency=CURRENCY_USD)

        with self.assertRaises(IntegrityError) as ex:
            test_account2 = Account.objects.create(name="Test Account 1", currency=CURRENCY_USD)
