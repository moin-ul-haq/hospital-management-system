from django import forms
from .models import Appointments, DoctorProfile


class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointments
        fields = ['doctor', 'appointment_date', 'appointment_time', 'reason']
        widgets = {
            'appointment_date': forms.DateInput(attrs={'type': 'date'}),
            'appointment_time': forms.TimeInput(attrs={'type': 'time'}),
        }


class DoctorFilterForm(forms.Form):
    specialization = forms.CharField(required=False)