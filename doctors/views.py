from rest_framework.response import Response
from rest_framework.viewsets import ViewSet
from .models import DoctorProfile,Appointments
from hospitalmanagementsystem.permissions import IsDoctor,IsPatient,IsReceptionist,IsDoctorOrReceptionist
from rest_framework.permissions import IsAuthenticated,AllowAny
from rest_framework import status
from .serializers import DoctorSerializer,AppointmentSerializer
from patients.models import PatientProfile
from rest_framework.authentication import SessionAuthentication
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.decorators import action

class DoctorViewSet(ViewSet):
    authentication_classes=[SessionAuthentication,JWTAuthentication]
    def get_permissions(self):
        return [IsAuthenticated()]

    def list(self,request):
        doctors=DoctorProfile.objects.all()
        serializer=DoctorSerializer(doctors,many=True)
        return Response(serializer.data,status=status.HTTP_200_OK)


class AppointmentViewSet(ViewSet):
    authentication_classes=[SessionAuthentication,JWTAuthentication]
    def get_permissions(self):
        if self.action == "create":
            return [IsAuthenticated(),IsPatient()]
        return [IsAuthenticated()]
    
    def list(self,request):
        if request.user.role == 'patient':
            appointments=Appointments.objects.filter(patient=request.user.patient_profile)
        elif request.user.role == 'doctor':
            appointments=Appointments.objects.filter(doctor=request.user.doctor_profile)
        elif request.user.role in ['receptionist','admin']:
            appointments=Appointments.objects.all()
        serializer=AppointmentSerializer(appointments,many=True)
        return Response(serializer.data,status=status.HTTP_200_OK)
    
    
    
    
    def create(self,request):
        patient=PatientProfile.objects.get(user=request.user)
        serializer=AppointmentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(patient=patient)
            return Response(serializer.data,status=status.HTTP_201_CREATED)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True,methods=['patch'],url_path='status')
    def status(self,request,pk=None):
        try:
            appointment=Appointments.objects.get(pk=pk)
            serializer=AppointmentSerializer(appointment,data=request.data,partial=True)
        except Appointments.DoesNotExist:
            return Response({'message':"Appointment Does not Exists"},status=status.HTTP_404_NOT_FOUND)
        
        if request.user.role == 'receptionist' or (request.user.role == 'doctor' and appointment.doctor==request.user.doctor_profile):
            new_status=request.data.get('status')
            if new_status in ['pending','completed','cancelled','confirmed']:
                if serializer.is_valid():
                    serializer.save(status=new_status)
                    return Response(serializer.data,status=status.HTTP_201_CREATED)
        return Response({'message':"you are not allowed!"},status=status.HTTP_405_METHOD_NOT_ALLOWED)
 