# -*- coding: utf-8 -*-
from __future__ import unicode_literals

"""
Accounting Service
"""

from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from accounting.constants import (
    MOVEMENT_TYPE_INPUT, MOVEMENT_TYPE_OUTPUT,
    ERROR_UNKNOWN_MOVEMENT_TYPE, ERROR_ACCOUNT_REQUIRED, ERROR_DISABLED,
    ERROR_AMOUNT_REQUIRED, ERROR_NOT_BALANCE, ERROR_DIFFERENT_CURRENCY)
from accounting.models import Account, Operation, OperationMovement


class AccountingService():
    """
    Accounting Service
    """

    @classmethod
    # account should be locked
    def simple_operation(
            cls, user, concept, detail, account, movement_type, amount,
            other_account=None, other_amount=None, current_datetime=timezone.now()):
        """
        Registers simple operation with 1 or 2 movements
        for first movement parameters:
            account, amount and movement_type are used
        for second movement parameters:
            other_account most be especified
            if other_amount is especified, accounts most have different currency
                else accounts most have same currency
            reverted movement type
        """
        # verifications
        cls._validate_movement_type(movement_type=movement_type)
        cls._validate_account(account=account)
        cls._validate_amount(amount=amount)
        if movement_type == MOVEMENT_TYPE_OUTPUT:
            cls._validate_account_balance(account=account, amount=amount)
        if other_account:
            cls._validate_account(account=other_account)
            movement_amount = amount
            if other_amount:
                # can be transfer with or without operation_cost, or exchange 
                cls._validate_amount(amount=other_amount)
                movement_amount = other_amount
            else:
                # must be accounts with same currencies
                if account.currency != other_account.currency:
                    raise ValidationError(ERROR_DIFFERENT_CURRENCY % (account, other_account))
            # verify balance
            if movement_type == MOVEMENT_TYPE_INPUT:
                cls._validate_account_balance(account=other_account, amount=movement_amount)
        with transaction.atomic(savepoint=False):
            # create new operation
            operation = Operation(
                user=user,
                datetime=current_datetime,
                concept=concept,
                detail=detail)
            operation.save()
            # create operation movement
            cls._add_operation_movement(
                operation=operation,
                account=account,
                movement_type=movement_type,
                amount=amount)
            if other_account:
                cls._add_operation_movement(
                    operation=operation,
                    account=other_account,
                    movement_type=cls._revert_movement_type(movement_type),
                    amount=movement_amount)
            return operation

    @classmethod
    def _find_and_lock_account_by_id(cls, account_id):
        """
        Gets and lock account
        """
        with transaction.atomic(savepoint=False):
            account = Account.objects.select_for_update().get(pk=account_id)
            return account

    @classmethod
    # account should be locked
    def _add_operation_movement(cls, operation, account, movement_type, amount):
        """
        Registers movement for operation
        """
        cls._do_account_movement(
            account=account,
            amount=amount,
            movement_type=movement_type)
        movement = OperationMovement(
            operation=operation,
            movement_type=movement_type,
            account=account,
            amount=amount)
        movement.save()
        return movement

    @classmethod
    # account should be locked
    def _do_account_movement(cls, account, amount, movement_type):
        if movement_type == MOVEMENT_TYPE_INPUT:
            account.balance = float(account.balance) + float(amount)
        if movement_type == MOVEMENT_TYPE_OUTPUT:
            account.balance = float(account.balance) - float(amount)
        account.save()
        return account

    @classmethod
    def _validate_movement_type(cls, movement_type):
        """
        Validates movement type
        """
        if (movement_type != MOVEMENT_TYPE_INPUT) and (movement_type != MOVEMENT_TYPE_OUTPUT):
            raise ValidationError(ERROR_UNKNOWN_MOVEMENT_TYPE % (movement_type))

    @classmethod
    def _validate_account(cls, account):
        """
        Validates account
        """
        if not account:
            raise ValidationError(
                ERROR_ACCOUNT_REQUIRED)
        if not account.enabled:
            raise ValidationError(
                ERROR_DISABLED % account)

    @classmethod
    def _validate_amount(cls, amount):
        """
        Validates positive amount
        """
        if not amount or amount <= 0:
            raise ValidationError(ERROR_AMOUNT_REQUIRED)

    @classmethod
    def _validate_account_balance(cls, account, amount):
        """
        Validates account balance
        """
        if account.balance < amount:
            raise ValidationError(ERROR_NOT_BALANCE % (
                account, account.balance, amount))

    @classmethod
    def _revert_movement_type(cls, movement_type):
        if movement_type == MOVEMENT_TYPE_OUTPUT:
            return MOVEMENT_TYPE_INPUT
        if movement_type == MOVEMENT_TYPE_INPUT:
            return MOVEMENT_TYPE_OUTPUT
        raise ValidationError(ERROR_UNKNOWN_MOVEMENT_TYPE % (movement_type))
