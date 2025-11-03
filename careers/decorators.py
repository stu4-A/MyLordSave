# careers/decorators.py
from django.shortcuts import redirect
from django.contrib import messages
from functools import wraps
from .models import UserProfile

def student_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated:
            profile = getattr(request.user, 'userprofile', None) or UserProfile.objects.filter(user=request.user).first()
            if profile and profile.role == 'student':
                return view_func(request, *args, **kwargs)
        messages.error(request, "You must be a student to access this page.")
        return redirect('login')
    return wrapper

def lecturer_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated:
            profile = getattr(request.user, 'userprofile', None) or UserProfile.objects.filter(user=request.user).first()
            if profile and profile.role == 'lecturer':
                return view_func(request, *args, **kwargs)
        messages.error(request, "You must be a lecturer to access this page.")
        return redirect('login')
    return wrapper
