from __future__ import unicode_literals

from django import forms
from django.utils import timezone

#from common.utils import send_email
from exceptions import Error
from .models import Caja, Transaction

class AccountActionForm(forms.Form):
    concept = forms.CharField(
        required=False,
        widget=forms.Textarea,
    )
    send_email = forms.BooleanField(
        required=False,
    )
    date = forms.DateTimeField()

    @property
    def email_subject_template(self):
        return 'email/account/notification_subject.txt'

    @property
    def email_body_template(self):
        raise NotImplementedError()

    def form_action(self, account, user):
        raise NotImplementedError()

    def save(self, caja, user):
        try:
            caja, transaction = self.form_action(caja, user)

        except Error as e:
            error_message = str(e)
            self.add_error(None, error_message)
            raise

        #if self.cleaned_data.get('send_email', False):
            #send_email(
            #    to=[caja.user.email],
            #    subject_template=self.email_subject_template,
            #    body_template=self.email_body_template,
            #    context={
            #        "account": caja,
            #        "transaction": transaction,
            #    }
            #)

        return caja, transaction


class WithdrawForm(AccountActionForm):
    amount = forms.IntegerField(
        #min_value=Account.MIN_WITHDRAW,
        #max_value=Account.MAX_WITHDRAW,
        required=True,
        help_text='Cantidad a extraer',
    )

    email_body_template = 'email/account/withdraw.txt'

    field_order = (
        'amount',
        'date',
        'comment',
        'send_email',
    )

    def form_action(self, caja, user):
        return Caja.withdraw(
            cid=caja.pk,
            #user=caja.user,
            amount=self.cleaned_data['amount'],
            withdrawn_by=user,
            concept=self.cleaned_data['concept'],
            asof=self.cleaned_data['date'],
        )

class DepositForm(AccountActionForm):
    amount = forms.IntegerField(
        #min_value=Account.MIN_DEPOSIT,
        #max_value=Account.MAX_DEPOSIT,
        required=True,
        help_text='Cantidad a depositar',
    )
    reference_type = forms.ChoiceField(
        required=True,
        choices=Transaction.REFERENCE_TYPE_CHOICES,
    )
    reference = forms.CharField(
        required=False,
    )

    email_body_template = 'email/account/deposit.txt'

    field_order = (
        'amount',
        'reference_type',
        'reference',
        'date',
        'concept',
        'send_email',
    )

    def form_action(self, caja, user):
        return Caja.deposit(
            cid=caja.pk,
            #user=caja.user,
            amount=self.cleaned_data['amount'],
            deposited_by=user,
            #reference=self.cleaned_data['reference'],
            reference_type=self.cleaned_data['reference_type'],
            concept=self.cleaned_data['concept'],
            asof=self.cleaned_data['date'],
        )

class TransferForm(AccountActionForm):
    amount = forms.IntegerField(
        required=True,
        help_text='Amount to be transfered from this Account'
    )
    rate = forms.FloatField(
        required=True,
        help_text='Exchange rate to apply on Destination Account'
    )

    destination = forms.ChoiceField(
        choices=[(obj.pk, obj.__str__()) for obj in Caja.objects.all()],
    )

    def form_action(self, caja, user):
        return Caja.transfer(
            cid=caja.pk,
            amount=self.cleaned_data['amount'],
            transfered_by=user,
            rate=self.cleaned_data['rate'],
            destination_id=self.cleaned_data['destination'],
            concept=self.cleaned_data['concept'],
            asof=self.cleaned_data['date'],
        )