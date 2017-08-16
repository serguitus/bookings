from __future__ import unicode_literals

from datetime import datetime
from django.db import models, transaction as db_transaction
from django.conf import settings
from django.core.exceptions import ValidationError

from cuentas.exceptions import Error

# Create your models here.

class Caja(models.Model):
    """ Esto define una Caja en cierta moneda """
    class Meta:
        verbose_name = 'Account'
        verbose_name_plural = 'Accounts'

    currency = models.CharField(max_length=5, choices=settings.CURRENCIES)
    balance = models.IntegerField(default=0, verbose_name='current_balance')
    description = models.CharField(max_length=100)
    created = models.DateTimeField(blank=True, default=datetime.now())
    modified = models.DateTimeField(blank=True, default=datetime.now())

    def __str__(self):
        """ Representation of a Caja """
        return "%s (%s)" % (self.description, self.currency)

    @classmethod
    def create(cls, user, created_by, asof, currency='cuc'):
        """Create account.

        user (User):
            Owner of the account.
        created_by (User):
            User that created the account.
        asof (datetime.datetime):
            Time of creation.

        Returns (tuple):
            [0] Account
            [1] Action
        """
        with db_transaction.atomic():
            caja = cls.objects.create(created=asof, modified=asof, balance=0, currency=currency)

            transaction = Transaction.create(
                user=created_by,
                caja=caja,
                t_type=Transaction.ACTION_TYPE_CREATED,
                delta=0,
                asof=asof,
            )

        return caja, transaction

    @classmethod
    def deposit(cls, cid, deposited_by, amount, asof,
                concept='', reference_type='None', detail=None):
        """Deposit to account.

        cid: Caja ID.
        deposited_by (User): Deposited by.
        amount (positive int): Amount to deposit.
        asof (datetime.datetime): Time of deposit.
        comment(str or None): Optional comment.

        Raises
        Account.DoesNotExist
        InvalidAmount

        Returns (tuple):
        [0] (Account) Updated account instance.
        [0] (Action) Deposit action.
        """
        assert amount > 0

        with db_transaction.atomic():
            account = cls.objects.select_for_update().get(id=cid)

            #if not (cls.MIN_DEPOSIT <= amount <= cls.MAX_DEPOSIT):
            #    raise errors.InvalidAmount(amount)

            #if account.balance + amount > cls.MAX_BALANCE:
            #    raise errors.ExceedsLimit()

            #total = cls.objects.aggregate(total=Sum('balance'))['total']
            #if total + amount > cls.MAX_TOTAL_BALANCES:
            #    raise errors.ExceedsLimit()

            account.balance += amount
            account.modified = asof

            account.save(update_fields=[
                'balance',
                'modified',
            ])

            transaction = Transaction.create(
                user=deposited_by,
                caja=account,
                t_type=Transaction.ACTION_TYPE_DEPOSITED,
                delta=amount,
                asof=asof,
                concept=concept,
                reference_type=reference_type,
                detail=detail
            )

        return account, transaction

    @classmethod
    def withdraw(cls, cid, withdrawn_by, amount, asof, concept, detail=None):
        """Withdraw from account.

        uid (uuid.UUID): Account public identifier.
        withdrawn_by (User): The withdrawing user.
        amount (positive int): Amount to withdraw.
        asof (datetime.datetime): Time of withdraw.
        concept (str or None): Payment Concept.
        detail: Optional description of the transaction

        Raises:
        Caja.DoesNotExist
        InvalidAmount

        Returns (tuple):
        [0] (Caja) Updated account instance.
        [0] (Transaction) Withdraw action.
        """
        assert amount > 0

        with db_transaction.atomic():
            account = cls.objects.select_for_update().get(id=cid)

            #if not (cls.MIN_WITHDRAW <= amount <= cls.MAX_WITHDRAW):
            #    raise InvalidAmount(amount)

            #if account.balance - amount < cls.MIN_BALANCE:
            #    raise InsufficientFunds(amount, account.balance)

            account.balance -= amount
            account.modified = asof

            account.save(update_fields=[
                'balance',
                'modified',
            ])

            action = Transaction.create(
                user=withdrawn_by,
                caja=account,
                t_type=Transaction.ACTION_TYPE_WITHDRAWN,
                delta=-amount,
                asof=asof,
                concept=concept
            )

        return account, action


class Transaction(models.Model):
    """ This deals with money operations. deposits, extractions, loans and transferences """
    class Meta:
        verbose_name = 'Transaction'
        verbose_name_plural = 'Transactions'

    ACTION_TYPE_CREATED = 'CREATED'
    ACTION_TYPE_DEPOSITED = 'DEPOSITED'
    ACTION_TYPE_WITHDRAWN = 'WITHDRAWN'
    ACTION_TYPE_CHOICES = (
        (ACTION_TYPE_CREATED, 'Created'),
        (ACTION_TYPE_DEPOSITED, 'Deposited'),
        (ACTION_TYPE_WITHDRAWN, 'Withdrawn'),
    )

    REFERENCE_TYPE_BANK_TRANSFER = 'BANK_TRANSFER'
    REFERENCE_TYPE_CASH = 'CASH'
    REFERENCE_TYPE_NONE = 'NONE'
    REFERENCE_TYPE_CHOICES = (
        (REFERENCE_TYPE_BANK_TRANSFER, 'Bank Transfer'),
        (REFERENCE_TYPE_CASH, 'Cash'),
        (REFERENCE_TYPE_NONE, 'None'),
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        help_text='User who performed the action.',
    )
    caja = models.ForeignKey(Caja, models.CASCADE)
    ammount = models.IntegerField(default=0)
    transaction_type = models.CharField(
        max_length=30,
        choices=ACTION_TYPE_CHOICES,
        default='Withdrawn'
    )
    reference_type = models.CharField(
        max_length=30,
        choices=REFERENCE_TYPE_CHOICES,
        default=REFERENCE_TYPE_NONE,
    )
    date = models.DateField()
    concept = models.CharField(max_length=100)
    detail = models.CharField(max_length=250)

    def __str__(self):
        return 'Transaccion: %s' % self.concept

    @classmethod
    def create(cls, user, caja, t_type, delta, asof, concept=None, reference_type=None, detail=None):
        """Create Action.

        user (User):
            User who executed the action.
        account (Account):
            Account the action executed on.
        type (str, one of Action.ACTION_TYPE_*):
            Type of action.
        delta (int):
            Change in balance.
        asof (datetime.datetime):
            When was the action executed.
        reference (str or None):
            Reference number when appropriate.
        reference_type(str or None):
            Type of reference.
            Defaults to "NONE".
        comment (str or None):
            Optional comment on the action.

        Raises:
            ValidationError

        Returns (Action)
        """
        assert asof is not None

        if (t_type == cls.ACTION_TYPE_DEPOSITED and 
            reference_type is None):
            raise ValidationError({
                'reference_type': 'required for deposit.',  
            })

        if reference_type is None:
            reference_type = cls.REFERENCE_TYPE_NONE

        # Don't store null in text field.

        if concept is None:
            reference = ''

        if detail is None:
            detail = ''

        #user_friendly_id = generate_user_friendly_id()

        return cls.objects.create(
            #user_friendly_id=user_friendly_id,
            date=asof,
            user=user,
            caja=caja,
            transaction_type=t_type,
            ammount=delta,
            concept=concept,
            reference_type=reference_type,
            detail=detail,
            #debug_balance=account.balance,
        )

