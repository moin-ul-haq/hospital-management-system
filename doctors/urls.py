from django.urls import path
from accounts.urls import router
from .views import DoctorViewSet, AppointmentStatusUpdateView, AppointmentCancelView




urlpatterns = [
	path('appointments/<int:pk>/status/', AppointmentStatusUpdateView.as_view(), name='appointment-status-update'),
	path('appointments/<int:pk>/cancel/', AppointmentCancelView.as_view(), name='appointment-cancel'),
]
