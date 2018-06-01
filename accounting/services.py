"""
Accounting Service
"""

from django.core.exceptions import ValidationError
from django.db import transaction

from accounting.constants import MOVEMENT_TYPES, MOVEMENT_TYPE_DEPOSIT, MOVEMENT_TYPE_WITHDRAW
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
        with transaction.atomic():
            account = Account.objects.select_for_update().get(pk=account_id)
            if not account:
                raise ValidationError('Account Not Fount : %s' % (account_id))
            return account

    @classmethod
    # account should be locked
    def simple_operation(
            cls, user, current_datetime, concept, detail, account, movement_type, amount):
        """
        Registers simple operation
        """
        with transaction.atomic():
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
            return operation

    @classmethod
    # account should be locked
    def add_operation_movement(cls, operation, account, movement_type, amount):
        """
        Registers movement for operation
        """
        cls._validate_operation(operation=operation)
        cls._validate_movement_type(movement_type=movement_type)
        with transaction.atomic():
            if movement_type is MOVEMENT_TYPE_DEPOSIT:
                cls._do_account_deposit(
                    account=account,
                    amount=amount)
            elif movement_type is MOVEMENT_TYPE_WITHDRAW:
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
    def revert_operation(cls, user, operation_id, current_datetime):
        """
        Registers operation for reverting another operation
        """
        operation = Operation.objects.get(pk=operation_id)
        revertion = None
        if operation:
            concept = 'Revertion for %s' % (operation.concept)
            detail = '%s - Revertion for %s' % (current_datetime, operation.detail)
            with transaction.atomic():
                revertion = Operation(
                    user=user,
                    date=current_datetime,
                    concept=concept,
                    detail=detail)
                revertion.save()
                # barrer movimientos de operacion
                movements = operation.operation_movement_set.all()
                for movement in movements:
                    reverted_movement_type = cls._revert_movement_type(movement.movement_type)
                    movement = OperationMovement(
                        operation=revertion,
                        movement_type=reverted_movement_type,
                        account=movement.account,
                        amount=movement.amount)
                    movement.save()
        return revertion

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
        """
        if not movement_type or not movement_type in MOVEMENT_TYPES:
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
        account.balance += amount
        account.save()
        return account

    @classmethod
    # account should be locked
    def _do_account_withdraw(cls, account, amount):
        cls._validate_account_balance(account=account, balance=amount)
        cls._validate_amount(amount=amount)
        account.balance -= amount
        account.save()
        return account

    @classmethod
    def _revert_movement_type(cls, movement_type):
        if movement_type == MOVEMENT_TYPE_WITHDRAW:
            return MOVEMENT_TYPE_DEPOSIT
        elif movement_type == MOVEMENT_TYPE_DEPOSIT:
            return MOVEMENT_TYPE_WITHDRAW
        else:
            raise ValidationError('Unknown Movement Type: %s' % (movement_type))
