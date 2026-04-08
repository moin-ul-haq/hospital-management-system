from django.shortcuts import render
from rest_framework.viewsets import ViewSet
from rest_framework.permissions import IsAuthenticated
from hospitalmanagementsystem.permissions import IsPatient,IsDoctorOrReceptionist,IsDoctor
from rest_framework.decorators import action
from .models import PatientProfile,MedicalHistory
from rest_framework.response import Response
from rest_framework import status
from .serializers import PatientSerializer,MedicalHistorySerializer
from rest_framework.authentication import SessionAuthentication
from rest_framework_simplejwt.authentication import JWTAuthentication

class PatientViewset(ViewSet):
    authentication_classes=[SessionAuthentication,JWTAuthentication]
    def get_permissions(self):
        if self.action in ['profile']:
            return [IsAuthenticated(),IsPatient()]
        elif self.action in ['list','retrieve']:
            return [IsAuthenticated(), IsDoctorOrReceptionist()]
        elif self.action in ['history']:
            if self.request.method=='GET':
                return [IsAuthenticated(),IsDoctorOrReceptionist()]
            return [IsAuthenticated(),IsDoctor()]
        return [IsAuthenticated()] 


        
    @action(detail=False,methods=['get','patch'],url_path='profile')
    def profile(self,request):
        try:
            patient=PatientProfile.objects.get(user=request.user)
        except Exception:
            return Response({'message':'Profile not Found'},status=status.HTTP_404_NOT_FOUND)
        
        if request.method=='GET':
            serializer=PatientSerializer(patient)
            return Response(serializer.data,status=status.HTTP_200_OK)
        
        elif request.method=='PATCH':
            print('yes')
            serializer=PatientSerializer(patient,data=request.data,partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data,status=status.HTTP_200_OK)
            
            return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
        

    def list(self, request):
        patients = PatientProfile.objects.all()
        serializer = PatientSerializer(patients, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def retrieve(self,request,pk):
        try:
            patient = PatientProfile.objects.get(pk=pk)
        except PatientProfile.DoesNotExist:
            return Response({'message':"Patient Not Found"},status=status.HTTP_404_NOT_FOUND)
        serializer=PatientSerializer(patient)
        return Response(serializer.data,status=status.HTTP_200_OK)


    @action(detail=True,methods=['get','post'],url_path='history')
    def history(self,request,pk=None):
        try:
            patient=PatientProfile.objects.get(pk=pk)
        except PatientProfile.DoesNotExist:
            return Response({'message':'Patient Not Found'},status=status.HTTP_404_NOT_FOUND)
        if request.method=='GET':
            history=MedicalHistory.objects.filter(patient=patient)
            serializer=MedicalHistorySerializer(history,many=True)
            return Response(serializer.data,status=status.HTTP_200_OK)
        elif request.method=='POST':
            serializer=MedicalHistorySerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(patient=patient,doctor=request.user)
                return Response(serializer.data,status=status.HTTP_201_CREATED)
            return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)