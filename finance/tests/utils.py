from accounting.tests.tests_services import AccountingBaseTestCase

from finance.models import LoanEntityCurrency, LoanAccount, AgencyCurrency, Provider
class FinanceBaseTestCase(AccountingBaseTestCase):

    def assertDocument(self, test_document, test_doc_type, test_currency):
        self.assertEqual(test_document.document_type, test_doc_type)
        self.assertEqual(test_document.currency, test_currency)

    def assertFinantialHistory(
            self, test_finantial_history, test_user, test_document,
            test_old_status, test_new_status):
        self.assertEqual(test_finantial_history.user_id, test_user.pk)
        self.assertEqual(test_finantial_history.document_id, test_document.pk)
        self.assertEqual(test_finantial_history.old_status, test_old_status)
        self.assertEqual(test_finantial_history.new_status, test_new_status)

    def assertLoanEntityCurrencyCreditAmount(self, loan_entity, currency, amount):
        loan_entity_currency = LoanEntityCurrency.objects.get(
            loan_entity_id=loan_entity.pk, currency=currency)
        self.assertEqual(loan_entity_currency.credit_amount, amount)

    def assertLoanEntityCurrencyDebitAmount(self, loan_entity, currency, amount):
        loan_entity_currency = LoanEntityCurrency.objects.get(
            loan_entity_id=loan_entity.pk, currency=currency)
        self.assertEqual(loan_entity_currency.debit_amount, amount)

    def assertLoanEntityCurrencyMatchedAmount(self, loan_entity, currency, amount):
        loan_entity_currency = LoanEntityCurrency.objects.get(
            loan_entity_id=loan_entity.pk, currency=currency)
        self.assertEqual(loan_entity_currency.matched_amount, amount)

    def assertLoanAccountCreditAmount(self, loan_account, amount):
        loan_account = LoanAccount.objects.get(
            loan_account_id=loan_account.pk)
        self.assertEqual(loan_account.credit_amount, amount)

    def assertLoanAccountDebitAmount(self, loan_account, amount):
        loan_account = LoanAccount.objects.get(
            loan_account_id=loan_account.pk)
        self.assertEqual(loan_account.debit_amount, amount)

    def assertLoanAccountMatchedAmount(self, loan_account, amount):
        loan_account = LoanAccount.objects.get(
            loan_account_id=loan_account.pk)
        self.assertEqual(loan_account.matched_amount, amount)

    def assertAgencyCurrencyCreditAmount(self, agency, currency, amount):
        agency_currency = AgencyCurrency.objects.get(
            agency_id=agency.pk, currency=currency)
        self.assertEqual(agency_currency.credit_amount, amount)

    def assertAgencyCurrencyDebitAmount(self, agency, currency, amount):
        agency_currency = AgencyCurrency.objects.get(
            agency_id=agency.pk, currency=currency)
        self.assertEqual(agency_currency.debit_amount, amount)

    def assertAgencyCurrencyMatchedAmount(self, agency, currency, amount):
        agency_currency = AgencyCurrency.objects.get(
            agency_id=agency.pk, currency=currency)
        self.assertEqual(agency_currency.matched_amount, amount)

    def assertProviderCurrencyCreditAmount(self, provider, currency, amount):
        provider_currency = ProviderCurrency.objects.get(
            provider_id=provider.pk, currency=currency)
        self.assertEqual(provider_currency.credit_amount, amount)

    def assertProviderCurrencyDebitAmount(self, provider, currency, amount):
        provider_currency = ProviderCurrency.objects.get(
            provider_id=provider.pk, currency=currency)
        self.assertEqual(provider_currency.debit_amount, amount)

    def assertProviderCurrencyMatchedAmount(self, provider, currency, amount):
        provider_currency = ProviderCurrency.objects.get(
            provider_id=provider.pk, currency=currency)
        self.assertEqual(provider_currency.matched_amount, amount)

