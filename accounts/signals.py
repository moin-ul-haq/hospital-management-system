from django.db.models.signals import post_save
from .models import User
from patients.models import PatientProfile
from doctors.models import DoctorProfile
from django.dispatch import receiver

@receiver(post_save,sender=User)
def create_patient_or_doctor(sender,instance,created,**kwargs):
    if created:
        if instance.role=='patient':
            PatientProfile.objects.create(user=instance)
        elif instance.role=='doctor':
            DoctorProfile.objects.create(user=instance)

    