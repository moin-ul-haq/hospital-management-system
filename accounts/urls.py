from django.urls import path
from rest_framework.routers import DefaultRouter
from django.urls import path,include
from .views import AuthViewSet,UserViewSet
from rest_framework_simplejwt.views import TokenRefreshView


router = DefaultRouter()
router.register(r'auth',AuthViewSet,basename='auth')
router.register(r'users',UserViewSet,basename='users')



urlpatterns = [
    path('', include(router.urls)),
    path('auth/token/refresh/', TokenRefreshView.as_view()),
]