from django import forms
from .models import Transaction, Category, BudgetLimit


class TransactionForm(forms.ModelForm):
    class Meta:
        model   = Transaction
        fields  = ('amount', 'type', 'description', 'category', 'date', 'notes')
        widgets = {'date': forms.DateInput(attrs={'type': 'date'})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].queryset  = Category.objects.all()
        self.fields['category'].required  = False
        for f in self.fields.values():
            f.widget.attrs.setdefault('class', 'fin-input')


class BudgetLimitForm(forms.ModelForm):
    class Meta:
        model  = BudgetLimit
        fields = ('category', 'amount')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].queryset = Category.objects.all()
        for f in self.fields.values():
            f.widget.attrs.setdefault('class', 'fin-input')
