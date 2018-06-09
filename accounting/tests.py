from datetime import datetime

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.test import TestCase

from accounting.constants import (
    MOVEMENT_TYPE_INPUT, MOVEMENT_TYPE_OUTPUT, CURRENCY_CUC, CURRENCY_USD,
    CONCEPT_DEPOSIT, CONCEPT_WITHDRAW, CONCEPT_TRANSFER, CONCEPT_CURRENCY_EXCHANGE)
from accounting.models import Account, Operation
from accounting.services import AccountingService


class AccountingServiceTestCase(TestCase):

    test_user = None
    test_account1 = None
    test_account2 = None
    test_account3 = None

    def setUp(self):
        self.test_user = User.objects.create(
            username="Test User")
        self.test_account1 = Account.objects.create(
            name="Test Account 1",
            currency=CURRENCY_CUC)
        self.test_account2 = Account.objects.create(
            name="Test Account 2",
            currency=CURRENCY_CUC)
        self.test_account3 = Account.objects.create(
            name="Test Account 3",
            currency=CURRENCY_USD)

    def test_simple_operation(self):
        """
        Does deposit of 100 on TA1
        """
        test_balance1 = self.test_account1.balance
        test_current_datetime = datetime.now()
        test_concept = CONCEPT_DEPOSIT
        test_detail = "Testing"
        test_movement_type = MOVEMENT_TYPE_INPUT
        test_amount = 100

        operation = AccountingService.simple_operation(
            user=self.test_user,
            current_datetime=test_current_datetime,
            concept=test_concept,
            detail=test_detail,
            account=self.test_account1,
            movement_type=test_movement_type,
            amount=test_amount)

        self.assertEqual(self.test_account1.balance, test_balance1 + test_amount)
        movements = operation.operationmovement_set
        self.assertEqual(movements.count(), 1)
        movement = movements.first()
        self.assertEqual(movement.account_id, self.test_account1.pk)
        self.assertEqual(movement.movement_type, test_movement_type)
        self.assertEqual(movement.amount, test_amount)

        """
        Does transfer of 50 from TA1 to TA2
        """
        test_balance1 = self.test_account1.balance
        test_balance2 = self.test_account2.balance
        test_current_datetime = datetime.now()
        test_concept = CONCEPT_TRANSFER
        test_detail = "Testing"
        test_movement_type = MOVEMENT_TYPE_INPUT
        test_amount = 50

        operation = AccountingService.simple_operation(
            user=self.test_user,
            current_datetime=test_current_datetime,
            concept=test_concept,
            detail=test_detail,
            account=self.test_account2,
            movement_type=test_movement_type,
            amount=test_amount,
            other_account=self.test_account1)

        self.assertEqual(self.test_account1.balance, test_balance1 - test_amount)
        self.assertEqual(self.test_account2.balance, test_balance2 + test_amount)
        movements = operation.operationmovement_set
        self.assertEqual(movements.count(), 2)
        movement = movements.first()
        if movement.movement_type is MOVEMENT_TYPE_INPUT:
            self.assertEqual(movement.account_id, self.test_account2.pk)
            self.assertEqual(movement.amount, test_amount)
            movement = movements.last()
            self.assertEqual(movement.account_id, self.test_account1.pk)
            self.assertEqual(movement.movement_type, MOVEMENT_TYPE_OUTPUT)
            self.assertEqual(movement.amount, test_amount)
        else:
            self.assertEqual(movement.account_id, self.test_account1.pk)
            self.assertEqual(movement.amount, test_amount)
            movement = movements.last()
            self.assertEqual(movement.account_id, self.test_account2.pk)
            self.assertEqual(movement.movement_type, MOVEMENT_TYPE_INPUT)
            self.assertEqual(movement.amount, test_amount)

        """
        Does exchange of 50 from TA1 to 100 in TA3
        """
        test_balance1 = self.test_account1.balance
        test_balance2 = self.test_account3.balance
        test_current_datetime = datetime.now()
        test_concept = CONCEPT_CURRENCY_EXCHANGE
        test_detail = "Testing"
        test_movement_type = MOVEMENT_TYPE_INPUT
        test_amount1 = 100
        test_amount2 = 50

        operation = AccountingService.simple_operation(
            user=self.test_user,
            current_datetime=test_current_datetime,
            concept=test_concept,
            detail=test_detail,
            account=self.test_account3,
            movement_type=test_movement_type,
            amount=test_amount1,
            other_account=self.test_account1,
            other_amount=test_amount2)

        self.assertEqual(self.test_account1.balance, test_balance1 - test_amount2)
        self.assertEqual(self.test_account3.balance, test_balance2 + test_amount1)
        movements = operation.operationmovement_set
        self.assertEqual(movements.count(), 2)
        movement = movements.first()
        if movement.movement_type is MOVEMENT_TYPE_INPUT:
            self.assertEqual(movement.account_id, self.test_account3.pk)
            self.assertEqual(movement.amount, test_amount1)
            movement = movements.last()
            self.assertEqual(movement.account_id, self.test_account1.pk)
            self.assertEqual(movement.movement_type, MOVEMENT_TYPE_OUTPUT)
            self.assertEqual(movement.amount, test_amount2)
        else:
            self.assertEqual(movement.account_id, self.test_account1.pk)
            self.assertEqual(movement.amount, test_amount2)
            movement = movements.last()
            self.assertEqual(movement.account_id, self.test_account3.pk)
            self.assertEqual(movement.movement_type, MOVEMENT_TYPE_INPUT)
            self.assertEqual(movement.amount, test_amount1)

    def test_simple_operation_deposit_on_disabled(self):
        """
        Does deposit on disabled account
        """
        test_balance = self.test_account1.balance
        self.test_account1.enabled = False
        self.test_account1.save()

        test_current_datetime = datetime.now()
        test_concept = CONCEPT_DEPOSIT
        test_detail = "Testing"
        test_movement_type = MOVEMENT_TYPE_INPUT
        test_amount = 100

        with self.assertRaises(ValidationError):
            operation = AccountingService.simple_operation(
                user=self.test_user,
                current_datetime=test_current_datetime,
                concept=test_concept,
                detail=test_detail,
                account=self.test_account1,
                movement_type=test_movement_type,
                amount=test_amount)

        self.assertEqual(self.test_account1.balance, test_balance)

    def test_simple_operation_withdraw_on_low_balance(self):
        """
        Does withdraw on low balance account
        """
        test_balance = self.test_account2.balance
        test_current_datetime = datetime.now()
        test_concept = CONCEPT_WITHDRAW
        test_detail = "Testing"
        test_movement_type = MOVEMENT_TYPE_OUTPUT
        test_amount = 100

        with self.assertRaises(ValidationError):
            operation = AccountingService.simple_operation(
                user=self.test_user,
                current_datetime=test_current_datetime,
                concept=test_concept,
                detail=test_detail,
                account=self.test_account2,
                movement_type=test_movement_type,
                amount=test_amount)

        self.assertEqual(self.test_account2.balance, test_balance)

    def test_simple_operation_with_invalid_movement_type(self):
        """
        Does unknown movement type
        """
        test_balance = self.test_account2.balance
        test_current_datetime = datetime.now()
        test_concept = CONCEPT_DEPOSIT
        test_detail = "Testing"
        test_movement_type = 'unknown'
        test_amount = 100

        with self.assertRaises(ValidationError):
            operation = AccountingService.simple_operation(
                user=self.test_user,
                current_datetime=test_current_datetime,
                concept=test_concept,
                detail=test_detail,
                account=self.test_account2,
                movement_type=test_movement_type,
                amount=test_amount)

        self.assertEqual(self.test_account2.balance, test_balance)
