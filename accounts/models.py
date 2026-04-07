from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    role_choices = [
        ('patient', 'Patient'),
        ('doctor', 'Doctor'),
        ('receptionist', 'Receptionist'),
        ('admin', 'Admin'),
    ]
    name = models.CharField(max_length=255)
    role = models.CharField(choices=role_choices, max_length=20, default='patient')

    def __str__(self):
        return self.name


class PatientProfile(models.Model):
    user=models.OneToOneField(User,on_delete=models.CASCADE,related_name='patient_profile')
    blood_group=models.CharField(max_length=10,null=True,blank=True)
    Address=models.TextField(null=True,blank=True)
    
    def __str__(self):
        return f"Patient {self.user.name}"

class DoctorProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='doctor_profile')
    specialization = models.CharField(max_length=100, null=True, blank=True)
    qualification = models.CharField(max_length=100, null=True, blank=True)
    experience_years = models.IntegerField(default=0)

    def __str__(self):
        return f"Dr. {self.user.name}"