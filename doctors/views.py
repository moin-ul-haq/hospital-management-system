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
from django.views.generic import ListView, CreateView
from django.views import View
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.http import HttpResponseForbidden
from .forms import AppointmentForm
from .tasks import appointment_email_task

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

    def _can_update_status(self, request, appointment):
        if request.user.role == 'receptionist':
            return True
        if request.user.role == 'doctor' and getattr(appointment.doctor, 'user_id', None) == request.user.id:
            return True
        return False
    
    @action(detail=True,methods=['patch'],url_path='status')
    def status(self,request,pk=None):
        try:
            appointment=Appointments.objects.get(pk=pk)
        except Appointments.DoesNotExist:
            return Response({'message':"Appointment Does not Exists"},status=status.HTTP_404_NOT_FOUND)
        
        if not self._can_update_status(request, appointment):
            return Response({'message':"you are not allowed!"},status=status.HTTP_405_METHOD_NOT_ALLOWED)

        new_status=request.data.get('status')
        if new_status not in ['pending','confirmed','completed','cancelled']:
            return Response({'message':'Invalid status.'}, status=status.HTTP_400_BAD_REQUEST)

        appointment.status = new_status
        appointment.save(update_fields=['status'])
        serializer = AppointmentSerializer(appointment)
        return Response(serializer.data,status=status.HTTP_200_OK)


class DoctorListView(ListView):
    model = DoctorProfile
    template_name = 'doctors_list.html'
    context_object_name = 'doctors'


class AppointmentCreateView(LoginRequiredMixin, CreateView):
    model = Appointments
    form_class = AppointmentForm
    template_name = 'appointment_form.html'
    success_url = reverse_lazy('dashboard')

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or getattr(request.user, 'role', None) != 'patient':
            return redirect('dashboard')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        patient = getattr(self.request.user, 'patient_profile', None)
        if patient is None:
            return redirect('dashboard')
        appointment = form.save(commit=False)
        appointment.patient = patient
        appointment.save()

        patient_email = patient.user.email
        doctor_email = appointment.doctor.user.email
        patient_name = patient.user.name
        doctor_name = appointment.doctor.user.name
        appointment_date = appointment.appointment_date

        appointment_email_task.delay(
            doctor_email=doctor_email,
            patient_email=patient_email,
            message_for_patient=f'Hello {patient_name}, your appointment with Dr. {doctor_name} is booked for {appointment_date}.',
            message_for_doctor=f'Hello Dr. {doctor_name}, you have a new appointment with {patient_name} on {appointment_date}.',
            subject='Appointment Booked Successfully',
        )

        return redirect(self.success_url)


class AppointmentStatusUpdateView(LoginRequiredMixin, View):
    def post(self, request, pk):
        if getattr(request.user, 'role', None) not in ['doctor', 'receptionist']:
            return HttpResponseForbidden('You are not allowed to update appointment status.')

        appointment = Appointments.objects.select_related('doctor__user', 'patient__user').filter(pk=pk).first()
        if appointment is None:
            return redirect('dashboard')

        if request.user.role == 'doctor' and appointment.doctor.user_id != request.user.id:
            return HttpResponseForbidden('You can only update your own appointments.')

        if appointment.status == 'completed':
            return HttpResponseForbidden('Completed appointments cannot be changed.')

        new_status = request.POST.get('status')
        if new_status in ['pending', 'confirmed', 'completed', 'cancelled'] and new_status != 'completed':
            appointment.status = new_status
            appointment.save(update_fields=['status'])

        return redirect('dashboard')


class AppointmentCancelView(LoginRequiredMixin, View):
    def post(self, request, pk):
        if getattr(request.user, 'role', None) != 'patient':
            return HttpResponseForbidden('Only patients can cancel appointments.')

        appointment = Appointments.objects.select_related('patient__user').filter(pk=pk, patient__user=request.user).first()
        if appointment is None:
            return redirect('dashboard')

        if appointment.status == 'completed':
            return HttpResponseForbidden('Completed appointments cannot be cancelled.')

        if appointment.status == 'cancelled':
            return HttpResponseForbidden('This appointment is already cancelled.')

        appointment.status = 'cancelled'
        appointment.save(update_fields=['status'])
        return redirect('dashboard')
 