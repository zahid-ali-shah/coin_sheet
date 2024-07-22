import logging
from decimal import Decimal

from django import forms
from django.contrib.admin.widgets import AdminDateWidget
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import transaction, IntegrityError

from core.models import DailyExpense, PaymentMode, PaymentTransaction

logger = logging.getLogger(__name__)
DEBIT_STYLE = 'color:green;border-color:green;'
CREDIT_STYLE = 'color:red;border-color:red;'


class DailyExpenseForm(forms.ModelForm):
    user = forms.ModelChoiceField(queryset=get_user_model().objects.all())
    date = forms.DateField(widget=AdminDateWidget)
    amount = forms.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('1.00'))])
    payment_mode = forms.ModelChoiceField(queryset=PaymentMode.objects.filter(is_active=True).all())
    comment = forms.CharField(required=False, widget=forms.Textarea)
    is_deposited = forms.BooleanField(required=False)

    def __init__(self, *args, **kwargs):
        super(DailyExpenseForm, self).__init__(*args, **kwargs)
        is_deposited = False

        if tr := getattr(self.instance, 'transaction', None):
            ptr = PaymentTransaction.objects.filter(id=tr.id).first()
            is_deposited = ptr.is_deposited
            self.fields['amount'].initial = abs(ptr.amount)
            self.fields['date'].initial = ptr.date
            self.fields['payment_mode'].initial = ptr.payment_mode
            self.fields['user'].initial = ptr.user
            self.fields['comment'].initial = ptr.comment
            self.fields['is_deposited'].initial = ptr.is_deposited

        self.fields['amount'].widget.attrs['style'] = DEBIT_STYLE if is_deposited else CREDIT_STYLE

    class Meta:
        model = DailyExpense
        fields = '__all__'

    def save(self, commit=True):
        instance = super(DailyExpenseForm, self).save(commit=False)
        try:
            with ((transaction.atomic())):
                data = {
                    'date': self.cleaned_data['date'],
                    'payment_mode': self.cleaned_data['payment_mode'],
                    'amount': self.cleaned_data['amount'],
                    'user': self.cleaned_data['user'],
                    'comment': self.cleaned_data['comment'],
                    'is_deposited': self.cleaned_data['is_deposited'],
                }
                if tr := getattr(instance, 'transaction', None):
                    ptr = PaymentTransaction.objects.filter(id=tr.id).first()
                    ptr.date = data['date']
                    ptr.payment_mode = data['payment_mode']
                    ptr.amount = data['amount']
                    ptr.user = data['user']
                    ptr.comment = data['comment']
                    ptr.is_deposited = data['is_deposited']
                    ptr.save()
                else:
                    ptr = PaymentTransaction(**data)
                    ptr.save()
                instance.transaction = ptr
                instance.transaction_id = ptr.id
                instance.save()
                return instance
        except IntegrityError as iex:
            logger.error(iex)
            raise Exception('Unable to save DailyExpense, looks like there is an error in PaymentTransaction')


class PaymentTransactionForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(PaymentTransactionForm, self).__init__(*args, **kwargs)

        if amount := getattr(self.instance, 'amount', 0):
            self.instance.amount = abs(amount)

        super(PaymentTransactionForm, self).__init__(*args, **kwargs)
        is_deposited = self.fields['is_deposited'].initial
        self.fields['amount'].widget.attrs['style'] = DEBIT_STYLE if is_deposited else CREDIT_STYLE

    class Meta:
        model = PaymentTransaction
        fields = '__all__'

