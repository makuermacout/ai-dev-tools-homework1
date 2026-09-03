from django import forms
from django.contrib.auth.models import User
from .models import Household, HouseholdMember


class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']


class HouseholdForm(forms.ModelForm):
    class Meta:
        model = Household
        fields = ['name']