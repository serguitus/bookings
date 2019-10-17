from datetime import timedelta

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone

from accounting.constants import (
    CURRENCY_CUC, CURRENCY_USD)

from finance.constants import STATUS_DRAFT, STATUS_READY, DOC_TYPE_AGENCY_INVOICE
from finance.models import Agency, AgencyInvoice
from finance.services import FinanceServices
from finance.tests.utils import FinanceBaseTestCase


class FinanceServicesTestCase(FinanceBaseTestCase):

    test_user = None
    test_agency = None

    def setUp(self):
        self.test_user = User.objects.create(
            username="Test User")
        self.test_agency = Agency.objects.create(
            name="Test Agency",
            currency=CURRENCY_CUC)

    def test_save_agency_invoice_status_draft(self):
        """
        Does draft agency_invoice
        """
        test_currency = CURRENCY_CUC
        test_date = timezone.now()
        test_amount = 100
        test_status = STATUS_DRAFT

        agency_invoice = AgencyInvoice(
            agency=self.test_agency,
            date=test_date,
            currency=test_currency,
            amount=test_amount,
            status=test_status)

        agency_invoice = FinanceServices.save_agency_invoice(
            user=self.test_user,
            agency_invoice=agency_invoice)

        # document data auto filled
        self.assertDocument(agency_invoice, DOC_TYPE_AGENCY_INVOICE, test_currency)

        # one finantial history created
        finantials = agency_invoice.finantialdocumenthistory_set
        self.assertEqual(finantials.count(), 1)

        # finantial history info
        finantial = finantials.first()
        self.assertFinantialHistory(
            test_finantial_history=finantial, test_document=agency_invoice, test_user=self.test_user,
            test_old_status=None, test_new_status=test_status)

    def test_save_agency_invoice_status_ready(self):
        """
        Does ready agency_invoice
        """
        test_currency = CURRENCY_CUC
        test_date = timezone.now()
        test_amount = 100
        test_status = STATUS_READY

        agency_invoice = AgencyInvoice(
            agency=self.test_agency,
            date=test_date,
            currency=test_currency,
            amount=test_amount,
            status=test_status)

        agency_invoice = FinanceServices.save_agency_invoice(
            user=self.test_user,
            agency_invoice=agency_invoice)

        # document data auto filled
        self.assertDocument(agency_invoice, DOC_TYPE_AGENCY_INVOICE, test_currency)

        # one finantial history created
        finantials = agency_invoice.finantialdocumenthistory_set
        self.assertEqual(finantials.count(), 1)

        # finantial history info
        finantial = finantials.first()
        self.assertFinantialHistory(
            test_finantial_history=finantial, test_document=agency_invoice, test_user=self.test_user,
            test_old_status=None, test_new_status=test_status)

    def test_save_agency_invoice_draft_then_ready(self):
        """
        Does draft agency_invoice and then change to ready
        """
        test_currency = CURRENCY_CUC
        test_date = timezone.now()
        test_amount = 100
        test_status1 = STATUS_DRAFT

        agency_invoice = AgencyInvoice(
            agency=self.test_agency,
            date=test_date,
            currency=test_currency,
            amount=test_amount,
            status=test_status1)

        agency_invoice = FinanceServices.save_agency_invoice(
            user=self.test_user,
            agency_invoice=agency_invoice)

        # document data auto filled
        self.assertDocument(agency_invoice, DOC_TYPE_AGENCY_INVOICE, test_currency)

        # one finantial history created
        finantials = agency_invoice.finantialdocumenthistory_set
        self.assertEqual(finantials.count(), 1)

        # finantial history info
        finantial = finantials.first()
        self.assertFinantialHistory(
            test_finantial_history=finantial, test_document=agency_invoice, test_user=self.test_user,
            test_old_status=None, test_new_status=test_status1)

        test_status2 = STATUS_READY

        agency_invoice.status = test_status2

        agency_invoice = FinanceServices.save_agency_invoice(
            user=self.test_user,
            agency_invoice=agency_invoice)

        # document data auto filled
        self.assertDocument(agency_invoice, DOC_TYPE_AGENCY_INVOICE, test_currency)

        # now two finantial history created
        finantials = agency_invoice.finantialdocumenthistory_set
        self.assertEqual(finantials.count(), 2)

        # new finantial history info
        finantial = finantials.last()
        self.assertFinantialHistory(
            test_finantial_history=finantial, test_document=agency_invoice, test_user=self.test_user,
            test_old_status=test_status1, test_new_status=test_status2)

    def test_save_agency_invoice_ready_then_draft(self):
        """
        Does ready agency_invoice and then change to draft
        """
        test_currency = CURRENCY_CUC
        test_date = timezone.now()
        test_amount = 100
        test_status1 = STATUS_READY

        agency_invoice = AgencyInvoice(
            agency=self.test_agency,
            date=test_date,
            currency=test_currency,
            amount=test_amount,
            status=test_status1)

        agency_invoice = FinanceServices.save_agency_invoice(
            user=self.test_user,
            agency_invoice=agency_invoice)

        # document data auto filled
        self.assertDocument(agency_invoice, DOC_TYPE_AGENCY_INVOICE, test_currency)

        # one finantial history created
        finantials = agency_invoice.finantialdocumenthistory_set
        self.assertEqual(finantials.count(), 1)

        # finantial history info
        finantial = finantials.first()
        self.assertFinantialHistory(
            test_finantial_history=finantial, test_document=agency_invoice, test_user=self.test_user,
            test_old_status=None, test_new_status=test_status1)

        test_status2 = STATUS_DRAFT

        agency_invoice.status = test_status2

        agency_invoice = FinanceServices.save_agency_invoice(
            user=self.test_user,
            agency_invoice=agency_invoice)

        # document data auto filled
        self.assertDocument(agency_invoice, DOC_TYPE_AGENCY_INVOICE, test_currency)

        # now two finantial history created
        finantials = agency_invoice.finantialdocumenthistory_set
        self.assertEqual(finantials.count(), 2)

        # new finantial history info
        finantial = finantials.last()
        self.assertFinantialHistory(
            test_finantial_history=finantial, test_document=agency_invoice, test_user=self.test_user,
            test_old_status=test_status1, test_new_status=test_status2)

    def test_save_agency_invoice_ready_then_draft_currency(self):
        """
        Does ready agency_invoice and then change to draft and currency
        """
        test_currency1 = CURRENCY_CUC
        test_date = timezone.now()
        test_amount = 100
        test_status1 = STATUS_READY

        agency_invoice = AgencyInvoice(
            agency=self.test_agency,
            date=test_date,
            currency=test_currency1,
            amount=test_amount,
            status=test_status1)

        agency_invoice = FinanceServices.save_agency_invoice(
            user=self.test_user,
            agency_invoice=agency_invoice)

        # document data auto filled
        self.assertDocument(agency_invoice, DOC_TYPE_AGENCY_INVOICE, test_currency1)

        # one finantial history created
        finantials = agency_invoice.finantialdocumenthistory_set
        self.assertEqual(finantials.count(), 1)

        # finantial history info
        finantial = finantials.first()
        self.assertFinantialHistory(
            test_finantial_history=finantial, test_document=agency_invoice, test_user=self.test_user,
            test_old_status=None, test_new_status=test_status1)

        test_status2 = STATUS_DRAFT
        test_currency2 = CURRENCY_USD

        agency_invoice.status = test_status2
        agency_invoice.currency = test_currency2

        agency_invoice = FinanceServices.save_agency_invoice(
            user=self.test_user,
            agency_invoice=agency_invoice)

        # document data auto filled
        self.assertDocument(agency_invoice, DOC_TYPE_AGENCY_INVOICE, test_currency2)

        # now two finantial history created
        finantials = agency_invoice.finantialdocumenthistory_set
        self.assertEqual(finantials.count(), 2)

        # new finantial history info
        finantial = finantials.last()
        self.assertFinantialHistory(
            test_finantial_history=finantial, test_document=agency_invoice, test_user=self.test_user,
            test_old_status=test_status1, test_new_status=test_status2)

    def test_save_agency_invoice_draft_then_amount(self):
        """
        Does draft agency_invoice and then change amount
        """
        test_currency = CURRENCY_CUC
        test_date = timezone.now()
        test_amount1 = 100
        test_status = STATUS_DRAFT

        agency_invoice = AgencyInvoice(
            agency=self.test_agency,
            date=test_date,
            currency=test_currency,
            amount=test_amount1,
            status=test_status)

        agency_invoice = FinanceServices.save_agency_invoice(
            user=self.test_user,
            agency_invoice=agency_invoice)

        # document data auto filled
        self.assertDocument(agency_invoice, DOC_TYPE_AGENCY_INVOICE, test_currency)

        # one finantial history created
        finantials = agency_invoice.finantialdocumenthistory_set
        self.assertEqual(finantials.count(), 1)

        # finantial history info
        finantial = finantials.first()
        self.assertFinantialHistory(
            test_finantial_history=finantial, test_document=agency_invoice, test_user=self.test_user,
            test_old_status=None, test_new_status=test_status)

        test_amount2 = 50

        agency_invoice.amount = test_amount2

        agency_invoice = FinanceServices.save_agency_invoice(
            user=self.test_user,
            agency_invoice=agency_invoice)

        # document data auto filled
        self.assertDocument(agency_invoice, DOC_TYPE_AGENCY_INVOICE, test_currency)

        # no aditional finantial history
        finantials = agency_invoice.finantialdocumenthistory_set
        self.assertEqual(finantials.count(), 1)

    def test_save_agency_invoice_ready_then_amount(self):
        """
        Does ready agency_invoice and then change amount
        """
        test_currency = CURRENCY_CUC
        test_date = timezone.now()
        test_amount1 = 100
        test_status = STATUS_READY

        agency_invoice = AgencyInvoice(
            agency=self.test_agency,
            date=test_date,
            currency=test_currency,
            amount=test_amount1,
            status=test_status)

        agency_invoice = FinanceServices.save_agency_invoice(
            user=self.test_user,
            agency_invoice=agency_invoice)

        # document data auto filled
        self.assertDocument(agency_invoice, DOC_TYPE_AGENCY_INVOICE, test_currency)

        # one finantial history created
        finantials = agency_invoice.finantialdocumenthistory_set
        self.assertEqual(finantials.count(), 1)

        # finantial history info
        finantial = finantials.first()
        self.assertFinantialHistory(
            test_finantial_history=finantial, test_document=agency_invoice, test_user=self.test_user,
            test_old_status=None, test_new_status=test_status)

        test_amount2 = 50

        agency_invoice.amount = test_amount2

        agency_invoice = FinanceServices.save_agency_invoice(
            user=self.test_user,
            agency_invoice=agency_invoice)

        # document data auto filled
        self.assertDocument(agency_invoice, DOC_TYPE_AGENCY_INVOICE, test_currency)

        # no aditional finantial history
        finantials = agency_invoice.finantialdocumenthistory_set
        self.assertEqual(finantials.count(), 1)

    def test_save_agency_invoice_draft_then_currency(self):
        """
        Does draft agency_invoice and then change currency
        """
        test_currency1 = CURRENCY_CUC
        test_date = timezone.now()
        test_amount = 100
        test_status = STATUS_DRAFT

        agency_invoice = AgencyInvoice(
            agency=self.test_agency,
            date=test_date,
            currency=test_currency1,
            amount=test_amount,
            status=test_status)

        agency_invoice = FinanceServices.save_agency_invoice(
            user=self.test_user,
            agency_invoice=agency_invoice)

        # document data auto filled
        self.assertDocument(agency_invoice, DOC_TYPE_AGENCY_INVOICE, test_currency1)

        # one finantial history created
        finantials = agency_invoice.finantialdocumenthistory_set
        self.assertEqual(finantials.count(), 1)

        # finantial history info
        finantial = finantials.first()
        self.assertFinantialHistory(
            test_finantial_history=finantial, test_document=agency_invoice, test_user=self.test_user,
            test_old_status=None, test_new_status=test_status)

        test_currency2 = CURRENCY_USD

        agency_invoice.currency = test_currency2

        agency_invoice = FinanceServices.save_agency_invoice(
            user=self.test_user,
            agency_invoice=agency_invoice)

        # document data auto filled
        self.assertDocument(agency_invoice, DOC_TYPE_AGENCY_INVOICE, test_currency2)

        # no aditional finantial history
        finantials = agency_invoice.finantialdocumenthistory_set
        self.assertEqual(finantials.count(), 1)

    def test_save_agency_invoice_ready_then_currency(self):
        """
        Does ready agency_invoice and then change currency
        """
        test_currency1 = CURRENCY_CUC
        test_date = timezone.now()
        test_amount = 100
        test_status = STATUS_READY

        agency_invoice = AgencyInvoice(
            agency=self.test_agency,
            date=test_date,
            currency=test_currency1,
            amount=test_amount,
            status=test_status)

        agency_invoice = FinanceServices.save_agency_invoice(
            user=self.test_user,
            agency_invoice=agency_invoice)

        # document data auto filled
        self.assertDocument(agency_invoice, DOC_TYPE_AGENCY_INVOICE, test_currency1)

        # one finantial history created
        finantials = agency_invoice.finantialdocumenthistory_set
        self.assertEqual(finantials.count(), 1)

        # finantial history info
        finantial = finantials.first()
        self.assertFinantialHistory(
            test_finantial_history=finantial, test_document=agency_invoice, test_user=self.test_user,
            test_old_status=None, test_new_status=test_status)

        test_currency2 = CURRENCY_USD

        agency_invoice.currency = test_currency2

        agency_invoice = FinanceServices.save_agency_invoice(
            user=self.test_user,
            agency_invoice=agency_invoice)

        # document data auto filled
        self.assertDocument(agency_invoice, DOC_TYPE_AGENCY_INVOICE, test_currency2)

        # no aditional finantial history
        finantials = agency_invoice.finantialdocumenthistory_set
        self.assertEqual(finantials.count(), 1)

    def test_save_agency_invoice_ready_then_amount_currency(self):
        """
        Does ready agency_invoice and then change amount and currency
        """
        test_currency1 = CURRENCY_CUC
        test_date = timezone.now()
        test_amount1 = 100
        test_status = STATUS_READY

        agency_invoice = AgencyInvoice(
            agency=self.test_agency,
            date=test_date,
            currency=test_currency1,
            amount=test_amount1,
            status=test_status)

        agency_invoice = FinanceServices.save_agency_invoice(
            user=self.test_user,
            agency_invoice=agency_invoice)

        # document data auto filled
        self.assertDocument(agency_invoice, DOC_TYPE_AGENCY_INVOICE, test_currency1)

        # one finantial history created
        finantials = agency_invoice.finantialdocumenthistory_set
        self.assertEqual(finantials.count(), 1)

        # finantial history info
        finantial = finantials.first()
        self.assertFinantialHistory(
            test_finantial_history=finantial, test_document=agency_invoice, test_user=self.test_user,
            test_old_status=None, test_new_status=test_status)

        test_currency2 = CURRENCY_USD
        test_amount2 = 50

        agency_invoice.currency = test_currency2
        agency_invoice.amount = test_amount2

        agency_invoice = FinanceServices.save_agency_invoice(
            user=self.test_user,
            agency_invoice=agency_invoice)

        # document data auto filled
        self.assertDocument(agency_invoice, DOC_TYPE_AGENCY_INVOICE, test_currency2)

        # no aditional finantial history
        finantials = agency_invoice.finantialdocumenthistory_set
        self.assertEqual(finantials.count(), 1)

    def test_save_agency_invoice_draft_then_date(self):
        """
        Does draft agency_invoice and then change date
        """
        test_currency = CURRENCY_CUC
        test_date1 = timezone.now()
        test_amount = 100
        test_status = STATUS_DRAFT

        agency_invoice = AgencyInvoice(
            agency=self.test_agency,
            date=test_date1,
            currency=test_currency,
            amount=test_amount,
            status=test_status)

        agency_invoice = FinanceServices.save_agency_invoice(
            user=self.test_user,
            agency_invoice=agency_invoice)

        test_name1 = agency_invoice.name

        # document data auto filled
        self.assertDocument(agency_invoice, DOC_TYPE_AGENCY_INVOICE, test_currency)

        # one finantial history created
        finantials = agency_invoice.finantialdocumenthistory_set
        self.assertEqual(finantials.count(), 1)

        # finantial history info
        finantial = finantials.first()
        self.assertFinantialHistory(
            test_finantial_history=finantial, test_document=agency_invoice, test_user=self.test_user,
            test_old_status=None, test_new_status=test_status)

        test_date2 = test_date1 - timedelta(days=5)

        agency_invoice.date = test_date2

        agency_invoice = FinanceServices.save_agency_invoice(
            user=self.test_user,
            agency_invoice=agency_invoice)

        test_name2 = agency_invoice.name

        # name changed
        self.assertNotEqual(test_name1, test_name2)

        # document data auto filled
        self.assertDocument(agency_invoice, DOC_TYPE_AGENCY_INVOICE, test_currency)

        # no finantial history created
        finantials = agency_invoice.finantialdocumenthistory_set
        self.assertEqual(finantials.count(), 1)

    def test_save_agency_invoice_ready_then_date(self):
        """
        Does ready agency_invoice and then change to draft
        """
        test_currency = CURRENCY_CUC
        test_date1 = timezone.now()
        test_amount = 100
        test_status = STATUS_READY

        agency_invoice = AgencyInvoice(
            agency=self.test_agency,
            date=test_date1,
            currency=test_currency,
            amount=test_amount,
            status=test_status)

        agency_invoice = FinanceServices.save_agency_invoice(
            user=self.test_user,
            agency_invoice=agency_invoice)

        test_name1 = agency_invoice.name

        # document data auto filled
        self.assertDocument(agency_invoice, DOC_TYPE_AGENCY_INVOICE, test_currency)

        # one finantial history created
        finantials = agency_invoice.finantialdocumenthistory_set
        self.assertEqual(finantials.count(), 1)

        # finantial history info
        finantial = finantials.first()
        self.assertFinantialHistory(
            test_finantial_history=finantial, test_document=agency_invoice, test_user=self.test_user,
            test_old_status=None, test_new_status=test_status)

        test_date2 = test_date1 - timedelta(days=5)

        agency_invoice.date = test_date2

        agency_invoice = FinanceServices.save_agency_invoice(
            user=self.test_user,
            agency_invoice=agency_invoice)

        test_name2 = agency_invoice.name

        # name changed
        self.assertNotEqual(test_name1, test_name2)

        # document data auto filled
        self.assertDocument(agency_invoice, DOC_TYPE_AGENCY_INVOICE, test_currency)

        # same finantial history
        finantials = agency_invoice.finantialdocumenthistory_set
        self.assertEqual(finantials.count(), 1)
