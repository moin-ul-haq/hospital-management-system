
from django.contrib import admin
from django.urls import path,include

urlpatterns = [
    path("admin/", admin.site.urls),
    path('auth/',include('rest_framework.urls')),
    path('api/',include('accounts.urls')),
    path('api/',include('patients.urls')),
    path('api/',include('doctors.urls')),

]
