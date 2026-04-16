from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from doctors.models import Appointments, DoctorProfile
from patients.models import PatientProfile
from patients.models import MedicalHistory


def home(request):
    return render(request, 'index.html')


def dashboard(request):
    role = getattr(request.user, 'role', None)

    if role == 'patient':
        return redirect('patient_dashboard')
    if role == 'doctor':
        return redirect('doctor_dashboard')
    if role == 'receptionist':
        return redirect('receptionist_dashboard')
    if role == 'admin':
        return redirect('admin_dashboard')

    return redirect('homepage')


def patient_dashboard(request):
    patient = None
    appointments = []
    histories = []

    if request.user.is_authenticated and getattr(request.user, 'role', None) == 'patient':
        patient = PatientProfile.objects.filter(user=request.user).first()
        if patient:
            appointments = patient.appointments.select_related('doctor__user').order_by('-appointment_date', '-appointment_time')
            histories = patient.medical_histories.select_related('doctor').order_by('-visit_date')

    return render(request, 'dashboards/patient_dashboard.html', {
        'patient': patient,
        'appointments': appointments,
        'histories': histories,
    })


def doctor_dashboard(request):
    doctor = None
    appointments = []
    patients = []
    histories = []

    if request.user.is_authenticated and getattr(request.user, 'role', None) == 'doctor':
        doctor = DoctorProfile.objects.filter(user=request.user).first()
        if doctor:
            appointments = doctor.appointments.select_related('patient__user').order_by('-appointment_date', '-appointment_time')
            patients = PatientProfile.objects.filter(appointments__doctor=doctor).distinct().order_by('user__name')
            histories = MedicalHistory.objects.filter(doctor=request.user).select_related('patient__user').order_by('-visit_date')

    return render(request, 'dashboards/doctor_dashboard.html', {
        'doctor': doctor,
        'appointments': appointments,
        'patients': patients,
        'histories': histories,
    })


def receptionist_dashboard(request):
    appointments = Appointments.objects.select_related('doctor__user', 'patient__user').order_by('-created_at')
    return render(request, 'dashboards/receptionist_dashboard.html', {
        'appointments': appointments,
    })


def admin_dashboard(request):
    return render(request, 'dashboards/admin_dashboard.html')


@login_required
def profile(request):
    role = getattr(request.user, 'role', None)
    patient_profile = None
    doctor_profile = None

    if role == 'patient':
        patient_profile = PatientProfile.objects.filter(user=request.user).first()
    elif role == 'doctor':
        doctor_profile = DoctorProfile.objects.filter(user=request.user).first()

    return render(request, 'profile.html', {
        'patient_profile': patient_profile,
        'doctor_profile': doctor_profile,
    })