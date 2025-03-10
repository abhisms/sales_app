# forms.py
from django import forms
from .models import Quotation

class QuotationForm(forms.ModelForm):
    class Meta:
        model = Quotation
        fields = ['customer', 'product_name', 'amount', 'quantity', 'expiry_date', 'status']
        widgets = {
            'expiry_date': forms.DateInput(attrs={'type': 'date'}),
        }

