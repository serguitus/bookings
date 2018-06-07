"""
Accounting Service
"""

from django.core.exceptions import ValidationError
from django.db import transaction

from accounting.constants import (MOVEMENT_TYPES,
                                  MOVEMENT_TYPE_INPUT,
                                  MOVEMENT_TYPE_OUTPUT)
from accounting.models import Account, Operation, OperationMovement


class AccountingService():
    """
    Accounting Service
    """

    @classmethod
    def find_and_lock_account_by_id(cls, account_id):
        """
        Gets and lock account
        """
        with transaction.atomic(savepoint=False):
            account = Account.objects.select_for_update().get(
                    pk=account_id)
            return account

    @classmethod
    # account should be locked
    def simple_operation(
            cls, user, current_datetime, concept, detail,
            account, movement_type, amount, other_account=None, other_amount=None):
        """
        Registers simple operation
        """
        with transaction.atomic(savepoint=False):
            # create new operation
            operation = Operation(
                user=user,
                date=current_datetime,
                concept=concept,
                detail=detail)
            operation.save()
            # create operation movement
            cls.add_operation_movement(
                operation=operation,
                account=account,
                movement_type=movement_type,
                amount=amount)
            if other_account:
                movement_amount = amount
                if other_amount:
                    movement_amount = other_amount
                cls.add_operation_movement(
                    operation=operation,
                    account=other_account,
                    movement_type=cls._revert_movement_type(movement_type),
                    amount=movement_amount)
            return operation

    @classmethod
    # account should be locked
    def add_operation_movement(cls, operation, account, movement_type, amount):
        """
        Registers movement for operation
        """
        cls._validate_operation(operation=operation)
        cls._validate_movement_type(movement_type=movement_type)
        with transaction.atomic(savepoint=False):
            if movement_type is MOVEMENT_TYPE_INPUT:
                cls._do_account_deposit(
                    account=account,
                    amount=amount)
            elif movement_type is MOVEMENT_TYPE_OUTPUT:
                cls._do_account_withdraw(
                    account=account,
                    amount=amount)
            else:
                raise ValidationError('Invalid Movement Type: %s' % (movement_type))
            movement = OperationMovement(
                operation=operation,
                movement_type=movement_type,
                account=account,
                amount=amount)
            movement.save()
            return movement

    @classmethod
    def revert_operation(
        cls, user, operation_id, current_datetime, movement_type, account=None, other_account=None):
        """
        Registers operation for reverting another operation
        """
        operation = Operation.objects.get(pk=operation_id)
        revertion = None
        saved = False
        if operation:
            concept = 'Revertion of %s' % (operation.concept)
            detail = '%s - Revertion of %s' % (current_datetime, operation.detail)
            with transaction.atomic(savepoint=False):
                revertion = Operation(
                    user=user,
                    date=current_datetime,
                    concept=concept,
                    detail=detail)
                reverted_movement_type = cls._revert_movement_type(movement_type)
                # barrer movimientos de operacion
                movements = operation.operationmovement_set.all()
                for movement in movements:
                    if movement.movement_type == movement_type:
                        if account and (account.pk == movement.account_id):
                            movement_account = account
                        elif other_account and (other_account.pk == movement.account_id):
                            movement_account = other_account
                        else:
                            movement_account = cls.find_and_lock_account_by_id(movement.account_id)
                        if not saved:
                            revertion.save()
                            saved=True
                        cls.add_operation_movement(
                            operation=revertion,
                            account=movement_account,
                            movement_type=reverted_movement_type,
                            amount=movement.amount)
        if saved:
            return revertion
        return None

    @classmethod
    def _validate_amount(cls, amount):
        """
        Validates positive amount
        """
        if not amount or amount <= 0:
            raise ValidationError('Amount Required')

    @classmethod
    def _validate_operation(cls, operation):
        """
        Validates operation
        """
        if not operation:
            raise ValidationError('Operation Required')

    @classmethod
    def _validate_movement_type(cls, movement_type):
        """
        Validates movement type
        Maybe this is not needed
        see site-packages/django/forms/models.py#1218
        This validates the ChoiceField option
        """
        if not movement_type or not movement_type in [t[0] for t in MOVEMENT_TYPES]:
            raise ValidationError('Movement Type Required')

    @classmethod
    def _validate_account_enabled(cls, account):
        """
        Validates account enabled
        """
        if not account:
            raise ValidationError('Account Required')
        if not account.enabled:
            raise ValidationError(
                'Account %s Not Enabled' % account.__str__())

    @classmethod
    def _validate_account_balance(cls, account, balance):
        """
        Validates account balance
        """
        cls._validate_account_enabled(account=account)
        if account.balance < balance:
            raise ValidationError('Account %s Balance (%s) Insufficient for (%s)' % (
                account.__str__(), account.balance, balance))

    @classmethod
    # account should be locked
    def _do_account_deposit(cls, account, amount):
        cls._validate_account_enabled(account=account)
        cls._validate_amount(amount=amount)
        account.balance = account.balance + amount
        account.save()
        return account

    @classmethod
    # account should be locked
    def _do_account_withdraw(cls, account, amount):
        cls._validate_account_balance(account=account, balance=amount)
        cls._validate_amount(amount=amount)
        account.balance = account.balance - amount
        account.save()
        return account

    @classmethod
    def _revert_movement_type(cls, movement_type):
        if movement_type == MOVEMENT_TYPE_OUTPUT:
            return MOVEMENT_TYPE_INPUT
        elif movement_type == MOVEMENT_TYPE_INPUT:
            return MOVEMENT_TYPE_OUTPUT
        else:
            raise ValidationError('Unknown Movement Type: %s' % (movement_type))
