from django.urls import path

from .views import PatientViewset, MedicalHistoryCreateView


urlpatterns = [
	path('patients/<int:pk>/report', PatientViewset.as_view({'get': 'report'}), name='patient-report'),
	path('patients/<int:pk>/history/add/', MedicalHistoryCreateView.as_view(), name='medical-history-add'),
]
