from celery import shared_task
from django.core.mail import send_mail 



@shared_task
def send_login_email(subject,sender,message,receiver):
    send_mail(subject=subject,from_email=sender,message=message,recipient_list=[receiver])




@shared_task
def send_signup_email(subject,sender,message,receiver):
    send_mail(subject=subject,from_email=sender,message=message,recipient_list=[receiver])