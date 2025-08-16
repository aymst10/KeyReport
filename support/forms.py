from django import forms
from .models import SupportTicket, ServiceRequest, ServiceSchedule
from django.utils import timezone


class SupportTicketForm(forms.ModelForm):
    """Form for creating and updating support tickets."""
    
    class Meta:
        model = SupportTicket
        fields = [
            'title', 'description', 'ticket_type', 'priority', 
            'related_product'
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Brief description of your issue'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Please provide detailed information about your issue...'
            }),
            'ticket_type': forms.Select(attrs={
                'class': 'form-control'
            }),
            'priority': forms.Select(attrs={
                'class': 'form-control'
            }),
            'related_product': forms.Select(attrs={
                'class': 'form-control'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make related_product optional
        self.fields['related_product'].required = False
        self.fields['related_product'].empty_label = "Select a product (optional)"


class ServiceRequestForm(forms.ModelForm):
    """Form for creating and updating service requests."""
    
    class Meta:
        model = ServiceRequest
        fields = [
            'service_type', 'title', 'description', 'service_address',
            'service_city', 'service_state', 'service_zip_code',
            'preferred_date', 'preferred_time'
        ]
        widgets = {
            'service_type': forms.Select(attrs={
                'class': 'form-control'
            }),
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Brief description of the service needed'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Please provide detailed information about the service you need...'
            }),
            'service_address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Service address'
            }),
            'service_city': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'City'
            }),
            'service_state': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'State/Province'
            }),
            'service_zip_code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'ZIP/Postal Code'
            }),
            'preferred_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'preferred_time': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time'
            }),
        }
    
    def clean_preferred_date(self):
        """Validate that preferred date is not in the past."""
        preferred_date = self.cleaned_data.get('preferred_date')
        if preferred_date and preferred_date < timezone.now().date():
            raise forms.ValidationError('Preferred date cannot be in the past.')
        return preferred_date


class TicketResponseForm(forms.Form):
    """Form for adding responses to tickets."""
    
    message = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'placeholder': 'Type your response here...'
        })
    )
    
    is_internal = forms.BooleanField(
        required=False,
        label='Internal note (staff only)',
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )


class ServiceScheduleForm(forms.ModelForm):
    """Form for scheduling service appointments."""
    
    class Meta:
        model = ServiceSchedule
        fields = [
            'technician', 'scheduled_date', 'scheduled_time', 
            'estimated_duration', 'notes'
        ]
        widgets = {
            'technician': forms.Select(attrs={
                'class': 'form-control'
            }),
            'scheduled_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'scheduled_time': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time'
            }),
            'estimated_duration': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '15',
                'step': '15'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Additional notes for the technician...'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filter technicians to only show staff members
        if 'technician' in self.fields:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            self.fields['technician'].queryset = User.objects.filter(
                user_type__in=['staff', 'admin']
            )
    
    def clean_scheduled_date(self):
        """Validate that scheduled date is not in the past."""
        scheduled_date = self.cleaned_data.get('scheduled_date')
        if scheduled_date and scheduled_date < timezone.now().date():
            raise forms.ValidationError('Scheduled date cannot be in the past.')
        return scheduled_date
    
    def clean_estimated_duration(self):
        """Validate estimated duration."""
        duration = self.cleaned_data.get('estimated_duration')
        if duration and duration < 15:
            raise forms.ValidationError('Estimated duration must be at least 15 minutes.')
        return duration
