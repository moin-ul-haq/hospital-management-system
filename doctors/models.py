from django.db import models
from accounts.models import User
from patients.models import PatientProfile

class DoctorProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='doctor_profile')
    specialization = models.CharField(max_length=100, null=True, blank=True)
    qualification = models.CharField(max_length=100, null=True, blank=True)
    experience_years = models.IntegerField(default=0)
    phone = models.CharField(max_length=15, null=True, blank=True)
    available_from = models.TimeField(null=True, blank=True)
    available_to = models.TimeField(null=True, blank=True)

    def __str__(self):
        return f"Dr. {self.user.name}"
    


class Appointments(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    doctor=models.ForeignKey(DoctorProfile,on_delete=models.CASCADE,related_name='appointments')
    patient=models.ForeignKey(PatientProfile,on_delete=models.CASCADE,related_name='appointments')
    appointment_date = models.DateField()
    appointment_time = models.TimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    reason = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together=['doctor','appointment_time','appointment_date']
    
    def __str__(self):
        return f"{self.patient.name} → Dr.{self.doctor.name} | {self.appointment_date}"