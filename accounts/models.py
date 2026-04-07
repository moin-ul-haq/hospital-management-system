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




