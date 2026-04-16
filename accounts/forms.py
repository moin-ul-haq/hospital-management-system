from django import forms
from accounts.models import User
from django.contrib.auth.forms import UserCreationForm

class SignupForm(UserCreationForm):
    email=forms.EmailField(required=True)
    name=forms.CharField(max_length=50)
    class Meta:
        model=User
        fields=['name','username','email','role','password1','password2']