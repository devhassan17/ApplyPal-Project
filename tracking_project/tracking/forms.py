from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import University

class UniversitySignUpForm(UserCreationForm):
    # Fields related to the University model
    institution_name = forms.CharField(required=True)
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)
    calendly_link = forms.URLField(required=True, label="Calendly Link")
    address = forms.CharField(widget=forms.Textarea, required=True)

    class Meta:
        model = User  # Use the User model for username and password
        fields = ['username', 'email' ,'password1', 'password2', 'institution_name', 'first_name', 'last_name','calendly_link', 'address']
    