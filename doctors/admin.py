from django.contrib import admin
from .models import DoctorProfile,Appointments


admin.site.register(DoctorProfile)
admin.site.register(Appointments)