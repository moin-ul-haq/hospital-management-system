from rest_framework import serializers
from .models import PatientProfile,MedicalHistory

class PatientSerializer(serializers.ModelSerializer):
    class Meta:
        model=PatientProfile
        fields='__all__'

class MedicalHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model=MedicalHistory
        fields='__all__'