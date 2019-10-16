from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone

from accounting.constants import CURRENCY_CUC, CURRENCY_USD
from accounting.models import Account

from finance.constants import (
    STATUS_DRAFT, STATUS_READY,
    ERROR_MATCH_STATUS, ERROR_MATCH_AMOUNT, ERROR_MATCH_ACCOUNT, ERROR_MATCH_LOAN_ENTITY)
from finance.models import LoanEntity, LoanEntityDeposit, LoanEntityWithdraw, LoanEntityMatch
from finance.services import FinanceServices
from finance.tests.utils import FinanceBaseTestCase


class FinanceServicesTestCase(FinanceBaseTestCase):

    test_user = None

    def setUp(self):
        self.test_user = User.objects.create(
            username="Test User")

    def test_loan_entity_match(self):
        """
        Does match between loan_entity_deposit and loan_entity_withdraw
        """
        test_account = Account.objects.create(
            name='Test Account',
            currency=CURRENCY_CUC,
            balance=1000)

        test_loan_entity = LoanEntity.objects.create(
            name='Test Loan Entity')

        test_date = timezone.now()
        test_amount = 100
        test_status = STATUS_READY

        loan_entity_deposit = LoanEntityDeposit(
            date=test_date,
            account=test_account,
            amount=test_amount,
            loan_entity=test_loan_entity,
            status=test_status)

        loan_entity_deposit = FinanceServices.save_loan_entity_deposit(
            user=self.test_user,
            loan_entity_deposit=loan_entity_deposit)

        loan_entity_withdraw = LoanEntityWithdraw(
            date=test_date,
            account=test_account,
            amount=test_amount,
            loan_entity=test_loan_entity,
            status=test_status)

        loan_entity_withdraw = FinanceServices.save_loan_entity_withdraw(
            user=self.test_user,
            loan_entity_withdraw=loan_entity_withdraw)

        loan_entity_match = LoanEntityMatch(
            loan_entity_deposit=loan_entity_deposit,
            loan_entity_withdraw=loan_entity_withdraw,
            matched_amount=test_amount)

        loan_entity_match = FinanceServices.save_loan_entity_match(loan_entity_match)

        # entity matched incremented
        self.assertLoanEntityCurrencyMatchedAmount(
            loan_entity=test_loan_entity,
            currency=CURRENCY_CUC,
            amount=test_amount)

        loan_entity_deposit.refresh_from_db()
        loan_entity_withdraw.refresh_from_db()

        self.assertEqual(loan_entity_deposit.matched_amount, test_amount)
        self.assertEqual(loan_entity_withdraw.matched_amount, test_amount)

    def test_loan_entity_match_then_decrease_matched_amount(self):
        """
        Does match between loan_entity_deposit and loan_entity_withdraw then decrease matched amount
        """
        test_account = Account.objects.create(
            name='Test Account',
            currency=CURRENCY_CUC,
            balance=1000)

        test_loan_entity = LoanEntity.objects.create(
            name='Test Loan Entity')

        test_date = timezone.now()
        test_amount = 100
        test_status = STATUS_READY

        loan_entity_deposit = LoanEntityDeposit(
            date=test_date,
            account=test_account,
            amount=test_amount,
            loan_entity=test_loan_entity,
            status=test_status)

        loan_entity_deposit = FinanceServices.save_loan_entity_deposit(
            user=self.test_user,
            loan_entity_deposit=loan_entity_deposit)

        loan_entity_withdraw = LoanEntityWithdraw(
            date=test_date,
            account=test_account,
            amount=test_amount,
            loan_entity=test_loan_entity,
            status=test_status)

        loan_entity_withdraw = FinanceServices.save_loan_entity_withdraw(
            user=self.test_user,
            loan_entity_withdraw=loan_entity_withdraw)

        loan_entity_match = LoanEntityMatch(
            loan_entity_deposit=loan_entity_deposit,
            loan_entity_withdraw=loan_entity_withdraw,
            matched_amount=test_amount)

        loan_entity_match = FinanceServices.save_loan_entity_match(loan_entity_match)

        # entity matched incremented
        self.assertLoanEntityCurrencyMatchedAmount(
            loan_entity=test_loan_entity,
            currency=CURRENCY_CUC,
            amount=test_amount)

        loan_entity_deposit.refresh_from_db()
        loan_entity_withdraw.refresh_from_db()

        self.assertEqual(loan_entity_deposit.matched_amount, test_amount)
        self.assertEqual(loan_entity_withdraw.matched_amount, test_amount)

        # change amount
        delta = -10
        loan_entity_match.matched_amount += delta

        loan_entity_match = FinanceServices.save_loan_entity_match(loan_entity_match)

        # entity matched changed
        self.assertLoanEntityCurrencyMatchedAmount(
            loan_entity=test_loan_entity,
            currency=CURRENCY_CUC,
            amount=test_amount + delta)

        loan_entity_deposit.refresh_from_db()
        loan_entity_withdraw.refresh_from_db()

        self.assertEqual(loan_entity_deposit.matched_amount, test_amount + delta)
        self.assertEqual(loan_entity_withdraw.matched_amount, test_amount + delta)

    def test_loan_entity_match_then_delete(self):
        """
        Does match between loan_entity_deposit and loan_entity_withdraw then delete
        """
        test_account = Account.objects.create(
            name='Test Account',
            currency=CURRENCY_CUC,
            balance=1000)

        test_loan_entity = LoanEntity.objects.create(
            name='Test Loan Entity')

        test_date = timezone.now()
        test_amount = 100
        test_status = STATUS_READY

        loan_entity_deposit = LoanEntityDeposit(
            date=test_date,
            account=test_account,
            amount=test_amount,
            loan_entity=test_loan_entity,
            status=test_status)

        loan_entity_deposit = FinanceServices.save_loan_entity_deposit(
            user=self.test_user,
            loan_entity_deposit=loan_entity_deposit)

        loan_entity_withdraw = LoanEntityWithdraw(
            date=test_date,
            account=test_account,
            amount=test_amount,
            loan_entity=test_loan_entity,
            status=test_status)

        loan_entity_withdraw = FinanceServices.save_loan_entity_withdraw(
            user=self.test_user,
            loan_entity_withdraw=loan_entity_withdraw)

        loan_entity_match = LoanEntityMatch(
            loan_entity_deposit=loan_entity_deposit,
            loan_entity_withdraw=loan_entity_withdraw,
            matched_amount=test_amount)

        loan_entity_match = FinanceServices.save_loan_entity_match(loan_entity_match)

        # entity matched incremented
        self.assertLoanEntityCurrencyMatchedAmount(
            loan_entity=test_loan_entity,
            currency=CURRENCY_CUC,
            amount=test_amount)

        loan_entity_deposit.refresh_from_db()
        loan_entity_withdraw.refresh_from_db()

        self.assertEqual(loan_entity_deposit.matched_amount, test_amount)
        self.assertEqual(loan_entity_withdraw.matched_amount, test_amount)

        FinanceServices.delete_loan_entity_match(loan_entity_match.pk)

        loan_entity_deposit.refresh_from_db()
        loan_entity_withdraw.refresh_from_db()

        self.assertEqual(loan_entity_deposit.matched_amount, 0)
        self.assertEqual(loan_entity_withdraw.matched_amount, 0)

    def test_loan_entity_match_document_draft(self):
        """
        Does match between loan_entity_deposit and loan_entity_withdraw with draft status
        """
        test_account = Account.objects.create(
            name='Test Account',
            currency=CURRENCY_CUC,
            balance=1000)

        test_loan_entity = LoanEntity.objects.create(
            name='Test Loan Entity')

        test_date = timezone.now()
        test_amount = 100
        test_status = STATUS_DRAFT

        loan_entity_deposit = LoanEntityDeposit(
            date=test_date,
            account=test_account,
            amount=test_amount,
            loan_entity=test_loan_entity,
            status=test_status)

        loan_entity_deposit = FinanceServices.save_loan_entity_deposit(
            user=self.test_user,
            loan_entity_deposit=loan_entity_deposit)

        loan_entity_withdraw = LoanEntityWithdraw(
            date=test_date,
            account=test_account,
            amount=test_amount,
            loan_entity=test_loan_entity,
            status=test_status)

        loan_entity_withdraw = FinanceServices.save_loan_entity_withdraw(
            user=self.test_user,
            loan_entity_withdraw=loan_entity_withdraw)

        loan_entity_match = LoanEntityMatch(
            loan_entity_deposit=loan_entity_deposit,
            loan_entity_withdraw=loan_entity_withdraw,
            matched_amount=test_amount)

        with self.assertRaises(ValidationError):
            loan_entity_match = FinanceServices.save_loan_entity_match(loan_entity_match)

    def test_loan_entity_match_excesive_amount(self):
        """
        Does match between loan_entity_deposit and loan_entity_withdraw with excesive amount
        """
        test_account = Account.objects.create(
            name='Test Account',
            currency=CURRENCY_CUC,
            balance=1000)

        test_loan_entity = LoanEntity.objects.create(
            name='Test Loan Entity')

        test_date = timezone.now()
        test_amount = 100
        test_status = STATUS_READY

        loan_entity_deposit = LoanEntityDeposit(
            date=test_date,
            account=test_account,
            amount=test_amount,
            loan_entity=test_loan_entity,
            status=test_status)

        loan_entity_deposit = FinanceServices.save_loan_entity_deposit(
            user=self.test_user,
            loan_entity_deposit=loan_entity_deposit)

        loan_entity_withdraw = LoanEntityWithdraw(
            date=test_date,
            account=test_account,
            amount=test_amount,
            loan_entity=test_loan_entity,
            status=test_status)

        loan_entity_withdraw = FinanceServices.save_loan_entity_withdraw(
            user=self.test_user,
            loan_entity_withdraw=loan_entity_withdraw)

        loan_entity_match = LoanEntityMatch(
            loan_entity_deposit=loan_entity_deposit,
            loan_entity_withdraw=loan_entity_withdraw,
            matched_amount=test_amount + 0.01)

        with self.assertRaises(ValidationError):
            loan_entity_match = FinanceServices.save_loan_entity_match(loan_entity_match)

    def test_loan_entity_match_different_loan_entity(self):
        """
        Does match between loan_entity_deposit and loan_entity_withdraw with different loan_entities
        """
        test_account = Account.objects.create(
            name='Test Account',
            currency=CURRENCY_CUC,
            balance=1000)

        test_loan_entity1 = LoanEntity.objects.create(
            name='Test Loan Entity1')

        test_date = timezone.now()
        test_amount = 100
        test_status = STATUS_READY

        loan_entity_deposit = LoanEntityDeposit(
            date=test_date,
            account=test_account,
            amount=test_amount,
            loan_entity=test_loan_entity1,
            status=test_status)

        loan_entity_deposit = FinanceServices.save_loan_entity_deposit(
            user=self.test_user,
            loan_entity_deposit=loan_entity_deposit)

        test_loan_entity2 = LoanEntity.objects.create(
            name='Test Loan Entity2')

        loan_entity_withdraw = LoanEntityWithdraw(
            date=test_date,
            account=test_account,
            amount=test_amount,
            loan_entity=test_loan_entity2,
            status=test_status)

        loan_entity_withdraw = FinanceServices.save_loan_entity_withdraw(
            user=self.test_user,
            loan_entity_withdraw=loan_entity_withdraw)

        loan_entity_match = LoanEntityMatch(
            loan_entity_deposit=loan_entity_deposit,
            loan_entity_withdraw=loan_entity_withdraw,
            matched_amount=test_amount)

        with self.assertRaises(ValidationError):
            loan_entity_match = FinanceServices.save_loan_entity_match(loan_entity_match)

    def test_loan_entity_match_different_accounts(self):
        """
        Does match between loan_entity_deposit and loan_entity_withdraw with different accounts
        """
        test_account1 = Account.objects.create(
            name='Test Account1',
            currency=CURRENCY_CUC,
            balance=1000)

        test_loan_entity = LoanEntity.objects.create(
            name='Test Loan Entity')

        test_date = timezone.now()
        test_amount = 100
        test_status = STATUS_READY

        loan_entity_deposit = LoanEntityDeposit(
            date=test_date,
            account=test_account1,
            amount=test_amount,
            loan_entity=test_loan_entity,
            status=test_status)

        loan_entity_deposit = FinanceServices.save_loan_entity_deposit(
            user=self.test_user,
            loan_entity_deposit=loan_entity_deposit)

        test_account2 = Account.objects.create(
            name='Test Account2',
            currency=CURRENCY_CUC,
            balance=500)

        loan_entity_withdraw = LoanEntityWithdraw(
            date=test_date,
            account=test_account2,
            amount=test_amount,
            loan_entity=test_loan_entity,
            status=test_status)

        loan_entity_withdraw = FinanceServices.save_loan_entity_withdraw(
            user=self.test_user,
            loan_entity_withdraw=loan_entity_withdraw)

        loan_entity_match = LoanEntityMatch(
            loan_entity_deposit=loan_entity_deposit,
            loan_entity_withdraw=loan_entity_withdraw,
            matched_amount=test_amount)

        with self.assertRaises(ValidationError):
            loan_entity_match = FinanceServices.save_loan_entity_match(loan_entity_match)

    def test_loan_entity_match_then_increase_amount(self):
        """
        Does match between loan_entity_deposit and loan_entity_withdraw then increase amount
        """
        test_account = Account.objects.create(
            name='Test Account',
            currency=CURRENCY_CUC,
            balance=1000)

        test_loan_entity = LoanEntity.objects.create(
            name='Test Loan Entity')

        test_date = timezone.now()
        test_amount = 100
        test_status = STATUS_READY

        loan_entity_deposit = LoanEntityDeposit(
            date=test_date,
            account=test_account,
            amount=test_amount,
            loan_entity=test_loan_entity,
            status=test_status)

        loan_entity_deposit = FinanceServices.save_loan_entity_deposit(
            user=self.test_user,
            loan_entity_deposit=loan_entity_deposit)

        loan_entity_withdraw = LoanEntityWithdraw(
            date=test_date,
            account=test_account,
            amount=test_amount,
            loan_entity=test_loan_entity,
            status=test_status)

        loan_entity_withdraw = FinanceServices.save_loan_entity_withdraw(
            user=self.test_user,
            loan_entity_withdraw=loan_entity_withdraw)

        loan_entity_match = LoanEntityMatch(
            loan_entity_deposit=loan_entity_deposit,
            loan_entity_withdraw=loan_entity_withdraw,
            matched_amount=test_amount)

        loan_entity_match = FinanceServices.save_loan_entity_match(loan_entity_match)

        loan_entity_deposit.refresh_from_db()
        loan_entity_withdraw.refresh_from_db()

        self.assertEqual(loan_entity_deposit.matched_amount, test_amount)
        self.assertEqual(loan_entity_withdraw.matched_amount, test_amount)

        loan_entity_withdraw.amount = loan_entity_withdraw.amount + 20

        loan_entity_withdraw = FinanceServices.save_loan_entity_withdraw(
            user=self.test_user,
            loan_entity_withdraw=loan_entity_withdraw)

        self.assertEqual(loan_entity_withdraw.matched_amount, test_amount)

    def test_loan_entity_match_then_change_status(self):
        """
        Does match between loan_entity_deposit and loan_entity_withdraw then change status
        """
        test_account = Account.objects.create(
            name='Test Account',
            currency=CURRENCY_CUC,
            balance=1000)

        test_loan_entity = LoanEntity.objects.create(
            name='Test Loan Entity')

        test_date = timezone.now()
        test_amount = 100
        test_status = STATUS_READY

        loan_entity_deposit = LoanEntityDeposit(
            date=test_date,
            account=test_account,
            amount=test_amount,
            loan_entity=test_loan_entity,
            status=test_status)

        loan_entity_deposit = FinanceServices.save_loan_entity_deposit(
            user=self.test_user,
            loan_entity_deposit=loan_entity_deposit)

        loan_entity_withdraw = LoanEntityWithdraw(
            date=test_date,
            account=test_account,
            amount=test_amount,
            loan_entity=test_loan_entity,
            status=test_status)

        loan_entity_withdraw = FinanceServices.save_loan_entity_withdraw(
            user=self.test_user,
            loan_entity_withdraw=loan_entity_withdraw)

        loan_entity_match = LoanEntityMatch(
            loan_entity_deposit=loan_entity_deposit,
            loan_entity_withdraw=loan_entity_withdraw,
            matched_amount=test_amount)

        loan_entity_match = FinanceServices.save_loan_entity_match(loan_entity_match)

        loan_entity_deposit.refresh_from_db()
        loan_entity_withdraw.refresh_from_db()

        self.assertEqual(loan_entity_deposit.matched_amount, test_amount)
        self.assertEqual(loan_entity_withdraw.matched_amount, test_amount)

        loan_entity_withdraw.status = STATUS_DRAFT

        with self.assertRaisesMessage(ValidationError, ERROR_MATCH_STATUS):
            loan_entity_withdraw = FinanceServices.save_loan_entity_withdraw(
                user=self.test_user,
                loan_entity_withdraw=loan_entity_withdraw)

    def test_loan_entity_match_then_decrease_amount(self):
        """
        Does match between loan_entity_deposit and loan_entity_withdraw then decrease amount
        """
        test_account = Account.objects.create(
            name='Test Account',
            currency=CURRENCY_CUC,
            balance=1000)

        test_loan_entity = LoanEntity.objects.create(
            name='Test Loan Entity')

        test_date = timezone.now()
        test_amount = 100
        test_status = STATUS_READY

        loan_entity_deposit = LoanEntityDeposit(
            date=test_date,
            account=test_account,
            amount=test_amount,
            loan_entity=test_loan_entity,
            status=test_status)

        loan_entity_deposit = FinanceServices.save_loan_entity_deposit(
            user=self.test_user,
            loan_entity_deposit=loan_entity_deposit)

        loan_entity_withdraw = LoanEntityWithdraw(
            date=test_date,
            account=test_account,
            amount=test_amount,
            loan_entity=test_loan_entity,
            status=test_status)

        loan_entity_withdraw = FinanceServices.save_loan_entity_withdraw(
            user=self.test_user,
            loan_entity_withdraw=loan_entity_withdraw)

        loan_entity_match = LoanEntityMatch(
            loan_entity_deposit=loan_entity_deposit,
            loan_entity_withdraw=loan_entity_withdraw,
            matched_amount=test_amount)

        loan_entity_match = FinanceServices.save_loan_entity_match(loan_entity_match)

        loan_entity_deposit.refresh_from_db()
        loan_entity_withdraw.refresh_from_db()

        self.assertEqual(loan_entity_deposit.matched_amount, test_amount)
        self.assertEqual(loan_entity_withdraw.matched_amount, test_amount)

        loan_entity_withdraw.amount = loan_entity_withdraw.amount - 20

        with self.assertRaisesMessage(ValidationError, ERROR_MATCH_AMOUNT):
            loan_entity_withdraw = FinanceServices.save_loan_entity_withdraw(
                user=self.test_user,
                loan_entity_withdraw=loan_entity_withdraw)

    def test_loan_entity_match_then_change_account(self):
        """
        Does match between loan_entity_deposit and loan_entity_withdraw then change account
        """
        test_account1 = Account.objects.create(
            name='Test Account1',
            currency=CURRENCY_CUC,
            balance=1000)

        test_loan_entity = LoanEntity.objects.create(
            name='Test Loan Entity')

        test_date = timezone.now()
        test_amount = 100
        test_status = STATUS_READY

        loan_entity_deposit = LoanEntityDeposit(
            date=test_date,
            account=test_account1,
            amount=test_amount,
            loan_entity=test_loan_entity,
            status=test_status)

        loan_entity_deposit = FinanceServices.save_loan_entity_deposit(
            user=self.test_user,
            loan_entity_deposit=loan_entity_deposit)

        loan_entity_withdraw = LoanEntityWithdraw(
            date=test_date,
            account=test_account1,
            amount=test_amount,
            loan_entity=test_loan_entity,
            status=test_status)

        loan_entity_withdraw = FinanceServices.save_loan_entity_withdraw(
            user=self.test_user,
            loan_entity_withdraw=loan_entity_withdraw)

        loan_entity_match = LoanEntityMatch(
            loan_entity_deposit=loan_entity_deposit,
            loan_entity_withdraw=loan_entity_withdraw,
            matched_amount=test_amount)

        loan_entity_match = FinanceServices.save_loan_entity_match(loan_entity_match)

        loan_entity_deposit.refresh_from_db()
        loan_entity_withdraw.refresh_from_db()

        self.assertEqual(loan_entity_deposit.matched_amount, test_amount)
        self.assertEqual(loan_entity_withdraw.matched_amount, test_amount)

        test_account2 = Account.objects.create(
            name='Test Account2',
            currency=CURRENCY_CUC,
            balance=500)

        loan_entity_withdraw.account = test_account2

        with self.assertRaisesMessage(ValidationError, ERROR_MATCH_ACCOUNT):
            loan_entity_withdraw = FinanceServices.save_loan_entity_withdraw(
                user=self.test_user,
                loan_entity_withdraw=loan_entity_withdraw)

    def test_loan_entity_match_then_change_loan_entity(self):
        """
        Does match between loan_entity_deposit and loan_entity_withdraw then change loan_entity
        """
        test_account = Account.objects.create(
            name='Test Account',
            currency=CURRENCY_CUC,
            balance=1000)

        test_loan_entity1 = LoanEntity.objects.create(
            name='Test Loan Entity1')

        test_date = timezone.now()
        test_amount = 100
        test_status = STATUS_READY

        loan_entity_deposit = LoanEntityDeposit(
            date=test_date,
            account=test_account,
            amount=test_amount,
            loan_entity=test_loan_entity1,
            status=test_status)

        loan_entity_deposit = FinanceServices.save_loan_entity_deposit(
            user=self.test_user,
            loan_entity_deposit=loan_entity_deposit)

        loan_entity_withdraw = LoanEntityWithdraw(
            date=test_date,
            account=test_account,
            amount=test_amount,
            loan_entity=test_loan_entity1,
            status=test_status)

        loan_entity_withdraw = FinanceServices.save_loan_entity_withdraw(
            user=self.test_user,
            loan_entity_withdraw=loan_entity_withdraw)

        loan_entity_match = LoanEntityMatch(
            loan_entity_deposit=loan_entity_deposit,
            loan_entity_withdraw=loan_entity_withdraw,
            matched_amount=test_amount)

        loan_entity_match = FinanceServices.save_loan_entity_match(loan_entity_match)

        loan_entity_deposit.refresh_from_db()
        loan_entity_withdraw.refresh_from_db()

        self.assertEqual(loan_entity_deposit.matched_amount, test_amount)
        self.assertEqual(loan_entity_withdraw.matched_amount, test_amount)

        test_loan_entity2 = LoanEntity.objects.create(
            name='Test Loan Entity2')

        loan_entity_withdraw.loan_entity = test_loan_entity2

        with self.assertRaisesMessage(ValidationError, ERROR_MATCH_LOAN_ENTITY):
            loan_entity_withdraw = FinanceServices.save_loan_entity_withdraw(
                user=self.test_user,
                loan_entity_withdraw=loan_entity_withdraw)
