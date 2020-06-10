from django.contrib.auth.models import User
from django.test import TestCase

from accounting.constants import (
    MOVEMENT_TYPE_INPUT, MOVEMENT_TYPE_OUTPUT, CURRENCY_CUC, CURRENCY_USD)
from accounting.models import Account, Operation, OperationMovement


class AccountingServiceTestCase(TestCase):

    test_user = None

    def setUp(self):
        self.test_user = User.objects.create(
            username='Test User')

    def test_account_fix_balance_without_movements(self):
        test_account = Account.objects.create(
            name='Test Account',
            currency=CURRENCY_CUC,
            balance=100)
        # test_balance = test_account.balance

        # test_account.fix_balance()

        self.assertEqual(test_account.balance, 0)

    def test_account_fix_balance_with_movements(self):
        test_account1 = Account.objects.create(
            name='Test Account',
            currency=CURRENCY_CUC,
            balance=1000)
        test_account2 = Account.objects.create(
            name='Test Account',
            currency=CURRENCY_USD,
            balance=500)

        test_operation = Operation.objects.create(
            user=self.test_user,
            concept='testing concept',
            detail='testing detail'
        )

        test_amount1 = 100
        test_amount2 = 50

        OperationMovement.objects.create(
            operation=test_operation,
            account=test_account1,
            movement_type=MOVEMENT_TYPE_INPUT,
            amount=test_amount1
        )
        OperationMovement.objects.create(
            operation=test_operation,
            account=test_account2,
            movement_type=MOVEMENT_TYPE_INPUT,
            amount=test_amount2
        )

        test_operation = Operation.objects.create(
            user=self.test_user,
            concept='testing concept',
            detail='testing detail'
        )

        test_amount3 = 20
        test_amount4 = 10

        OperationMovement.objects.create(
            operation=test_operation,
            account=test_account1,
            movement_type=MOVEMENT_TYPE_OUTPUT,
            amount=test_amount3
        )
        OperationMovement.objects.create(
            operation=test_operation,
            account=test_account2,
            movement_type=MOVEMENT_TYPE_OUTPUT,
            amount=test_amount4
        )

        # test_account1.fix_balance()
        # test_account2.fix_balance()

        self.assertEqual(test_account1.balance, test_amount1 - test_amount3)
        self.assertEqual(test_account2.balance, test_amount2 - test_amount4)
