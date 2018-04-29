
from django.core.exceptions import ValidationError
from django.db import transaction

from accounting.constants import MOVEMENT_TYPES, MOVEMENT_TYPE_DEPOSIT, MOVEMENT_TYPE_WITHDRAW
from accounting.models import *


class AccountingService():

    @classmethod
    def validateAmount(cls, amount):
        if not amount or amount < 0:
            raise ValidationError('Amount Required')

    @classmethod
    def validateOperation(cls, operation):
        if not operation:
            raise ValidationError('Operation Required')

    @classmethod
    def validateMovementType(cls, movement_type):
        if not movement_type or not movement_type in MOVEMENT_TYPES:
            raise ValidationError('Movement Type Required')

    @classmethod
    def validateAccountEnabled(cls, account):
        if not account:
            raise ValidationError('Account Required')
        if not account.enabled:
            raise ValidationError(
                'Account %s Not Enabled' % account.__str__())

    @classmethod
    def validateAccountBalance(cls, account, balance):
        cls.validateAccountEnabled(account=account)
        if account.balance < balance:
            raise ValidationError('Account %s Balance (%s) Insufficient for (%s)' % (
                account.__str__(), account.balance, balance))

    @classmethod
    def findAccountById(cls, account_id):
        with transaction.atomic():
            account = (
                Account.objects.get(id=account_id)
            )
            if not account:
                raise ValidationError('Account Not Fount : %s' % (account_id))
            return account

    @classmethod
    def findAndLockAccountById(cls, account_id):
        with transaction.atomic():
            account = (
                Account.objects.select_for_update().get(id=account_id)
            )
            if not account:
                raise ValidationError('Account Not Fount : %s' % (account_id))
            return account

    @classmethod
    def findOperationById(cls, operation_id):
        with transaction.atomic():
            operation = (
                Operation.objects.get(id=operation_id)
            )
            if not operation:
                raise ValidationError('Operation Not Fount : %s' % (operation_id))
            return operation

    @classmethod
    # account should be locked
    def doAccountDeposit(cls, account, amount):
        cls.validateAccountEnabled(account=account)
        cls.validateAmount(amount=amount)
        account.balance += amount
        account.save()
        return account

    @classmethod
    # account should be locked
    def doAccountWithdraw(cls, account, amount):
        cls.validateAccountBalance(account=account, balance=amount)
        cls.validateAmount(amount=amount)
        account.balance -= amount
        account.save()
        return account

    @classmethod
    # account should be locked
    def addOperationMovement(cls, operation, account, movement_type, amount):
        cls.validateOperation(operation=operation)
        cls.validateMovementType(movement_type=movement_type)
        with transaction.atomic():
            if movement_type is MOVEMENT_TYPE_DEPOSIT:
                cls.doAccountDeposit(
                    account=account,
                    amount=amount,
                )
            else:
                cls.doAccountWithdraw(
                    account=account,
                    amount=amount,
                )
            movement = Movement(
                operation=operation,
                movement_type=movement_type,
                account=account,
                amount=amount,
            )
            movement.save()
            return movement
