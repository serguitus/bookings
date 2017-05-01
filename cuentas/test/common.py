from __future__ import unicode_literals
from cuentas.models import Caja

class TestCajaBase:
   
    DEFAULT = object()
    
    @classmethod
    def default(value, default_value):
        return default_value if value is cls.DEFAULT else value
    
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        # Set up some default values
        cls.admin = User.objects.create_superuser(
            'Admin',
            'admin',
            'admin@testing.test',
        )

        cls.user_A = User.objects.create_user(
            'user_A',
            'user_A',
            'A@testing.test',
        )

    @classmethod
    def create(cls, user=DEFAULT, created_by=DEFAULT, asof=DEFAULT):
        user = cls.default(user, cls.user_A)
        created_by = cls.default(created_by, cls.admin)
        asof = cls.default(asof, timezone.now())

        account, transaction = Caja.create(user, created_by, asof)
        return cls.account, transaction

    def deposit(
        self,
        amount,
        caja=DEFAULT,
        deposited_by=DEFAULT,
        asof=DEFAULT,
        concept=DEFAULT,
    ):
        caja = self.default(caja, self.caja)
        deposited_by = self.default(deposited_by, self.admin)
        asof = self.default(asof, timezone.now())
        concept = self.default(concept, ‘deposit comment’)

        self.caja, transaction = Caja.deposit(
            uid=account.uid,
            deposited_by=deposited_by,
            amount=amount,
            asof=asof,
        )

        self.assertEqual(action.type, Action.ACTION_TYPE_DEPOSITED)
        self.assertIsNotNone(action.user_friendly_id)
        self.assertEqual(action.created, asof)
        self.assertEqual(action.delta, amount)
        self.assertEqual(action.user, deposited_by)

        return action

    def withdraw(
        self,
        amount,
        caja=DEFAULT,
        withdrawn_by=DEFAULT,
        asof=DEFAULT,
        concept=DEFAULT,
    ):
        caja = self.default(caja, self.caja)
        withdrawn_by = self.default(withdrawn_by, self.admin)
        asof = self.default(asof, timezone.now())
        concept = self.default(concept, ‘withdraw comment’)

        self.caja, transaction = Caja.withdraw(
            uid=account.uid,
            withdrawn_by=withdrawn_by,
            amount=amount,
            asof=asof,
            concept=concept
        )

        self.assertEqual(action.type, Action.ACTION_TYPE_WITHDRAWN)
        self.assertIsNotNone(action.user_friendly_id)
        self.assertEqual(action.created, asof)
        self.assertEqual(action.delta, amount)
        self.assertEqual(action.user, withdrawn_by)

        return action
