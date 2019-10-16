from datetime import timedelta

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone

from accounting.constants import (
    CURRENCY_CUC, CURRENCY_USD)

from finance.constants import STATUS_DRAFT, STATUS_READY, DOC_TYPE_PROVIDER_INVOICE
from finance.models import Provider, ProviderInvoice
from finance.services import FinanceServices
from finance.tests.utils import FinanceBaseTestCase


class FinanceServicesTestCase(FinanceBaseTestCase):

    test_user = None
    test_provider = None

    def setUp(self):
        self.test_user = User.objects.create(
            username="Test User")
        self.test_provider = Provider.objects.create(
            name="Test Provider",
            currency=CURRENCY_CUC)

    def test_save_provider_invoice_status_draft(self):
        """
        Does draft provider_invoice
        """
        test_currency = CURRENCY_CUC
        test_date = timezone.now()
        test_amount = 100
        test_status = STATUS_DRAFT

        provider_invoice = ProviderInvoice(
            provider=self.test_provider,
            date=test_date,
            currency=test_currency,
            amount=test_amount,
            status=test_status)

        provider_invoice = FinanceServices.save_provider_invoice(
            user=self.test_user,
            provider_invoice=provider_invoice)

        # document data auto filled
        self.assertDocument(provider_invoice, DOC_TYPE_PROVIDER_INVOICE, test_currency)

        # one finantial history created
        finantials = provider_invoice.finantialdocumenthistory_set
        self.assertEqual(finantials.count(), 1)

        # finantial history info
        finantial = finantials.first()
        self.assertFinantialHistory(
            test_finantial_history=finantial, test_document=provider_invoice, test_user=self.test_user,
            test_old_status=None, test_new_status=test_status)

    def test_save_provider_invoice_status_ready(self):
        """
        Does ready provider_invoice
        """
        test_currency = CURRENCY_CUC
        test_date = timezone.now()
        test_amount = 100
        test_status = STATUS_READY

        provider_invoice = ProviderInvoice(
            provider=self.test_provider,
            date=test_date,
            currency=test_currency,
            amount=test_amount,
            status=test_status)

        provider_invoice = FinanceServices.save_provider_invoice(
            user=self.test_user,
            provider_invoice=provider_invoice)

        # document data auto filled
        self.assertDocument(provider_invoice, DOC_TYPE_PROVIDER_INVOICE, test_currency)

        # one finantial history created
        finantials = provider_invoice.finantialdocumenthistory_set
        self.assertEqual(finantials.count(), 1)

        # finantial history info
        finantial = finantials.first()
        self.assertFinantialHistory(
            test_finantial_history=finantial, test_document=provider_invoice, test_user=self.test_user,
            test_old_status=None, test_new_status=test_status)

    def test_save_provider_invoice_draft_then_ready(self):
        """
        Does draft provider_invoice and then change to ready
        """
        test_currency = CURRENCY_CUC
        test_date = timezone.now()
        test_amount = 100
        test_status1 = STATUS_DRAFT

        provider_invoice = ProviderInvoice(
            provider=self.test_provider,
            date=test_date,
            currency=test_currency,
            amount=test_amount,
            status=test_status1)

        provider_invoice = FinanceServices.save_provider_invoice(
            user=self.test_user,
            provider_invoice=provider_invoice)

        # document data auto filled
        self.assertDocument(provider_invoice, DOC_TYPE_PROVIDER_INVOICE, test_currency)

        # one finantial history created
        finantials = provider_invoice.finantialdocumenthistory_set
        self.assertEqual(finantials.count(), 1)

        # finantial history info
        finantial = finantials.first()
        self.assertFinantialHistory(
            test_finantial_history=finantial, test_document=provider_invoice, test_user=self.test_user,
            test_old_status=None, test_new_status=test_status1)

        test_status2 = STATUS_READY

        provider_invoice.status = test_status2

        provider_invoice = FinanceServices.save_provider_invoice(
            user=self.test_user,
            provider_invoice=provider_invoice)

        # document data auto filled
        self.assertDocument(provider_invoice, DOC_TYPE_PROVIDER_INVOICE, test_currency)

        # now two finantial history created
        finantials = provider_invoice.finantialdocumenthistory_set
        self.assertEqual(finantials.count(), 2)

        # new finantial history info
        finantial = finantials.last()
        self.assertFinantialHistory(
            test_finantial_history=finantial, test_document=provider_invoice, test_user=self.test_user,
            test_old_status=test_status1, test_new_status=test_status2)

    def test_save_provider_invoice_ready_then_draft(self):
        """
        Does ready provider_invoice and then change to draft
        """
        test_currency = CURRENCY_CUC
        test_date = timezone.now()
        test_amount = 100
        test_status1 = STATUS_READY

        provider_invoice = ProviderInvoice(
            provider=self.test_provider,
            date=test_date,
            currency=test_currency,
            amount=test_amount,
            status=test_status1)

        provider_invoice = FinanceServices.save_provider_invoice(
            user=self.test_user,
            provider_invoice=provider_invoice)

        # document data auto filled
        self.assertDocument(provider_invoice, DOC_TYPE_PROVIDER_INVOICE, test_currency)

        # one finantial history created
        finantials = provider_invoice.finantialdocumenthistory_set
        self.assertEqual(finantials.count(), 1)

        # finantial history info
        finantial = finantials.first()
        self.assertFinantialHistory(
            test_finantial_history=finantial, test_document=provider_invoice, test_user=self.test_user,
            test_old_status=None, test_new_status=test_status1)

        test_status2 = STATUS_DRAFT

        provider_invoice.status = test_status2

        provider_invoice = FinanceServices.save_provider_invoice(
            user=self.test_user,
            provider_invoice=provider_invoice)

        # document data auto filled
        self.assertDocument(provider_invoice, DOC_TYPE_PROVIDER_INVOICE, test_currency)

        # now two finantial history created
        finantials = provider_invoice.finantialdocumenthistory_set
        self.assertEqual(finantials.count(), 2)

        # new finantial history info
        finantial = finantials.last()
        self.assertFinantialHistory(
            test_finantial_history=finantial, test_document=provider_invoice, test_user=self.test_user,
            test_old_status=test_status1, test_new_status=test_status2)

    def test_save_provider_invoice_ready_then_draft_currency(self):
        """
        Does ready provider_invoice and then change to draft and currency
        """
        test_currency1 = CURRENCY_CUC
        test_date = timezone.now()
        test_amount = 100
        test_status1 = STATUS_READY

        provider_invoice = ProviderInvoice(
            provider=self.test_provider,
            date=test_date,
            currency=test_currency1,
            amount=test_amount,
            status=test_status1)

        provider_invoice = FinanceServices.save_provider_invoice(
            user=self.test_user,
            provider_invoice=provider_invoice)

        # document data auto filled
        self.assertDocument(provider_invoice, DOC_TYPE_PROVIDER_INVOICE, test_currency1)

        # one finantial history created
        finantials = provider_invoice.finantialdocumenthistory_set
        self.assertEqual(finantials.count(), 1)

        # finantial history info
        finantial = finantials.first()
        self.assertFinantialHistory(
            test_finantial_history=finantial, test_document=provider_invoice, test_user=self.test_user,
            test_old_status=None, test_new_status=test_status1)

        test_status2 = STATUS_DRAFT
        test_currency2 = CURRENCY_USD

        provider_invoice.status = test_status2
        provider_invoice.currency = test_currency2

        provider_invoice = FinanceServices.save_provider_invoice(
            user=self.test_user,
            provider_invoice=provider_invoice)

        # document data auto filled
        self.assertDocument(provider_invoice, DOC_TYPE_PROVIDER_INVOICE, test_currency2)

        # now two finantial history created
        finantials = provider_invoice.finantialdocumenthistory_set
        self.assertEqual(finantials.count(), 2)

        # new finantial history info
        finantial = finantials.last()
        self.assertFinantialHistory(
            test_finantial_history=finantial, test_document=provider_invoice, test_user=self.test_user,
            test_old_status=test_status1, test_new_status=test_status2)

    def test_save_provider_invoice_draft_then_amount(self):
        """
        Does draft provider_invoice and then change amount
        """
        test_currency = CURRENCY_CUC
        test_date = timezone.now()
        test_amount1 = 100
        test_status = STATUS_DRAFT

        provider_invoice = ProviderInvoice(
            provider=self.test_provider,
            date=test_date,
            currency=test_currency,
            amount=test_amount1,
            status=test_status)

        provider_invoice = FinanceServices.save_provider_invoice(
            user=self.test_user,
            provider_invoice=provider_invoice)

        # document data auto filled
        self.assertDocument(provider_invoice, DOC_TYPE_PROVIDER_INVOICE, test_currency)

        # one finantial history created
        finantials = provider_invoice.finantialdocumenthistory_set
        self.assertEqual(finantials.count(), 1)

        # finantial history info
        finantial = finantials.first()
        self.assertFinantialHistory(
            test_finantial_history=finantial, test_document=provider_invoice, test_user=self.test_user,
            test_old_status=None, test_new_status=test_status)

        test_amount2 = 50

        provider_invoice.amount = test_amount2

        provider_invoice = FinanceServices.save_provider_invoice(
            user=self.test_user,
            provider_invoice=provider_invoice)

        # document data auto filled
        self.assertDocument(provider_invoice, DOC_TYPE_PROVIDER_INVOICE, test_currency)

        # no aditional finantial history
        finantials = provider_invoice.finantialdocumenthistory_set
        self.assertEqual(finantials.count(), 1)

    def test_save_provider_invoice_ready_then_amount(self):
        """
        Does ready provider_invoice and then change amount
        """
        test_currency = CURRENCY_CUC
        test_date = timezone.now()
        test_amount1 = 100
        test_status = STATUS_READY

        provider_invoice = ProviderInvoice(
            provider=self.test_provider,
            date=test_date,
            currency=test_currency,
            amount=test_amount1,
            status=test_status)

        provider_invoice = FinanceServices.save_provider_invoice(
            user=self.test_user,
            provider_invoice=provider_invoice)

        # document data auto filled
        self.assertDocument(provider_invoice, DOC_TYPE_PROVIDER_INVOICE, test_currency)

        # one finantial history created
        finantials = provider_invoice.finantialdocumenthistory_set
        self.assertEqual(finantials.count(), 1)

        # finantial history info
        finantial = finantials.first()
        self.assertFinantialHistory(
            test_finantial_history=finantial, test_document=provider_invoice, test_user=self.test_user,
            test_old_status=None, test_new_status=test_status)

        test_amount2 = 50

        provider_invoice.amount = test_amount2

        provider_invoice = FinanceServices.save_provider_invoice(
            user=self.test_user,
            provider_invoice=provider_invoice)

        # document data auto filled
        self.assertDocument(provider_invoice, DOC_TYPE_PROVIDER_INVOICE, test_currency)

        # no aditional finantial history
        finantials = provider_invoice.finantialdocumenthistory_set
        self.assertEqual(finantials.count(), 1)

    def test_save_provider_invoice_draft_then_currency(self):
        """
        Does draft provider_invoice and then change currency
        """
        test_currency1 = CURRENCY_CUC
        test_date = timezone.now()
        test_amount = 100
        test_status = STATUS_DRAFT

        provider_invoice = ProviderInvoice(
            provider=self.test_provider,
            date=test_date,
            currency=test_currency1,
            amount=test_amount,
            status=test_status)

        provider_invoice = FinanceServices.save_provider_invoice(
            user=self.test_user,
            provider_invoice=provider_invoice)

        # document data auto filled
        self.assertDocument(provider_invoice, DOC_TYPE_PROVIDER_INVOICE, test_currency1)

        # one finantial history created
        finantials = provider_invoice.finantialdocumenthistory_set
        self.assertEqual(finantials.count(), 1)

        # finantial history info
        finantial = finantials.first()
        self.assertFinantialHistory(
            test_finantial_history=finantial, test_document=provider_invoice, test_user=self.test_user,
            test_old_status=None, test_new_status=test_status)

        test_currency2 = CURRENCY_USD

        provider_invoice.currency = test_currency2

        provider_invoice = FinanceServices.save_provider_invoice(
            user=self.test_user,
            provider_invoice=provider_invoice)

        # document data auto filled
        self.assertDocument(provider_invoice, DOC_TYPE_PROVIDER_INVOICE, test_currency2)

        # no aditional finantial history
        finantials = provider_invoice.finantialdocumenthistory_set
        self.assertEqual(finantials.count(), 1)

    def test_save_provider_invoice_ready_then_currency(self):
        """
        Does ready provider_invoice and then change currency
        """
        test_currency1 = CURRENCY_CUC
        test_date = timezone.now()
        test_amount = 100
        test_status = STATUS_READY

        provider_invoice = ProviderInvoice(
            provider=self.test_provider,
            date=test_date,
            currency=test_currency1,
            amount=test_amount,
            status=test_status)

        provider_invoice = FinanceServices.save_provider_invoice(
            user=self.test_user,
            provider_invoice=provider_invoice)

        # document data auto filled
        self.assertDocument(provider_invoice, DOC_TYPE_PROVIDER_INVOICE, test_currency1)

        # one finantial history created
        finantials = provider_invoice.finantialdocumenthistory_set
        self.assertEqual(finantials.count(), 1)

        # finantial history info
        finantial = finantials.first()
        self.assertFinantialHistory(
            test_finantial_history=finantial, test_document=provider_invoice, test_user=self.test_user,
            test_old_status=None, test_new_status=test_status)

        test_currency2 = CURRENCY_USD

        provider_invoice.currency = test_currency2

        provider_invoice = FinanceServices.save_provider_invoice(
            user=self.test_user,
            provider_invoice=provider_invoice)

        # document data auto filled
        self.assertDocument(provider_invoice, DOC_TYPE_PROVIDER_INVOICE, test_currency2)

        # no aditional finantial history
        finantials = provider_invoice.finantialdocumenthistory_set
        self.assertEqual(finantials.count(), 1)

    def test_save_provider_invoice_ready_then_amount_currency(self):
        """
        Does ready provider_invoice and then change amount and currency
        """
        test_currency1 = CURRENCY_CUC
        test_date = timezone.now()
        test_amount1 = 100
        test_status = STATUS_READY

        provider_invoice = ProviderInvoice(
            provider=self.test_provider,
            date=test_date,
            currency=test_currency1,
            amount=test_amount1,
            status=test_status)

        provider_invoice = FinanceServices.save_provider_invoice(
            user=self.test_user,
            provider_invoice=provider_invoice)

        # document data auto filled
        self.assertDocument(provider_invoice, DOC_TYPE_PROVIDER_INVOICE, test_currency1)

        # one finantial history created
        finantials = provider_invoice.finantialdocumenthistory_set
        self.assertEqual(finantials.count(), 1)

        # finantial history info
        finantial = finantials.first()
        self.assertFinantialHistory(
            test_finantial_history=finantial, test_document=provider_invoice, test_user=self.test_user,
            test_old_status=None, test_new_status=test_status)

        test_currency2 = CURRENCY_USD
        test_amount2 = 50

        provider_invoice.currency = test_currency2
        provider_invoice.amount = test_amount2

        provider_invoice = FinanceServices.save_provider_invoice(
            user=self.test_user,
            provider_invoice=provider_invoice)

        # document data auto filled
        self.assertDocument(provider_invoice, DOC_TYPE_PROVIDER_INVOICE, test_currency2)

        # no aditional finantial history
        finantials = provider_invoice.finantialdocumenthistory_set
        self.assertEqual(finantials.count(), 1)

    def test_save_provider_invoice_draft_then_date(self):
        """
        Does draft provider_invoice and then change date
        """
        test_currency = CURRENCY_CUC
        test_date1 = timezone.now()
        test_amount = 100
        test_status = STATUS_DRAFT

        provider_invoice = ProviderInvoice(
            provider=self.test_provider,
            date=test_date1,
            currency=test_currency,
            amount=test_amount,
            status=test_status)

        provider_invoice = FinanceServices.save_provider_invoice(
            user=self.test_user,
            provider_invoice=provider_invoice)

        test_name1 = provider_invoice.name

        # document data auto filled
        self.assertDocument(provider_invoice, DOC_TYPE_PROVIDER_INVOICE, test_currency)

        # one finantial history created
        finantials = provider_invoice.finantialdocumenthistory_set
        self.assertEqual(finantials.count(), 1)

        # finantial history info
        finantial = finantials.first()
        self.assertFinantialHistory(
            test_finantial_history=finantial, test_document=provider_invoice, test_user=self.test_user,
            test_old_status=None, test_new_status=test_status)

        test_date2 = test_date1 - timedelta(days=5)

        provider_invoice.date = test_date2

        provider_invoice = FinanceServices.save_provider_invoice(
            user=self.test_user,
            provider_invoice=provider_invoice)

        test_name2 = provider_invoice.name

        # name changed
        self.assertNotEqual(test_name1, test_name2)

        # document data auto filled
        self.assertDocument(provider_invoice, DOC_TYPE_PROVIDER_INVOICE, test_currency)

        # no finantial history created
        finantials = provider_invoice.finantialdocumenthistory_set
        self.assertEqual(finantials.count(), 1)

    def test_save_provider_invoice_ready_then_date(self):
        """
        Does ready provider_invoice and then change to draft
        """
        test_currency = CURRENCY_CUC
        test_date1 = timezone.now()
        test_amount = 100
        test_status = STATUS_READY

        provider_invoice = ProviderInvoice(
            provider=self.test_provider,
            date=test_date1,
            currency=test_currency,
            amount=test_amount,
            status=test_status)

        provider_invoice = FinanceServices.save_provider_invoice(
            user=self.test_user,
            provider_invoice=provider_invoice)

        test_name1 = provider_invoice.name

        # document data auto filled
        self.assertDocument(provider_invoice, DOC_TYPE_PROVIDER_INVOICE, test_currency)

        # one finantial history created
        finantials = provider_invoice.finantialdocumenthistory_set
        self.assertEqual(finantials.count(), 1)

        # finantial history info
        finantial = finantials.first()
        self.assertFinantialHistory(
            test_finantial_history=finantial, test_document=provider_invoice, test_user=self.test_user,
            test_old_status=None, test_new_status=test_status)

        test_date2 = test_date1 - timedelta(days=5)

        provider_invoice.date = test_date2

        provider_invoice = FinanceServices.save_provider_invoice(
            user=self.test_user,
            provider_invoice=provider_invoice)

        test_name2 = provider_invoice.name

        # name changed
        self.assertNotEqual(test_name1, test_name2)

        # document data auto filled
        self.assertDocument(provider_invoice, DOC_TYPE_PROVIDER_INVOICE, test_currency)

        # same finantial history
        finantials = provider_invoice.finantialdocumenthistory_set
        self.assertEqual(finantials.count(), 1)
