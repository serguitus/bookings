from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone

from accounting.constants import (
    MOVEMENT_TYPE_INPUT, MOVEMENT_TYPE_OUTPUT, CURRENCY_CUC, CURRENCY_USD,
    CONCEPT_DEPOSIT, CONCEPT_WITHDRAW, CONCEPT_TRANSFER, CONCEPT_CURRENCY_EXCHANGE)
from accounting.models import Account

from finance.models import Deposit
from finance.services import FinanceService


class FinanceServiceTestCase(TestCase):

    test_user = None

    def setUp(self):
        self.test_user = User.objects.create(
            username="Test User")
