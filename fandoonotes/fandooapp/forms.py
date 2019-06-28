from django import forms
from .models import UserProfileInfo
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm


class UserForm(forms.ModelForm):        # User Form
    password = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = User
        fields = ('username', 'password', 'email')


class UserProfileInfoForm(forms.ModelForm):     # User profile Info Form

    class Meta:
        model = UserProfileInfo
        fields = ('portfolio_site', 'profile_pic')


class SignupForm(UserCreationForm):     # signup form
    email = forms.EmailField(max_length=200, help_text='Required')

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')
