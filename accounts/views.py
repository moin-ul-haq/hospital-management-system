from django.shortcuts import render
from rest_framework import viewsets
from .models import User
from .serializers import RegisterSerializer,UserSerializer
from rest_framework.permissions import AllowAny,IsAuthenticated
from rest_framework.decorators import action
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate
from rest_framework_simplejwt.authentication import JWTAuthentication
from hospitalmanagementsystem.permissions import IsAdmin
from rest_framework.authentication import SessionAuthentication
from .tasks import send_login_email,send_signup_email
from hospitalmanagementsystem import settings


class AuthViewSet(viewsets.ViewSet):
    authentication_classes=[JWTAuthentication]
    def get_permissions(self):
        if self.action in ['register','login']:
            return [AllowAny()]
        return [IsAuthenticated()]
    @action(detail=False,methods=['POST'],url_path='register')
    def register(self,request):
        serializer=RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user=serializer.save()
            refresh=RefreshToken.for_user(user=user)
            send_signup_email.delay(receiver=user.email,subject='Account Registered Successfully',message=f'Hello {user.name}, You have Created Your account Successfully.',sender=settings.DEFAULT_FROM_EMAIL)
            return Response({
                'message': 'User registered successfully',
                'role': user.role,
                'access': str(refresh.access_token),
                'refresh': str(refresh),
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False,methods=['POST'],url_path='login')
    def login(self,request):
        username=request.data.get('username')
        password=request.data.get('password')
        user=authenticate(username=username,password=password)
        if user is None:
            return Response({'message':'Invalid Credentials'})
        refresh=RefreshToken.for_user(user)
        send_login_email.delay(receiver=user.email,subject='Account Logged in Successfully',message=f'Hello {user.name}, You have Logged in to Your account Successfully.',sender=settings.DEFAULT_FROM_EMAIL)
        return Response({
            'name':user.name,
            'role':user.role,
            'access':str(refresh.access_token),
            'refresh':str(refresh)
        })
    
    @action(detail=False,methods=['POST'],url_path='logout')
    def logout(self,request):
        print(request.user)
        print(request.headers.get('Authorization'))
        try:
            token=RefreshToken(request.data.get('refresh'))
            token.blacklist()
            return Response({'message':'Logged Out Successfully'})
        except Exception:
            return Response({"error":"inlvalid Token"},status=status.HTTP_400_BAD_REQUEST)
        
    @action(detail=False,methods=['get'],url_path='me')
    def profile(self,request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)
    

class UserViewSet(viewsets.ViewSet):
    permission_classes=[IsAuthenticated,IsAdmin]
    authentication_classes=[SessionAuthentication,JWTAuthentication]


    def list(self,request):
        users=User.objects.all()
        serializer=UserSerializer(users,many=True)
        return Response(serializer.data)

    def retrieve(self,request,pk=None):
        try:
            user=User.objects.get(pk=pk)
        except Exception:
            return Response({'message':'User Not Fount'})
        serializer=UserSerializer(user)
        # if user is None:
        #     return Response({'message':'User Not found'})
        return Response(serializer.data)
    

    def destroy(self,request,pk=None):
        user=User.objects.get(pk=pk)
        if user is None:
            return Response({'message':"User Not Found"})
        user.delete()
        return Response({"message":"User Deleted Successfully"})
    

    @action(detail=True, methods=['post'], url_path='role')
    def update_role(self, request, pk=None):
        try:
            user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            return Response({'message':'User Not Found'}, status=status.HTTP_404_NOT_FOUND)

        new_role = request.data.get('role')
        if new_role not in ['patient','doctor','receptionist','admin']:
            return Response({'message':'Invalid Role'}, status=status.HTTP_400_BAD_REQUEST)

        user.role = new_role
        user.save()
        return Response({'success': f'Role changed to {new_role}'})