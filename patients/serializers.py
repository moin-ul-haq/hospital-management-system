from rest_framework import serializers
from .models import PatientProfile,MedicalHistory

class PatientSerializer(serializers.ModelSerializer):
    class Meta:
        model=PatientProfile
        fields='__all__'