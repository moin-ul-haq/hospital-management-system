from django.core.mail import send_mail
from hospitalmanagementsystem import settings
from celery import shared_task
from twilio.rest import Client

account_sid = settings.TWILIO_ACCOUNT_SID
auth_token=settings.TWILIO_AUTH_TOKEN


@shared_task
def appointment_email_task(doctor_email,patient_email,message_for_patient,message_for_doctor,subject):
    send_mail(subject=subject,recipient_list=[patient_email],message=message_for_patient,from_email=settings.DEFAULT_FROM_EMAIL)
    send_mail(subject=subject,recipient_list=[doctor_email],message=message_for_doctor,from_email=settings.DEFAULT_FROM_EMAIL)
    client = Client(account_sid, auth_token)
    message=client.messages.create(body=message_for_patient,from_=settings.TWILIO_NUMBER,to="+923433018324")



@shared_task
def send_appointment_reminder(patient_email, doctor_email, patient_name, doctor_name, appointment_date):
    subject = 'Appointment Reminder'
    message_patient = f"Hello {patient_name}! Reminder: Your appointment with {doctor_name} is tomorrow on {appointment_date}."
    message_doctor = f"Hello {doctor_name}! Reminder: You have an appointment with {patient_name} tomorrow on {appointment_date}."
    
    send_mail(subject, message_patient, settings.DEFAULT_FROM_EMAIL, [patient_email])
    send_mail(subject, message_doctor, settings.DEFAULT_FROM_EMAIL, [doctor_email])

    client = Client(account_sid, auth_token)
    message=client.messages.create(body=message_patient,from_=settings.TWILIO_NUMBER,to="+923433018324")



