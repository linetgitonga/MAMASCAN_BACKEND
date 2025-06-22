from django import forms
from django.utils import timezone
from .models import Appointment, Client, Service, Staff, ClientFeedback

class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['client', 'staff', 'service', 'appointment_date', 'appointment_time', 'notes']
        widgets = {
            'appointment_date': forms.DateInput(attrs={
                'type': 'date', 
                'class': 'form-control',
                'min': timezone.now().date().isoformat()
            }),
            'appointment_time': forms.TimeInput(attrs={
                'type': 'time', 
                'class': 'form-control'
            }),
            'notes': forms.Textarea(attrs={
                'rows': 3, 
                'class': 'form-control',
                'placeholder': 'Any special notes or requirements...'
            }),
            'client': forms.Select(attrs={'class': 'form-control'}),
            'staff': forms.Select(attrs={'class': 'form-control'}),
            'service': forms.Select(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['staff'].queryset = Staff.objects.filter(is_active=True)
        self.fields['service'].queryset = Service.objects.filter(is_active=True)
        self.fields['client'].queryset = Client.objects.filter(is_active=True)

class AppointmentStatusForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['status']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-control'}),
        }

class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = [
            'first_name', 'last_name', 'email', 'phone', 'address', 
            'date_of_birth', 'notes'
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'date_of_birth': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }

class FeedbackForm(forms.ModelForm):
    class Meta:
        model = ClientFeedback
        fields = ['rating', 'comment', 'would_recommend']
        widgets = {
            'rating': forms.Select(attrs={'class': 'form-control'}),
            'comment': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'would_recommend': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
