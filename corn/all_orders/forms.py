from django import forms
from .models import ExpenseOrder

class ExpenseOrderForm(forms.ModelForm):
    class Meta:
        model = ExpenseOrder
        fields = ['status', 'recipient', 'amount', 'basis', 'comment']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            # 'recipient': forms.TextInput(attrs={'class': 'form-control'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'basis': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'comment': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }

class ExpenseOrderApproveForm(forms.ModelForm):
    class Meta:
        model = ExpenseOrder
        fields = []
