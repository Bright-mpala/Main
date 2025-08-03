from django import forms
from .models import PAYMENT_METHODS

class DonationForm(forms.Form):
    name = forms.CharField(max_length=100, required=True)
    email = forms.EmailField(required=True)
    amount = forms.DecimalField(min_value=1, max_digits=10, decimal_places=2, required=True)
    payment_method = forms.ChoiceField(choices=PAYMENT_METHODS, required=True)
    proof = forms.FileField(required=False)
    terms = forms.BooleanField(required=True, label="I agree to the terms and conditions")

    def clean(self):
        cleaned_data = super().clean()
        method = cleaned_data.get('payment_method')
        proof = cleaned_data.get('proof')

        if method in ['bank', 'ecocash'] and not proof:
            self.add_error('proof', 'Proof of payment is required for bank and EcoCash donations.')
      