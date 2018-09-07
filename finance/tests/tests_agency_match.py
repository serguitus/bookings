from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone

from accounting.constants import CURRENCY_CUC, CURRENCY_USD
from accounting.models import Account

from finance.constants import (
    STATUS_DRAFT, STATUS_READY,
    ERROR_MATCH_STATUS, ERROR_MATCH_AMOUNT, ERROR_MATCH_AGENCY)
from finance.models import Agency, AgencyInvoice, AgencyPayment, AgencyDocumentMatch
from finance.services import FinanceService
from finance.tests.utils import FinanceBaseTestCase


class FinanceServiceTestCase(FinanceBaseTestCase):

    test_user = None

    def setUp(self):
        self.test_user = User.objects.create(
            username="Test User")

    def test_agency_match(self):
        """
        Does match between agency_payment and agency_invoice
        """
        test_account = Account.objects.create(
            name='Test Account',
            currency=CURRENCY_CUC,
            balance=1000)

        test_agency = Agency.objects.create(
            name='Test Agency')

        test_date = timezone.now()
        test_amount = 100
        test_status = STATUS_READY

        agency_payment = AgencyPayment(
            date=test_date,
            account=test_account,
            amount=test_amount,
            agency=test_agency,
            status=test_status)

        agency_payment = FinanceService.save_agency_payment(
            user=self.test_user,
            agency_payment=agency_payment)

        agency_invoice = AgencyInvoice(
            date=test_date,
            amount=test_amount,
            agency=test_agency,
            status=test_status)

        agency_invoice = FinanceService.save_agency_invoice(
            user=self.test_user,
            agency_invoice=agency_invoice)

        agency_match = AgencyDocumentMatch(
            credit_document=agency_payment,
            debit_document=agency_invoice,
            matched_amount=test_amount)

        agency_match = FinanceService.save_agency_match(agency_match)

        # entity matched incremented
        self.assertAgencyCurrencyMatchedAmount(
            agency=test_agency,
            currency=CURRENCY_CUC,
            amount=test_amount)

        agency_payment.refresh_from_db()
        agency_invoice.refresh_from_db()

        self.assertEqual(agency_payment.matched_amount, test_amount)
        self.assertEqual(agency_invoice.matched_amount, test_amount)

    def test_agency_match_then_decrease_matched_amount(self):
        """
        Does match between agency_payment and agency_invoice then decrease matched amount
        """
        test_account = Account.objects.create(
            name='Test Account',
            currency=CURRENCY_CUC,
            balance=1000)

        test_agency = Agency.objects.create(
            name='Test Agency')

        test_date = timezone.now()
        test_amount = 100
        test_status = STATUS_READY

        agency_payment = AgencyPayment(
            date=test_date,
            account=test_account,
            amount=test_amount,
            agency=test_agency,
            status=test_status)

        agency_payment = FinanceService.save_agency_payment(
            user=self.test_user,
            agency_payment=agency_payment)

        agency_invoice = AgencyInvoice(
            date=test_date,
            amount=test_amount,
            agency=test_agency,
            status=test_status)

        agency_invoice = FinanceService.save_agency_invoice(
            user=self.test_user,
            agency_invoice=agency_invoice)

        agency_match = AgencyDocumentMatch(
            credit_document=agency_payment,
            debit_document=agency_invoice,
            matched_amount=test_amount)

        agency_match = FinanceService.save_agency_match(agency_match)

        # entity matched incremented
        self.assertAgencyCurrencyMatchedAmount(
            agency=test_agency,
            currency=CURRENCY_CUC,
            amount=test_amount)

        agency_payment.refresh_from_db()
        agency_invoice.refresh_from_db()

        self.assertEqual(agency_payment.matched_amount, test_amount)
        self.assertEqual(agency_invoice.matched_amount, test_amount)

        # change amount
        delta = -10
        agency_match.matched_amount += delta

        agency_match = FinanceService.save_agency_match(agency_match)

        # entity matched changed
        self.assertAgencyCurrencyMatchedAmount(
            agency=test_agency,
            currency=CURRENCY_CUC,
            amount=test_amount + delta)

        agency_payment.refresh_from_db()
        agency_invoice.refresh_from_db()

        self.assertEqual(agency_payment.matched_amount, test_amount + delta)
        self.assertEqual(agency_invoice.matched_amount, test_amount + delta)

    def test_agency_match_then_delete(self):
        """
        Does match between agency_payment and agency_invoice then delete
        """
        test_account = Account.objects.create(
            name='Test Account',
            currency=CURRENCY_CUC,
            balance=1000)

        test_agency = Agency.objects.create(
            name='Test Agency')

        test_date = timezone.now()
        test_amount = 100
        test_status = STATUS_READY

        agency_payment = AgencyPayment(
            date=test_date,
            account=test_account,
            amount=test_amount,
            agency=test_agency,
            status=test_status)

        agency_payment = FinanceService.save_agency_payment(
            user=self.test_user,
            agency_payment=agency_payment)

        agency_invoice = AgencyInvoice(
            date=test_date,
            amount=test_amount,
            agency=test_agency,
            status=test_status)

        agency_invoice = FinanceService.save_agency_invoice(
            user=self.test_user,
            agency_invoice=agency_invoice)

        agency_match = AgencyDocumentMatch(
            credit_document=agency_payment,
            debit_document=agency_invoice,
            matched_amount=test_amount)

        agency_match = FinanceService.save_agency_match(agency_match)

        # entity matched incremented
        self.assertAgencyCurrencyMatchedAmount(
            agency=test_agency,
            currency=CURRENCY_CUC,
            amount=test_amount)

        agency_payment.refresh_from_db()
        agency_invoice.refresh_from_db()

        self.assertEqual(agency_payment.matched_amount, test_amount)
        self.assertEqual(agency_invoice.matched_amount, test_amount)

        # delete
        FinanceService.delete_agency_match(agency_match.pk)

        agency_payment.refresh_from_db()
        agency_invoice.refresh_from_db()

        self.assertEqual(agency_payment.matched_amount, 0)
        self.assertEqual(agency_invoice.matched_amount, 0)

    def test_agency_match_document_draft(self):
        """
        Does match between agency_payment and agency_invoice with draft status
        """
        test_account = Account.objects.create(
            name='Test Account',
            currency=CURRENCY_CUC,
            balance=1000)

        test_agency = Agency.objects.create(
            name='Test Agency')

        test_date = timezone.now()
        test_amount = 100
        test_status = STATUS_DRAFT

        agency_payment = AgencyPayment(
            date=test_date,
            account=test_account,
            amount=test_amount,
            agency=test_agency,
            status=test_status)

        agency_payment = FinanceService.save_agency_payment(
            user=self.test_user,
            agency_payment=agency_payment)

        agency_invoice = AgencyInvoice(
            date=test_date,
            amount=test_amount,
            agency=test_agency,
            status=test_status)

        agency_invoice = FinanceService.save_agency_invoice(
            user=self.test_user,
            agency_invoice=agency_invoice)

        agency_match = AgencyDocumentMatch(
            credit_document=agency_payment,
            debit_document=agency_invoice,
            matched_amount=test_amount)

        with self.assertRaises(ValidationError):
            agency_match = FinanceService.save_agency_match(agency_match)

    def test_agency_match_excesive_amount(self):
        """
        Does match between agency_payment and agency_invoice with excesive amount
        """
        test_account = Account.objects.create(
            name='Test Account',
            currency=CURRENCY_CUC,
            balance=1000)

        test_agency = Agency.objects.create(
            name='Test Agency')

        test_date = timezone.now()
        test_amount = 100
        test_status = STATUS_READY

        agency_payment = AgencyPayment(
            date=test_date,
            account=test_account,
            amount=test_amount,
            agency=test_agency,
            status=test_status)

        agency_payment = FinanceService.save_agency_payment(
            user=self.test_user,
            agency_payment=agency_payment)

        agency_invoice = AgencyInvoice(
            date=test_date,
            amount=test_amount,
            agency=test_agency,
            status=test_status)

        agency_invoice = FinanceService.save_agency_invoice(
            user=self.test_user,
            agency_invoice=agency_invoice)

        agency_match = AgencyDocumentMatch(
            credit_document=agency_payment,
            debit_document=agency_invoice,
            matched_amount=test_amount + 0.01)

        with self.assertRaises(ValidationError):
            agency_match = FinanceService.save_agency_match(agency_match)

    def test_agency_match_different_agency(self):
        """
        Does match between agency_payment and agency_invoice with different loan_entities
        """
        test_account = Account.objects.create(
            name='Test Account',
            currency=CURRENCY_CUC,
            balance=1000)

        test_agency1 = Agency.objects.create(
            name='Test Agency1')

        test_date = timezone.now()
        test_amount = 100
        test_status = STATUS_READY

        agency_payment = AgencyPayment(
            date=test_date,
            account=test_account,
            amount=test_amount,
            agency=test_agency1,
            status=test_status)

        agency_payment = FinanceService.save_agency_payment(
            user=self.test_user,
            agency_payment=agency_payment)

        test_agency2 = Agency.objects.create(
            name='Test Agency2')

        agency_invoice = AgencyInvoice(
            date=test_date,
            amount=test_amount,
            agency=test_agency2,
            status=test_status)

        agency_invoice = FinanceService.save_agency_invoice(
            user=self.test_user,
            agency_invoice=agency_invoice)

        agency_match = AgencyDocumentMatch(
            credit_document=agency_payment,
            debit_document=agency_invoice,
            matched_amount=test_amount)

        with self.assertRaises(ValidationError):
            agency_match = FinanceService.save_agency_match(agency_match)

    def test_agency_match_then_increase_amount(self):
        """
        Does match between agency_payment and agency_invoice then increase amount
        """
        test_account = Account.objects.create(
            name='Test Account',
            currency=CURRENCY_CUC,
            balance=1000)

        test_agency = Agency.objects.create(
            name='Test Agency')

        test_date = timezone.now()
        test_amount = 100
        test_status = STATUS_READY

        agency_payment = AgencyPayment(
            date=test_date,
            account=test_account,
            amount=test_amount,
            agency=test_agency,
            status=test_status)

        agency_payment = FinanceService.save_agency_payment(
            user=self.test_user,
            agency_payment=agency_payment)

        agency_invoice = AgencyInvoice(
            date=test_date,
            amount=test_amount,
            agency=test_agency,
            status=test_status)

        agency_invoice = FinanceService.save_agency_invoice(
            user=self.test_user,
            agency_invoice=agency_invoice)

        agency_match = AgencyDocumentMatch(
            credit_document=agency_payment,
            debit_document=agency_invoice,
            matched_amount=test_amount)

        agency_match = FinanceService.save_agency_match(agency_match)

        agency_payment.refresh_from_db()
        agency_invoice.refresh_from_db()

        self.assertEqual(agency_payment.matched_amount, test_amount)
        self.assertEqual(agency_invoice.matched_amount, test_amount)

        agency_invoice.amount = agency_invoice.amount + 20

        agency_invoice = FinanceService.save_agency_invoice(
            user=self.test_user,
            agency_invoice=agency_invoice)

        self.assertEqual(agency_invoice.matched_amount, test_amount)

    def test_agency_match_then_change_status(self):
        """
        Does match between agency_payment and agency_invoice then change status
        """
        test_account = Account.objects.create(
            name='Test Account',
            currency=CURRENCY_CUC,
            balance=1000)

        test_agency = Agency.objects.create(
            name='Test Agency')

        test_date = timezone.now()
        test_amount = 100
        test_status = STATUS_READY

        agency_payment = AgencyPayment(
            date=test_date,
            account=test_account,
            amount=test_amount,
            agency=test_agency,
            status=test_status)

        agency_payment = FinanceService.save_agency_payment(
            user=self.test_user,
            agency_payment=agency_payment)

        agency_invoice = AgencyInvoice(
            date=test_date,
            amount=test_amount,
            agency=test_agency,
            status=test_status)

        agency_invoice = FinanceService.save_agency_invoice(
            user=self.test_user,
            agency_invoice=agency_invoice)

        agency_match = AgencyDocumentMatch(
            credit_document=agency_payment,
            debit_document=agency_invoice,
            matched_amount=test_amount)

        agency_match = FinanceService.save_agency_match(agency_match)

        agency_payment.refresh_from_db()
        agency_invoice.refresh_from_db()

        self.assertEqual(agency_payment.matched_amount, test_amount)
        self.assertEqual(agency_invoice.matched_amount, test_amount)

        agency_invoice.status = STATUS_DRAFT

        with self.assertRaisesMessage(ValidationError, ERROR_MATCH_STATUS):
            agency_invoice = FinanceService.save_agency_invoice(
                user=self.test_user,
                agency_invoice=agency_invoice)

    def test_agency_match_then_decrease_amount(self):
        """
        Does match between agency_payment and agency_invoice then decrease amount
        """
        test_account = Account.objects.create(
            name='Test Account',
            currency=CURRENCY_CUC,
            balance=1000)

        test_agency = Agency.objects.create(
            name='Test Agency')

        test_date = timezone.now()
        test_amount = 100
        test_status = STATUS_READY

        agency_payment = AgencyPayment(
            date=test_date,
            account=test_account,
            amount=test_amount,
            agency=test_agency,
            status=test_status)

        agency_payment = FinanceService.save_agency_payment(
            user=self.test_user,
            agency_payment=agency_payment)

        agency_invoice = AgencyInvoice(
            date=test_date,
            amount=test_amount,
            agency=test_agency,
            status=test_status)

        agency_invoice = FinanceService.save_agency_invoice(
            user=self.test_user,
            agency_invoice=agency_invoice)

        agency_match = AgencyDocumentMatch(
            credit_document=agency_payment,
            debit_document=agency_invoice,
            matched_amount=test_amount)

        agency_match = FinanceService.save_agency_match(agency_match)

        agency_payment.refresh_from_db()
        agency_invoice.refresh_from_db()

        self.assertEqual(agency_payment.matched_amount, test_amount)
        self.assertEqual(agency_invoice.matched_amount, test_amount)

        agency_invoice.amount = agency_invoice.amount - 20

        with self.assertRaisesMessage(ValidationError, ERROR_MATCH_AMOUNT):
            agency_invoice = FinanceService.save_agency_invoice(
                user=self.test_user,
                agency_invoice=agency_invoice)

    def test_agency_match_then_change_agency(self):
        """
        Does match between agency_payment and agency_invoice then change agency
        """
        test_account = Account.objects.create(
            name='Test Account',
            currency=CURRENCY_CUC,
            balance=1000)

        test_agency1 = Agency.objects.create(
            name='Test Agency1')

        test_date = timezone.now()
        test_amount = 100
        test_status = STATUS_READY

        agency_payment = AgencyPayment(
            date=test_date,
            account=test_account,
            amount=test_amount,
            agency=test_agency1,
            status=test_status)

        agency_payment = FinanceService.save_agency_payment(
            user=self.test_user,
            agency_payment=agency_payment)

        agency_invoice = AgencyInvoice(
            date=test_date,
            amount=test_amount,
            agency=test_agency1,
            status=test_status)

        agency_invoice = FinanceService.save_agency_invoice(
            user=self.test_user,
            agency_invoice=agency_invoice)

        agency_match = AgencyDocumentMatch(
            credit_document=agency_payment,
            debit_document=agency_invoice,
            matched_amount=test_amount)

        agency_match = FinanceService.save_agency_match(agency_match)

        agency_payment.refresh_from_db()
        agency_invoice.refresh_from_db()

        self.assertEqual(agency_payment.matched_amount, test_amount)
        self.assertEqual(agency_invoice.matched_amount, test_amount)

        test_agency2 = Agency.objects.create(
            name='Test Agency2')

        agency_invoice.agency = test_agency2

        with self.assertRaisesMessage(ValidationError, ERROR_MATCH_AGENCY):
            agency_invoice = FinanceService.save_agency_invoice(
                user=self.test_user,
                agency_invoice=agency_invoice)
