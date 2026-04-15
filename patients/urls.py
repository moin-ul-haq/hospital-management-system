from django.urls import path

from .views import PatientViewset


urlpatterns = [
	path('patients/<int:pk>/report', PatientViewset.as_view({'get': 'report'}), name='patient-report'),
]
