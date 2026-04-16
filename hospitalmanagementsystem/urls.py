from .views import home
from django.contrib import admin
from django.urls import path,include
from accounts.views import SignupView,LoginView,LogoutView,DashboardRedirectView
from patients.views import PatientListView,PatientDetailView
from doctors.views import DoctorListView,AppointmentCreateView,AppointmentStatusUpdateView
from hospitalmanagementsystem.views import dashboard,patient_dashboard,doctor_dashboard,receptionist_dashboard,admin_dashboard,profile

urlpatterns = [
    path("admin/", admin.site.urls),
    path('auth/',include('rest_framework.urls')),
    path('api/',include('accounts.urls')),
    path('api/',include('patients.urls')),
    path('api/',include('doctors.urls')),
    path("",home,name='homepage'),
    path('register/',SignupView.as_view(),name='register'),
    path('login/',LoginView.as_view(),name='login'),
    path('dashboard/',DashboardRedirectView.as_view(),name='dashboard'),
    path('logout/',LogoutView.as_view(),name='logout'),
    path('dashboard/patient/',patient_dashboard,name='patient_dashboard'),
    path('dashboard/doctor/',doctor_dashboard,name='doctor_dashboard'),
    path('dashboard/receptionist/',receptionist_dashboard,name='receptionist_dashboard'),
    path('dashboard/admin/',admin_dashboard,name='admin_dashboard'),
    path('profile/',profile,name='profile'),
    path('patients/',PatientListView.as_view(),name='patients'),
    path('patients/<int:pk>/',PatientDetailView.as_view(),name='patient_detail'),
    path('doctors/',DoctorListView.as_view(),name='doctors'),
    path('appointments/book/',AppointmentCreateView.as_view(),name='book_appointment'),
    path('appointments/<int:pk>/status/',AppointmentStatusUpdateView.as_view(),name='appointment-status-update-frontend'),

]
