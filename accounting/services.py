
from django.core.exceptions import ValidationError
from django.db import transaction

from accounting.constants import MOVEMENT_TYPES, MOVEMENT_TYPE_DEPOSIT, MOVEMENT_TYPE_WITHDRAW
from accounting.models import *


class AccountingService():

    @classmethod
    def validate_amount(cls, amount):
        if not amount or amount < 0:
            raise ValidationError('Amount Required')

    @classmethod
    def validate_operation(cls, operation):
        if not operation:
            raise ValidationError('Operation Required')

    @classmethod
    def validate_movement_type(cls, movement_type):
        if not movement_type or not movement_type in MOVEMENT_TYPES:
            raise ValidationError('Movement Type Required')

    @classmethod
    def validate_account_enabled(cls, account):
        if not account:
            raise ValidationError('Account Required')
        if not account.enabled:
            raise ValidationError(
                'Account %s Not Enabled' % account.__str__())

    @classmethod
    def validate_account_balance(cls, account, balance):
        cls.validate_account_enabled(account=account)
        if account.balance < balance:
            raise ValidationError('Account %s Balance (%s) Insufficient for (%s)' % (
                account.__str__(), account.balance, balance))

    @classmethod
    def find_account_by_id(cls, account_id):
        with transaction.atomic():
            account = (
                Account.objects.get(id=account_id)
            )
            if not account:
                raise ValidationError('Account Not Fount : %s' % (account_id))
            return account

    @classmethod
    def find_and_lock_account_by_id(cls, account_id):
        with transaction.atomic():
            account = (
                Account.objects.select_for_update().get(id=account_id)
            )
            if not account:
                raise ValidationError('Account Not Fount : %s' % (account_id))
            return account

    @classmethod
    def find_operation_by_id(cls, operation_id):
        with transaction.atomic():
            operation = (
                Operation.objects.get(id=operation_id)
            )
            if not operation:
                raise ValidationError('Operation Not Fount : %s' % (operation_id))
            return operation

    @classmethod
    # account should be locked
    def do_account_deposit(cls, account, amount):
        cls.validate_account_enabled(account=account)
        cls.validate_amount(amount=amount)
        account.balance += amount
        account.save()
        return account

    @classmethod
    # account should be locked
    def do_account_withdraw(cls, account, amount):
        cls.validate_account_balance(account=account, balance=amount)
        cls.validate_amount(amount=amount)
        account.balance -= amount
        account.save()
        return account

    @classmethod
    # account should be locked
    def add_operation_movement(cls, operation, account, movement_type, amount):
        cls.validate_operation(operation=operation)
        cls.validate_movement_type(movement_type=movement_type)
        with transaction.atomic():
            if movement_type is MOVEMENT_TYPE_DEPOSIT:
                cls.do_account_deposit(
                    account=account,
                    amount=amount,
                )
            elif movement_type is MOVEMENT_TYPE_WITHDRAW:
                cls.do_account_withdraw(
                    account=account,
                    amount=amount,
                )
            else:
                raise ValidationError('Invalid Movement Type: %s' % (movement_type))
                
            movement = OperationMovement(
                operation=operation,
                movement_type=movement_type,
                account=account,
                amount=amount,
            )
            movement.save()
            return movement
