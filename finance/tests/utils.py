from accounting.tests.tests_services import AccountingBaseTestCase

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
