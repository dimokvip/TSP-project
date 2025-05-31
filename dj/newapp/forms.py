from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Task

class RegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'password1', 'password2']


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'description', 'status', 'priority', 'deadline', 'tags']
        widgets = {
            'tags': forms.CheckboxSelectMultiple()
        }