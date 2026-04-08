from rest_framework import serializers
from .models import DoctorProfile,Appointments


class DoctorSerializer(serializers.ModelSerializer):
    name=serializers.StringRelatedField(source='user.name')
    class Meta:
        model=DoctorProfile
        fields=['id','name','specialization','qualification','experience_years','phone','available_from','available_to']

class AppointmentSerializer(serializers.ModelSerializer):
    class Meta:
        model=Appointments
        fields='__all__'
        read_only_fields = ['patient', 'status']