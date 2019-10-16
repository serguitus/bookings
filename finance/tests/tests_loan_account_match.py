from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone

from accounting.constants import CURRENCY_CUC, CURRENCY_USD
from accounting.models import Account

from finance.constants import (
    STATUS_DRAFT, STATUS_READY,
    ERROR_MATCH_STATUS, ERROR_MATCH_AMOUNT, ERROR_MATCH_ACCOUNT, ERROR_MATCH_LOAN_ACCOUNT)
from finance.models import LoanAccount, LoanAccountDeposit, LoanAccountWithdraw, LoanAccountMatch
from finance.services import FinanceServices
from finance.tests.utils import FinanceBaseTestCase


class FinanceServicesTestCase(FinanceBaseTestCase):

    test_user = None

    def setUp(self):
        self.test_user = User.objects.create(
            username="Test User")

    def test_loan_account_match(self):
        """
        Does match between loan_account_deposit and loan_account_withdraw
        """
        test_account = Account.objects.create(
            name='Test Account',
            currency=CURRENCY_CUC,
            balance=1000)
        test_account2 = Account.objects.create(
            name='Test Loan Account',
            currency=CURRENCY_CUC,
            balance=1000)
        test_loan_account = LoanAccount.objects.create(
            account=test_account2)

        test_date = timezone.now()
        test_amount = 100
        test_status = STATUS_READY

        loan_account_deposit = LoanAccountDeposit(
            date=test_date,
            account=test_account,
            amount=test_amount,
            loan_account=test_loan_account,
            status=test_status)

        loan_account_deposit = FinanceServices.save_loan_account_deposit(
            user=self.test_user,
            loan_account_deposit=loan_account_deposit)

        loan_account_withdraw = LoanAccountWithdraw(
            date=test_date,
            account=test_account,
            amount=test_amount,
            loan_account=test_loan_account,
            status=test_status)

        loan_account_withdraw = FinanceServices.save_loan_account_withdraw(
            user=self.test_user,
            loan_account_withdraw=loan_account_withdraw)

        loan_account_match = LoanAccountMatch(
            loan_account_deposit=loan_account_deposit,
            loan_account_withdraw=loan_account_withdraw,
            matched_amount=test_amount)

        loan_account_match = FinanceServices.save_loan_account_match(loan_account_match)

        test_loan_account = LoanAccount.objects.get(pk=test_loan_account.pk)
        # entity matched incremented
        self.assertEqual(test_loan_account.matched_amount, test_amount)

        loan_account_deposit.refresh_from_db()
        loan_account_withdraw.refresh_from_db()

        self.assertEqual(loan_account_deposit.matched_amount, test_amount)
        self.assertEqual(loan_account_withdraw.matched_amount, test_amount)

    def test_loan_account_match_then_decrease_matched_amount(self):
        """
        Does match between loan_account_deposit and loan_account_withdraw then decrease matched amount
        """
        test_account = Account.objects.create(
            name='Test Account',
            currency=CURRENCY_CUC,
            balance=1000)
        test_account2 = Account.objects.create(
            name='Test Loan Account',
            currency=CURRENCY_CUC,
            balance=1000)
        test_loan_account = LoanAccount.objects.create(
            account=test_account2)

        test_date = timezone.now()
        test_amount = 100
        test_status = STATUS_READY

        loan_account_deposit = LoanAccountDeposit(
            date=test_date,
            account=test_account,
            amount=test_amount,
            loan_account=test_loan_account,
            status=test_status)

        loan_account_deposit = FinanceServices.save_loan_account_deposit(
            user=self.test_user,
            loan_account_deposit=loan_account_deposit)

        loan_account_withdraw = LoanAccountWithdraw(
            date=test_date,
            account=test_account,
            amount=test_amount,
            loan_account=test_loan_account,
            status=test_status)

        loan_account_withdraw = FinanceServices.save_loan_account_withdraw(
            user=self.test_user,
            loan_account_withdraw=loan_account_withdraw)

        loan_account_match = LoanAccountMatch(
            loan_account_deposit=loan_account_deposit,
            loan_account_withdraw=loan_account_withdraw,
            matched_amount=test_amount)

        loan_account_match = FinanceServices.save_loan_account_match(loan_account_match)

        test_loan_account = LoanAccount.objects.get(pk=test_loan_account.pk)
        # entity matched incremented
        self.assertEqual(test_loan_account.matched_amount, test_amount)

        loan_account_deposit.refresh_from_db()
        loan_account_withdraw.refresh_from_db()

        self.assertEqual(loan_account_deposit.matched_amount, test_amount)
        self.assertEqual(loan_account_withdraw.matched_amount, test_amount)

        # change amount
        delta = -10
        loan_account_match.matched_amount += delta

        loan_account_match = FinanceServices.save_loan_account_match(loan_account_match)

        test_loan_account = LoanAccount.objects.get(pk=test_loan_account.pk)
        # entity matched changed
        self.assertEqual(test_loan_account.matched_amount, test_amount + delta)

        loan_account_deposit.refresh_from_db()
        loan_account_withdraw.refresh_from_db()

        self.assertEqual(loan_account_deposit.matched_amount, test_amount + delta)
        self.assertEqual(loan_account_withdraw.matched_amount, test_amount + delta)

    def test_loan_account_match_then_delete(self):
        """
        Does match between loan_account_deposit and loan_account_withdraw then delete
        """
        test_account = Account.objects.create(
            name='Test Account',
            currency=CURRENCY_CUC,
            balance=1000)
        test_account2 = Account.objects.create(
            name='Test Loan Account',
            currency=CURRENCY_CUC,
            balance=1000)
        test_loan_account = LoanAccount.objects.create(
            account=test_account2)

        test_date = timezone.now()
        test_amount = 100
        test_status = STATUS_READY

        loan_account_deposit = LoanAccountDeposit(
            date=test_date,
            account=test_account,
            amount=test_amount,
            loan_account=test_loan_account,
            status=test_status)

        loan_account_deposit = FinanceServices.save_loan_account_deposit(
            user=self.test_user,
            loan_account_deposit=loan_account_deposit)

        loan_account_withdraw = LoanAccountWithdraw(
            date=test_date,
            account=test_account,
            amount=test_amount,
            loan_account=test_loan_account,
            status=test_status)

        loan_account_withdraw = FinanceServices.save_loan_account_withdraw(
            user=self.test_user,
            loan_account_withdraw=loan_account_withdraw)

        loan_account_match = LoanAccountMatch(
            loan_account_deposit=loan_account_deposit,
            loan_account_withdraw=loan_account_withdraw,
            matched_amount=test_amount)

        loan_account_match = FinanceServices.save_loan_account_match(loan_account_match)

        test_loan_account = LoanAccount.objects.get(pk=test_loan_account.pk)
        # entity matched incremented
        self.assertEqual(test_loan_account.matched_amount, test_amount)

        loan_account_deposit.refresh_from_db()
        loan_account_withdraw.refresh_from_db()

        self.assertEqual(loan_account_deposit.matched_amount, test_amount)
        self.assertEqual(loan_account_withdraw.matched_amount, test_amount)

        # delete

        FinanceServices.delete_loan_account_match(loan_account_match.pk)

        loan_account_deposit.refresh_from_db()
        loan_account_withdraw.refresh_from_db()

        self.assertEqual(loan_account_deposit.matched_amount, 0)
        self.assertEqual(loan_account_withdraw.matched_amount, 0)

    def test_loan_account_match_document_draft(self):
        """
        Does match between loan_account_deposit and loan_account_withdraw with draft status
        """
        test_account = Account.objects.create(
            name='Test Account',
            currency=CURRENCY_CUC,
            balance=1000)
        test_account2 = Account.objects.create(
            name='Test Loan Account',
            currency=CURRENCY_CUC,
            balance=1000)
        test_loan_account = LoanAccount.objects.create(
            account=test_account2)

        test_date = timezone.now()
        test_amount = 100
        test_status = STATUS_DRAFT

        loan_account_deposit = LoanAccountDeposit(
            date=test_date,
            account=test_account,
            amount=test_amount,
            loan_account=test_loan_account,
            status=test_status)

        loan_account_deposit = FinanceServices.save_loan_account_deposit(
            user=self.test_user,
            loan_account_deposit=loan_account_deposit)

        loan_account_withdraw = LoanAccountWithdraw(
            date=test_date,
            account=test_account,
            amount=test_amount,
            loan_account=test_loan_account,
            status=test_status)

        loan_account_withdraw = FinanceServices.save_loan_account_withdraw(
            user=self.test_user,
            loan_account_withdraw=loan_account_withdraw)

        loan_account_match = LoanAccountMatch(
            loan_account_deposit=loan_account_deposit,
            loan_account_withdraw=loan_account_withdraw,
            matched_amount=test_amount)

        with self.assertRaises(ValidationError):
            loan_account_match = FinanceServices.save_loan_account_match(loan_account_match)

    def test_loan_account_match_excesive_amount(self):
        """
        Does match between loan_account_deposit and loan_account_withdraw with excesive amount
        """
        test_account = Account.objects.create(
            name='Test Account',
            currency=CURRENCY_CUC,
            balance=1000)
        test_account2 = Account.objects.create(
            name='Test Loan Account',
            currency=CURRENCY_CUC,
            balance=1000)
        test_loan_account = LoanAccount.objects.create(
            account=test_account2)

        test_date = timezone.now()
        test_amount = 100
        test_status = STATUS_READY

        loan_account_deposit = LoanAccountDeposit(
            date=test_date,
            account=test_account,
            amount=test_amount,
            loan_account=test_loan_account,
            status=test_status)

        loan_account_deposit = FinanceServices.save_loan_account_deposit(
            user=self.test_user,
            loan_account_deposit=loan_account_deposit)

        loan_account_withdraw = LoanAccountWithdraw(
            date=test_date,
            account=test_account,
            amount=test_amount,
            loan_account=test_loan_account,
            status=test_status)

        loan_account_withdraw = FinanceServices.save_loan_account_withdraw(
            user=self.test_user,
            loan_account_withdraw=loan_account_withdraw)

        loan_account_match = LoanAccountMatch(
            loan_account_deposit=loan_account_deposit,
            loan_account_withdraw=loan_account_withdraw,
            matched_amount=test_amount + 0.01)

        with self.assertRaises(ValidationError):
            loan_account_match = FinanceServices.save_loan_account_match(loan_account_match)

    def test_loan_account_match_different_loan_account(self):
        """
        Does match between loan_account_deposit and loan_account_withdraw with different loan_entities
        """
        test_account = Account.objects.create(
            name='Test Account',
            currency=CURRENCY_CUC,
            balance=1000)
        test_account2 = Account.objects.create(
            name='Test Loan Account1',
            currency=CURRENCY_CUC,
            balance=1000)
        test_loan_account1 = LoanAccount.objects.create(
            account=test_account2)

        test_date = timezone.now()
        test_amount = 100
        test_status = STATUS_READY

        loan_account_deposit = LoanAccountDeposit(
            date=test_date,
            account=test_account,
            amount=test_amount,
            loan_account=test_loan_account1,
            status=test_status)

        loan_account_deposit = FinanceServices.save_loan_account_deposit(
            user=self.test_user,
            loan_account_deposit=loan_account_deposit)

        test_account4 = Account.objects.create(
            name='Test Loan Account2',
            currency=CURRENCY_CUC,
            balance=1000)
        test_loan_account2 = LoanAccount.objects.create(
            account=test_account4)

        loan_account_withdraw = LoanAccountWithdraw(
            date=test_date,
            account=test_account,
            amount=test_amount,
            loan_account=test_loan_account2,
            status=test_status)

        loan_account_withdraw = FinanceServices.save_loan_account_withdraw(
            user=self.test_user,
            loan_account_withdraw=loan_account_withdraw)

        loan_account_match = LoanAccountMatch(
            loan_account_deposit=loan_account_deposit,
            loan_account_withdraw=loan_account_withdraw,
            matched_amount=test_amount)

        with self.assertRaises(ValidationError):
            loan_account_match = FinanceServices.save_loan_account_match(loan_account_match)

    def test_loan_account_match_different_accounts(self):
        """
        Does match between loan_account_deposit and loan_account_withdraw with different accounts
        """
        test_account1 = Account.objects.create(
            name='Test Account1',
            currency=CURRENCY_CUC,
            balance=1000)
        test_account2 = Account.objects.create(
            name='Test Loan Account',
            currency=CURRENCY_CUC,
            balance=1000)
        test_loan_account = LoanAccount.objects.create(
            account=test_account2)

        test_date = timezone.now()
        test_amount = 100
        test_status = STATUS_READY

        loan_account_deposit = LoanAccountDeposit(
            date=test_date,
            account=test_account1,
            amount=test_amount,
            loan_account=test_loan_account,
            status=test_status)

        loan_account_deposit = FinanceServices.save_loan_account_deposit(
            user=self.test_user,
            loan_account_deposit=loan_account_deposit)

        test_account2 = Account.objects.create(
            name='Test Account2',
            currency=CURRENCY_CUC,
            balance=500)

        loan_account_withdraw = LoanAccountWithdraw(
            date=test_date,
            account=test_account2,
            amount=test_amount,
            loan_account=test_loan_account,
            status=test_status)

        loan_account_withdraw = FinanceServices.save_loan_account_withdraw(
            user=self.test_user,
            loan_account_withdraw=loan_account_withdraw)

        loan_account_match = LoanAccountMatch(
            loan_account_deposit=loan_account_deposit,
            loan_account_withdraw=loan_account_withdraw,
            matched_amount=test_amount)

        with self.assertRaises(ValidationError):
            loan_account_match = FinanceServices.save_loan_account_match(loan_account_match)

    def test_loan_account_match_then_increase_amount(self):
        """
        Does match between loan_account_deposit and loan_account_withdraw then increase amount
        """
        test_account = Account.objects.create(
            name='Test Account',
            currency=CURRENCY_CUC,
            balance=1000)
        test_account2 = Account.objects.create(
            name='Test Loan Account',
            currency=CURRENCY_CUC,
            balance=1000)
        test_loan_account = LoanAccount.objects.create(
            account=test_account2)

        test_date = timezone.now()
        test_amount = 100
        test_status = STATUS_READY

        loan_account_deposit = LoanAccountDeposit(
            date=test_date,
            account=test_account,
            amount=test_amount,
            loan_account=test_loan_account,
            status=test_status)

        loan_account_deposit = FinanceServices.save_loan_account_deposit(
            user=self.test_user,
            loan_account_deposit=loan_account_deposit)

        loan_account_withdraw = LoanAccountWithdraw(
            date=test_date,
            account=test_account,
            amount=test_amount,
            loan_account=test_loan_account,
            status=test_status)

        loan_account_withdraw = FinanceServices.save_loan_account_withdraw(
            user=self.test_user,
            loan_account_withdraw=loan_account_withdraw)

        loan_account_match = LoanAccountMatch(
            loan_account_deposit=loan_account_deposit,
            loan_account_withdraw=loan_account_withdraw,
            matched_amount=test_amount)

        loan_account_match = FinanceServices.save_loan_account_match(loan_account_match)

        loan_account_deposit.refresh_from_db()
        loan_account_withdraw.refresh_from_db()

        self.assertEqual(loan_account_deposit.matched_amount, test_amount)
        self.assertEqual(loan_account_withdraw.matched_amount, test_amount)

        loan_account_withdraw.amount = loan_account_withdraw.amount + 20

        loan_account_withdraw = FinanceServices.save_loan_account_withdraw(
            user=self.test_user,
            loan_account_withdraw=loan_account_withdraw)

        self.assertEqual(loan_account_withdraw.matched_amount, test_amount)

    def test_loan_account_match_then_change_status(self):
        """
        Does match between loan_account_deposit and loan_account_withdraw then change status
        """
        test_account = Account.objects.create(
            name='Test Account',
            currency=CURRENCY_CUC,
            balance=1000)
        test_account2 = Account.objects.create(
            name='Test Loan Account',
            currency=CURRENCY_CUC,
            balance=1000)
        test_loan_account = LoanAccount.objects.create(
            account=test_account2)

        test_date = timezone.now()
        test_amount = 100
        test_status = STATUS_READY

        loan_account_deposit = LoanAccountDeposit(
            date=test_date,
            account=test_account,
            amount=test_amount,
            loan_account=test_loan_account,
            status=test_status)

        loan_account_deposit = FinanceServices.save_loan_account_deposit(
            user=self.test_user,
            loan_account_deposit=loan_account_deposit)

        loan_account_withdraw = LoanAccountWithdraw(
            date=test_date,
            account=test_account,
            amount=test_amount,
            loan_account=test_loan_account,
            status=test_status)

        loan_account_withdraw = FinanceServices.save_loan_account_withdraw(
            user=self.test_user,
            loan_account_withdraw=loan_account_withdraw)

        loan_account_match = LoanAccountMatch(
            loan_account_deposit=loan_account_deposit,
            loan_account_withdraw=loan_account_withdraw,
            matched_amount=test_amount)

        loan_account_match = FinanceServices.save_loan_account_match(loan_account_match)

        loan_account_deposit.refresh_from_db()
        loan_account_withdraw.refresh_from_db()

        self.assertEqual(loan_account_deposit.matched_amount, test_amount)
        self.assertEqual(loan_account_withdraw.matched_amount, test_amount)

        loan_account_withdraw.status = STATUS_DRAFT

        with self.assertRaisesMessage(ValidationError, ERROR_MATCH_STATUS):
            loan_account_withdraw = FinanceServices.save_loan_account_withdraw(
                user=self.test_user,
                loan_account_withdraw=loan_account_withdraw)

    def test_loan_account_match_then_decrease_amount(self):
        """
        Does match between loan_account_deposit and loan_account_withdraw then decrease amount
        """
        test_account = Account.objects.create(
            name='Test Account',
            currency=CURRENCY_CUC,
            balance=1000)
        test_account2 = Account.objects.create(
            name='Test Loan Account',
            currency=CURRENCY_CUC,
            balance=1000)
        test_loan_account = LoanAccount.objects.create(
            account=test_account2)

        test_date = timezone.now()
        test_amount = 100
        test_status = STATUS_READY

        loan_account_deposit = LoanAccountDeposit(
            date=test_date,
            account=test_account,
            amount=test_amount,
            loan_account=test_loan_account,
            status=test_status)

        loan_account_deposit = FinanceServices.save_loan_account_deposit(
            user=self.test_user,
            loan_account_deposit=loan_account_deposit)

        loan_account_withdraw = LoanAccountWithdraw(
            date=test_date,
            account=test_account,
            amount=test_amount,
            loan_account=test_loan_account,
            status=test_status)

        loan_account_withdraw = FinanceServices.save_loan_account_withdraw(
            user=self.test_user,
            loan_account_withdraw=loan_account_withdraw)

        loan_account_match = LoanAccountMatch(
            loan_account_deposit=loan_account_deposit,
            loan_account_withdraw=loan_account_withdraw,
            matched_amount=test_amount)

        loan_account_match = FinanceServices.save_loan_account_match(loan_account_match)

        loan_account_deposit.refresh_from_db()
        loan_account_withdraw.refresh_from_db()

        self.assertEqual(loan_account_deposit.matched_amount, test_amount)
        self.assertEqual(loan_account_withdraw.matched_amount, test_amount)

        loan_account_withdraw.amount = loan_account_withdraw.amount - 20

        with self.assertRaisesMessage(ValidationError, ERROR_MATCH_AMOUNT):
            loan_account_withdraw = FinanceServices.save_loan_account_withdraw(
                user=self.test_user,
                loan_account_withdraw=loan_account_withdraw)

    def test_loan_account_match_then_change_account(self):
        """
        Does match between loan_account_deposit and loan_account_withdraw then change account
        """
        test_account1 = Account.objects.create(
            name='Test Account1',
            currency=CURRENCY_CUC,
            balance=1000)
        test_account2 = Account.objects.create(
            name='Test Loan Account',
            currency=CURRENCY_CUC,
            balance=1000)
        test_loan_account = LoanAccount.objects.create(
            account=test_account2)

        test_date = timezone.now()
        test_amount = 100
        test_status = STATUS_READY

        loan_account_deposit = LoanAccountDeposit(
            date=test_date,
            account=test_account1,
            amount=test_amount,
            loan_account=test_loan_account,
            status=test_status)

        loan_account_deposit = FinanceServices.save_loan_account_deposit(
            user=self.test_user,
            loan_account_deposit=loan_account_deposit)

        loan_account_withdraw = LoanAccountWithdraw(
            date=test_date,
            account=test_account1,
            amount=test_amount,
            loan_account=test_loan_account,
            status=test_status)

        loan_account_withdraw = FinanceServices.save_loan_account_withdraw(
            user=self.test_user,
            loan_account_withdraw=loan_account_withdraw)

        loan_account_match = LoanAccountMatch(
            loan_account_deposit=loan_account_deposit,
            loan_account_withdraw=loan_account_withdraw,
            matched_amount=test_amount)

        loan_account_match = FinanceServices.save_loan_account_match(loan_account_match)

        loan_account_deposit.refresh_from_db()
        loan_account_withdraw.refresh_from_db()

        self.assertEqual(loan_account_deposit.matched_amount, test_amount)
        self.assertEqual(loan_account_withdraw.matched_amount, test_amount)

        test_account2 = Account.objects.create(
            name='Test Account2',
            currency=CURRENCY_CUC,
            balance=500)

        loan_account_withdraw.account = test_account2

        with self.assertRaisesMessage(ValidationError, ERROR_MATCH_ACCOUNT):
            loan_account_withdraw = FinanceServices.save_loan_account_withdraw(
                user=self.test_user,
                loan_account_withdraw=loan_account_withdraw)

    def test_loan_account_match_then_change_loan_account(self):
        """
        Does match between loan_account_deposit and loan_account_withdraw then change loan_account
        """
        test_account = Account.objects.create(
            name='Test Account',
            currency=CURRENCY_CUC,
            balance=1000)
        test_account2 = Account.objects.create(
            name='Test Loan Account1',
            currency=CURRENCY_CUC,
            balance=1000)
        test_loan_account1 = LoanAccount.objects.create(
            account=test_account2)

        test_date = timezone.now()
        test_amount = 100
        test_status = STATUS_READY

        loan_account_deposit = LoanAccountDeposit(
            date=test_date,
            account=test_account,
            amount=test_amount,
            loan_account=test_loan_account1,
            status=test_status)

        loan_account_deposit = FinanceServices.save_loan_account_deposit(
            user=self.test_user,
            loan_account_deposit=loan_account_deposit)

        loan_account_withdraw = LoanAccountWithdraw(
            date=test_date,
            account=test_account,
            amount=test_amount,
            loan_account=test_loan_account1,
            status=test_status)

        loan_account_withdraw = FinanceServices.save_loan_account_withdraw(
            user=self.test_user,
            loan_account_withdraw=loan_account_withdraw)

        loan_account_match = LoanAccountMatch(
            loan_account_deposit=loan_account_deposit,
            loan_account_withdraw=loan_account_withdraw,
            matched_amount=test_amount)

        loan_account_match = FinanceServices.save_loan_account_match(loan_account_match)

        loan_account_deposit.refresh_from_db()
        loan_account_withdraw.refresh_from_db()

        self.assertEqual(loan_account_deposit.matched_amount, test_amount)
        self.assertEqual(loan_account_withdraw.matched_amount, test_amount)

        test_account4 = Account.objects.create(
            name='Test Loan Account2',
            currency=CURRENCY_CUC,
            balance=1000)
        test_loan_account2 = LoanAccount.objects.create(
            account=test_account4)

        loan_account_withdraw.loan_account = test_loan_account2

        with self.assertRaisesMessage(ValidationError, ERROR_MATCH_LOAN_ACCOUNT):
            loan_account_withdraw = FinanceServices.save_loan_account_withdraw(
                user=self.test_user,
                loan_account_withdraw=loan_account_withdraw)
