from django import forms
from .models import Booking
from django.utils.dateparse import parse_date, parse_time

from django import forms
from .models import Booking

class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['counseling_type', 'date', 'time']
        widgets = {
            'counseling_type': forms.Select(attrs={
                'class': 'form-select',
                'aria-required': 'true',
                'id': 'id_counseling_type'
            }),
            'date': forms.TextInput(attrs={
                'class': 'form-control',
                'id': 'datePicker',
                'aria-required': 'true',
                'autocomplete': 'off',
                'placeholder': 'Select date',
            }),
            'time': forms.TextInput(attrs={
                'class': 'form-control',
                'id': 'timePicker',
                'aria-required': 'true',
                'autocomplete': 'off',
                'placeholder': 'Select time',
            }),
        }



    def clean(self):
        cleaned_data = super().clean()
        date = cleaned_data.get('date')
        time = cleaned_data.get('time')

        if date and time:
            exists = Booking.objects.filter(date=date, time=time, approved=True).exists()
            if exists:
                raise forms.ValidationError('This date and time is already booked.')
        return cleaned_data
