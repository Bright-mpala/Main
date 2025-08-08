from django import forms
from .models import PAYMENT_METHODS, ProjectApplication, ProjectComment, Project, Donation
from django_countries.widgets import CountrySelectWidget

from django.forms.widgets import ClearableFileInput

class MultiFileInput(ClearableFileInput):
    allow_multiple_selected = True

    def value_from_datadict(self, data, files, name):
        if not files:
            return None
        return files.getlist(name)
    

class DonationForm(forms.ModelForm):
    terms = forms.BooleanField(required=True, label="I agree to the terms and conditions")

    class Meta:
        model = Donation
        fields = ['name', 'email', 'amount', 'payment_method', 'proof', 'project', 'country']
        widgets = {
            'country': CountrySelectWidget(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['project'].queryset = Project.objects.filter(status='ongoing')
        self.fields['project'].required = False
        self.fields['project'].label = "Choose a Project to Support (optional)"
        self.fields['project'].empty_label = "General Donation (No specific project)"

    def clean(self):
        cleaned_data = super().clean()
        method = cleaned_data.get('payment_method')
        proof = cleaned_data.get('proof')

        if method in ['bank', 'ecocash'] and not proof:
            self.add_error('proof', 'Proof of payment is required for bank and EcoCash donations.')

from django import forms
from .models import ProjectApplication

class ProjectApplicationForm(forms.ModelForm):
    images = forms.FileField(
        widget=MultiFileInput(attrs={'multiple': True}), 
        required=False,
        label="Upload Images (You can select multiple)"
    )

    class Meta:
        model = ProjectApplication
        fields = ['motivation']
 # 'images' is handled separately, not in model fields


class ProjectCommentForm(forms.ModelForm):
    class Meta:
        model = ProjectComment
        fields = ['comment']
        widgets = {
            'comment': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Leave a comment...',
                'class': 'form-control'
            }),
        }

from .models import Task

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'description', 'assigned_to', 'due_date', 'completed']
        widgets = {
            'due_date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 3}),
            }