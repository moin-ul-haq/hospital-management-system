from django.db import models
from accounts.models import User
# Create your models here.
class PatientProfile(models.Model):
    user=models.OneToOneField(User,on_delete=models.CASCADE,related_name='patient_profile')
    blood_group=models.CharField(max_length=10,null=True,blank=True)
    Address=models.TextField(null=True,blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    phone = models.CharField(max_length=15, null=True, blank=True)
    emergency_contact = models.CharField(max_length=15, null=True, blank=True)
    
    def __str__(self):
        return f"Patient {self.user.name}"



class MedicalHistory(models.Model):
    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE, related_name='medical_histories')
    diagnosis = models.TextField()
    treatment = models.TextField()
    prescribed_medications = models.TextField(null=True, blank=True)
    notes = models.TextField(null=True, blank=True)
    visit_date = models.DateTimeField(auto_now_add=True)
    doctor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='patient_visits')

    def __str__(self):
        return f"Medical History - {self.patient.user.name} - {self.visit_date.date()}"