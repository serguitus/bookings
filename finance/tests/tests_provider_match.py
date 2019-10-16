from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone

from accounting.constants import CURRENCY_CUC, CURRENCY_USD
from accounting.models import Account

from finance.constants import (
    STATUS_DRAFT, STATUS_READY,
    ERROR_MATCH_STATUS, ERROR_MATCH_AMOUNT, ERROR_MATCH_PROVIDER)
from finance.models import Provider, ProviderInvoice, ProviderPayment, ProviderDocumentMatch
from finance.services import FinanceServices
from finance.tests.utils import FinanceBaseTestCase


class FinanceServicesTestCase(FinanceBaseTestCase):

    test_user = None

    def setUp(self):
        self.test_user = User.objects.create(
            username="Test User")

    def test_provider_match(self):
        """
        Does match between provider_payment and provider_invoice
        """
        test_account = Account.objects.create(
            name='Test Account',
            currency=CURRENCY_CUC,
            balance=1000)

        test_provider = Provider.objects.create(
            name='Test Provider')

        test_date = timezone.now()
        test_amount = 100
        test_status = STATUS_READY

        provider_payment = ProviderPayment(
            date=test_date,
            account=test_account,
            amount=test_amount,
            provider=test_provider,
            status=test_status)

        provider_payment = FinanceServices.save_provider_payment(
            user=self.test_user,
            provider_payment=provider_payment)

        provider_invoice = ProviderInvoice(
            date=test_date,
            amount=test_amount,
            provider=test_provider,
            status=test_status)

        provider_invoice = FinanceServices.save_provider_invoice(
            user=self.test_user,
            provider_invoice=provider_invoice)

        provider_match = ProviderDocumentMatch(
            credit_document=provider_payment,
            debit_document=provider_invoice,
            matched_amount=test_amount)

        provider_match = FinanceServices.save_provider_match(provider_match)

        # entity matched incremented
        self.assertProviderCurrencyMatchedAmount(
            provider=test_provider,
            currency=CURRENCY_CUC,
            amount=test_amount)

        provider_payment.refresh_from_db()
        provider_invoice.refresh_from_db()

        self.assertEqual(provider_payment.matched_amount, test_amount)
        self.assertEqual(provider_invoice.matched_amount, test_amount)

    def test_provider_match_then_decrease_matched_amount(self):
        """
        Does match between provider_payment and provider_invoice then decrease matched amount
        """
        test_account = Account.objects.create(
            name='Test Account',
            currency=CURRENCY_CUC,
            balance=1000)

        test_provider = Provider.objects.create(
            name='Test Provider')

        test_date = timezone.now()
        test_amount = 100
        test_status = STATUS_READY

        provider_payment = ProviderPayment(
            date=test_date,
            account=test_account,
            amount=test_amount,
            provider=test_provider,
            status=test_status)

        provider_payment = FinanceServices.save_provider_payment(
            user=self.test_user,
            provider_payment=provider_payment)

        provider_invoice = ProviderInvoice(
            date=test_date,
            amount=test_amount,
            provider=test_provider,
            status=test_status)

        provider_invoice = FinanceServices.save_provider_invoice(
            user=self.test_user,
            provider_invoice=provider_invoice)

        provider_match = ProviderDocumentMatch(
            credit_document=provider_payment,
            debit_document=provider_invoice,
            matched_amount=test_amount)

        provider_match = FinanceServices.save_provider_match(provider_match)

        # entity matched incremented
        self.assertProviderCurrencyMatchedAmount(
            provider=test_provider,
            currency=CURRENCY_CUC,
            amount=test_amount)

        provider_payment.refresh_from_db()
        provider_invoice.refresh_from_db()

        self.assertEqual(provider_payment.matched_amount, test_amount)
        self.assertEqual(provider_invoice.matched_amount, test_amount)

        # change amount
        delta = -10
        provider_match.matched_amount += delta

        provider_match = FinanceServices.save_provider_match(provider_match)

        # entity matched changed
        self.assertProviderCurrencyMatchedAmount(
            provider=test_provider,
            currency=CURRENCY_CUC,
            amount=test_amount + delta)

        provider_payment.refresh_from_db()
        provider_invoice.refresh_from_db()

        self.assertEqual(provider_payment.matched_amount, test_amount + delta)
        self.assertEqual(provider_invoice.matched_amount, test_amount + delta)

    def test_provider_match_then_delete(self):
        """
        Does match between provider_payment and provider_invoice then delete
        """
        test_account = Account.objects.create(
            name='Test Account',
            currency=CURRENCY_CUC,
            balance=1000)

        test_provider = Provider.objects.create(
            name='Test Provider')

        test_date = timezone.now()
        test_amount = 100
        test_status = STATUS_READY

        provider_payment = ProviderPayment(
            date=test_date,
            account=test_account,
            amount=test_amount,
            provider=test_provider,
            status=test_status)

        provider_payment = FinanceServices.save_provider_payment(
            user=self.test_user,
            provider_payment=provider_payment)

        provider_invoice = ProviderInvoice(
            date=test_date,
            amount=test_amount,
            provider=test_provider,
            status=test_status)

        provider_invoice = FinanceServices.save_provider_invoice(
            user=self.test_user,
            provider_invoice=provider_invoice)

        provider_match = ProviderDocumentMatch(
            credit_document=provider_payment,
            debit_document=provider_invoice,
            matched_amount=test_amount)

        provider_match = FinanceServices.save_provider_match(provider_match)

        # entity matched incremented
        self.assertProviderCurrencyMatchedAmount(
            provider=test_provider,
            currency=CURRENCY_CUC,
            amount=test_amount)

        provider_payment.refresh_from_db()
        provider_invoice.refresh_from_db()

        self.assertEqual(provider_payment.matched_amount, test_amount)
        self.assertEqual(provider_invoice.matched_amount, test_amount)

        # delete
        FinanceServices.delete_provider_match(provider_match.pk)

        provider_payment.refresh_from_db()
        provider_invoice.refresh_from_db()

        self.assertEqual(provider_payment.matched_amount, 0)
        self.assertEqual(provider_invoice.matched_amount, 0)

    def test_provider_match_document_draft(self):
        """
        Does match between provider_payment and provider_invoice with draft status
        """
        test_account = Account.objects.create(
            name='Test Account',
            currency=CURRENCY_CUC,
            balance=1000)

        test_provider = Provider.objects.create(
            name='Test Provider')

        test_date = timezone.now()
        test_amount = 100
        test_status = STATUS_DRAFT

        provider_payment = ProviderPayment(
            date=test_date,
            account=test_account,
            amount=test_amount,
            provider=test_provider,
            status=test_status)

        provider_payment = FinanceServices.save_provider_payment(
            user=self.test_user,
            provider_payment=provider_payment)

        provider_invoice = ProviderInvoice(
            date=test_date,
            amount=test_amount,
            provider=test_provider,
            status=test_status)

        provider_invoice = FinanceServices.save_provider_invoice(
            user=self.test_user,
            provider_invoice=provider_invoice)

        provider_match = ProviderDocumentMatch(
            credit_document=provider_payment,
            debit_document=provider_invoice,
            matched_amount=test_amount)

        with self.assertRaises(ValidationError):
            provider_match = FinanceServices.save_provider_match(provider_match)

    def test_provider_match_excesive_amount(self):
        """
        Does match between provider_payment and provider_invoice with excesive amount
        """
        test_account = Account.objects.create(
            name='Test Account',
            currency=CURRENCY_CUC,
            balance=1000)

        test_provider = Provider.objects.create(
            name='Test Provider')

        test_date = timezone.now()
        test_amount = 100
        test_status = STATUS_READY

        provider_payment = ProviderPayment(
            date=test_date,
            account=test_account,
            amount=test_amount,
            provider=test_provider,
            status=test_status)

        provider_payment = FinanceServices.save_provider_payment(
            user=self.test_user,
            provider_payment=provider_payment)

        provider_invoice = ProviderInvoice(
            date=test_date,
            amount=test_amount,
            provider=test_provider,
            status=test_status)

        provider_invoice = FinanceServices.save_provider_invoice(
            user=self.test_user,
            provider_invoice=provider_invoice)

        provider_match = ProviderDocumentMatch(
            credit_document=provider_payment,
            debit_document=provider_invoice,
            matched_amount=test_amount + 0.01)

        with self.assertRaises(ValidationError):
            provider_match = FinanceServices.save_provider_match(provider_match)

    def test_provider_match_different_provider(self):
        """
        Does match between provider_payment and provider_invoice with different loan_entities
        """
        test_account = Account.objects.create(
            name='Test Account',
            currency=CURRENCY_CUC,
            balance=1000)

        test_provider1 = Provider.objects.create(
            name='Test Provider1')

        test_date = timezone.now()
        test_amount = 100
        test_status = STATUS_READY

        provider_payment = ProviderPayment(
            date=test_date,
            account=test_account,
            amount=test_amount,
            provider=test_provider1,
            status=test_status)

        provider_payment = FinanceServices.save_provider_payment(
            user=self.test_user,
            provider_payment=provider_payment)

        test_provider2 = Provider.objects.create(
            name='Test Provider2')

        provider_invoice = ProviderInvoice(
            date=test_date,
            amount=test_amount,
            provider=test_provider2,
            status=test_status)

        provider_invoice = FinanceServices.save_provider_invoice(
            user=self.test_user,
            provider_invoice=provider_invoice)

        provider_match = ProviderDocumentMatch(
            credit_document=provider_payment,
            debit_document=provider_invoice,
            matched_amount=test_amount)

        with self.assertRaises(ValidationError):
            provider_match = FinanceServices.save_provider_match(provider_match)

    def test_provider_match_then_increase_amount(self):
        """
        Does match between provider_payment and provider_invoice then increase amount
        """
        test_account = Account.objects.create(
            name='Test Account',
            currency=CURRENCY_CUC,
            balance=1000)

        test_provider = Provider.objects.create(
            name='Test Provider')

        test_date = timezone.now()
        test_amount = 100
        test_status = STATUS_READY

        provider_payment = ProviderPayment(
            date=test_date,
            account=test_account,
            amount=test_amount,
            provider=test_provider,
            status=test_status)

        provider_payment = FinanceServices.save_provider_payment(
            user=self.test_user,
            provider_payment=provider_payment)

        provider_invoice = ProviderInvoice(
            date=test_date,
            amount=test_amount,
            provider=test_provider,
            status=test_status)

        provider_invoice = FinanceServices.save_provider_invoice(
            user=self.test_user,
            provider_invoice=provider_invoice)

        provider_match = ProviderDocumentMatch(
            credit_document=provider_payment,
            debit_document=provider_invoice,
            matched_amount=test_amount)

        provider_match = FinanceServices.save_provider_match(provider_match)

        provider_payment.refresh_from_db()
        provider_invoice.refresh_from_db()

        self.assertEqual(provider_payment.matched_amount, test_amount)
        self.assertEqual(provider_invoice.matched_amount, test_amount)

        provider_invoice.amount = provider_invoice.amount + 20

        provider_invoice = FinanceServices.save_provider_invoice(
            user=self.test_user,
            provider_invoice=provider_invoice)

        self.assertEqual(provider_invoice.matched_amount, test_amount)

    def test_provider_match_then_change_status(self):
        """
        Does match between provider_payment and provider_invoice then change status
        """
        test_account = Account.objects.create(
            name='Test Account',
            currency=CURRENCY_CUC,
            balance=1000)

        test_provider = Provider.objects.create(
            name='Test Provider')

        test_date = timezone.now()
        test_amount = 100
        test_status = STATUS_READY

        provider_payment = ProviderPayment(
            date=test_date,
            account=test_account,
            amount=test_amount,
            provider=test_provider,
            status=test_status)

        provider_payment = FinanceServices.save_provider_payment(
            user=self.test_user,
            provider_payment=provider_payment)

        provider_invoice = ProviderInvoice(
            date=test_date,
            amount=test_amount,
            provider=test_provider,
            status=test_status)

        provider_invoice = FinanceServices.save_provider_invoice(
            user=self.test_user,
            provider_invoice=provider_invoice)

        provider_match = ProviderDocumentMatch(
            credit_document=provider_payment,
            debit_document=provider_invoice,
            matched_amount=test_amount)

        provider_match = FinanceServices.save_provider_match(provider_match)

        provider_payment.refresh_from_db()
        provider_invoice.refresh_from_db()

        self.assertEqual(provider_payment.matched_amount, test_amount)
        self.assertEqual(provider_invoice.matched_amount, test_amount)

        provider_invoice.status = STATUS_DRAFT

        with self.assertRaisesMessage(ValidationError, ERROR_MATCH_STATUS):
            provider_invoice = FinanceServices.save_provider_invoice(
                user=self.test_user,
                provider_invoice=provider_invoice)

    def test_provider_match_then_decrease_amount(self):
        """
        Does match between provider_payment and provider_invoice then decrease amount
        """
        test_account = Account.objects.create(
            name='Test Account',
            currency=CURRENCY_CUC,
            balance=1000)

        test_provider = Provider.objects.create(
            name='Test Provider')

        test_date = timezone.now()
        test_amount = 100
        test_status = STATUS_READY

        provider_payment = ProviderPayment(
            date=test_date,
            account=test_account,
            amount=test_amount,
            provider=test_provider,
            status=test_status)

        provider_payment = FinanceServices.save_provider_payment(
            user=self.test_user,
            provider_payment=provider_payment)

        provider_invoice = ProviderInvoice(
            date=test_date,
            amount=test_amount,
            provider=test_provider,
            status=test_status)

        provider_invoice = FinanceServices.save_provider_invoice(
            user=self.test_user,
            provider_invoice=provider_invoice)

        provider_match = ProviderDocumentMatch(
            credit_document=provider_payment,
            debit_document=provider_invoice,
            matched_amount=test_amount)

        provider_match = FinanceServices.save_provider_match(provider_match)

        provider_payment.refresh_from_db()
        provider_invoice.refresh_from_db()

        self.assertEqual(provider_payment.matched_amount, test_amount)
        self.assertEqual(provider_invoice.matched_amount, test_amount)

        provider_invoice.amount = provider_invoice.amount - 20

        with self.assertRaisesMessage(ValidationError, ERROR_MATCH_AMOUNT):
            provider_invoice = FinanceServices.save_provider_invoice(
                user=self.test_user,
                provider_invoice=provider_invoice)

    def test_provider_match_then_change_provider(self):
        """
        Does match between provider_payment and provider_invoice then change provider
        """
        test_account = Account.objects.create(
            name='Test Account',
            currency=CURRENCY_CUC,
            balance=1000)

        test_provider1 = Provider.objects.create(
            name='Test Provider1')

        test_date = timezone.now()
        test_amount = 100
        test_status = STATUS_READY

        provider_payment = ProviderPayment(
            date=test_date,
            account=test_account,
            amount=test_amount,
            provider=test_provider1,
            status=test_status)

        provider_payment = FinanceServices.save_provider_payment(
            user=self.test_user,
            provider_payment=provider_payment)

        provider_invoice = ProviderInvoice(
            date=test_date,
            amount=test_amount,
            provider=test_provider1,
            status=test_status)

        provider_invoice = FinanceServices.save_provider_invoice(
            user=self.test_user,
            provider_invoice=provider_invoice)

        provider_match = ProviderDocumentMatch(
            credit_document=provider_payment,
            debit_document=provider_invoice,
            matched_amount=test_amount)

        provider_match = FinanceServices.save_provider_match(provider_match)

        provider_payment.refresh_from_db()
        provider_invoice.refresh_from_db()

        self.assertEqual(provider_payment.matched_amount, test_amount)
        self.assertEqual(provider_invoice.matched_amount, test_amount)

        test_provider2 = Provider.objects.create(
            name='Test Provider2')

        provider_invoice.provider = test_provider2

        with self.assertRaisesMessage(ValidationError, ERROR_MATCH_PROVIDER):
            provider_invoice = FinanceServices.save_provider_invoice(
                user=self.test_user,
                provider_invoice=provider_invoice)
