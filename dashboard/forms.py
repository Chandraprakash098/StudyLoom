from django import forms
from . models import *
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
import random
import string
import secrets

class NotesForm(forms.ModelForm):
    class Meta:
        model=Notes
        fields=['title','desription']

class DateInput(forms.DateInput):
    input_type='date'

class HomeworkForm(forms.ModelForm):
    class Meta:
        model=Homework
        widgets={'due':DateInput()}
        fields=['subject','title','desription','due','is_finished']

class Dashboardform(forms.Form):
    text= forms.CharField(max_length=100,label="Search")

class TodoForm(forms.ModelForm):
    class Meta:
        model=Todo
        fields=['title','is_finished']

class userRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({
                'class': 'mt-1 block w-full px-3 py-2 bg-white border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500'
            })
