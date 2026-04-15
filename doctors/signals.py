from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Appointments
from django.core.mail import send_mail
from hospitalmanagementsystem import settings
from .tasks import appointment_email_task,send_appointment_reminder
from datetime import timedelta, datetime
import pytz


@receiver(post_save,sender=Appointments)
def send_appointment_email(sender,instance,created,**kwargs):
    if created:
        subject='Appointment Requested'
        message_for_patient=f"Hello {instance.patient.user.name}! Your Appointment with Dr. {instance.doctor.user.name} is Created and is waiting for confirmation."
        message_for_doctor=f"Hello Dr. {instance.doctor.user.name}! You have a new Appointment with {instance.patient.user.name} pending for confirmation on {instance.appointment_date} at {instance.appointment_date}"
    elif instance.status=='confirmed':
        subject='Appointment Confirmed'
        message_for_patient=f"Hello {instance.patient.user.name}! Your Appointment with Dr. {instance.doctor.user.name} is Confirmed on {instance.appointment_date} at {instance.appointment_date}"
        message_for_doctor=f"Hello Dr. {instance.doctor.user.name}! Your Appointment with {instance.patient.user.name} is confirmed on {instance.appointment_date} at {instance.appointment_date}"
    elif instance.status=='completed':
        subject='Appointment Completed'
        message_for_patient=f"Hello {instance.patient.user.name}! Your Appointment with Dr. {instance.doctor.user.name} is Completed."
        message_for_doctor=f"Hello Dr. {instance.doctor.user.name}! Your Appointment with {instance.patient.user.name} is Completed"
    elif instance.status=='cancelled':
        subject='Appointment Cancelled'
        message_for_patient=f"Hello {instance.patient.user.name}! You have cancelled your Appointment with Dr. {instance.doctor.user.name}"
        message_for_doctor=f"Hello Dr. {instance.doctor.user.name}! Your Appointment with {instance.patient.user.name} is cancelled by Patient."
    appointment_email_task.delay(doctor_email=instance.doctor.user.email,patient_email=instance.patient.user.email,subject=subject,message_for_patient=message_for_patient,message_for_doctor=message_for_doctor)


    
    
@receiver(post_save, sender=Appointments)
def schedule_appointment_reminder(sender, instance, created=False, **kwargs):
    if created:
        # appointment_date se 1 din pehle ka time nikalna
        appointment_datetime = datetime.combine(
            instance.appointment_date,
            instance.appointment_time  # agar alag field hai time ki
        )
        
        # timezone aware banao
        tz = pytz.timezone('Asia/Karachi')
        appointment_datetime = tz.localize(appointment_datetime)
        
        # 1 din pehle
        reminder_24hr = appointment_datetime - timedelta(hours=24)
        
        # 12 ghante pehle
        reminder_12hr = appointment_datetime - timedelta(hours=12)
        
        # schedule both reminders
        send_appointment_reminder.apply_async(
            kwargs={
                'patient_email': instance.patient.user.email,
                'doctor_email': instance.doctor.user.email,
                'patient_name': instance.patient.user.name,
                'doctor_name': instance.doctor.user.name,
                'appointment_date': str(instance.appointment_date),
            },
            eta=reminder_24hr
        )
        
        send_appointment_reminder.apply_async(
            kwargs={
                'patient_email': instance.patient.user.email,
                'doctor_email': instance.doctor.user.email,
                'patient_name': instance.patient.user.name,
                'doctor_name': instance.doctor.user.name,
                'appointment_date': str(instance.appointment_date),
            },
            eta=reminder_12hr
        )