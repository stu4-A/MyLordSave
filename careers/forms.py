# careers/forms.py
from django import forms
from .models import Application, StudentProfile, CareerOpportunity, UserProfile
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Application

# Application form
# careers/forms.py



class ApplicationForm(forms.ModelForm):
    message = forms.CharField(
        label="Message (optional)",
        required=False,
        widget=forms.Textarea(attrs={
            'rows': 4,
            'class': 'form-control',
            'placeholder': 'Write a short note or cover letter to the lecturer...'
        })
    )

    class Meta:
        model = Application
        fields = ['message']

# Profile form (student)
class ProfileForm(forms.ModelForm):
    class Meta:
        model = StudentProfile
        fields = ['skills', 'enrolled_subjects']
        widgets = {
            'skills': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Comma-separated skills, e.g. Python, SQL'}),
            'enrolled_subjects': forms.Textarea(attrs={'rows': 2, 'placeholder': 'Comma-separated subjects, e.g. Databases, OS'})
        }

# Registration form with role selection
ROLE_CHOICES = [
    ('student', 'Student'),
    ('lecturer', 'Lecturer'),
]

class RegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    role = forms.ChoiceField(choices=ROLE_CHOICES, required=True, initial='student')

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2', 'role')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            role = self.cleaned_data.get('role', 'student')
            # Ensure UserProfile exists (signal covers new users but do explicitly here)
            UserProfile.objects.get_or_create(user=user, defaults={'role': role})
            # Create StudentProfile only if role is student
            if role == 'student':
                StudentProfile.objects.get_or_create(user=user)
        return user

# Lecturer opportunity form
class OpportunityForm(forms.ModelForm):
    class Meta:
        model = CareerOpportunity
        fields = ['company', 'role', 'deadline', 'link', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Describe the opportunity'}),
            'deadline': forms.DateInput(attrs={'type': 'date'})
        }
