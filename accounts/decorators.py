# accounts/decorators.py

from django.shortcuts import redirect
from django.contrib import messages
from .models import UserProfile

def user_is_approved(function):
    def wrap(request, *args, **kwargs):
        user_profile = UserProfile.objects.get(user=request.user)
        if user_profile.is_approved:
            return function(request, *args, **kwargs)
        else:
            messages.error(request, 'Tu cuenta está pendiente de aprobación.')
            return redirect('home')
    return wrap

def admin_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, "Debes iniciar sesión para acceder a esta página.")
            return redirect('login')
        
        user_profile = request.user.userprofile
        if user_profile.role in ['ADMIN_TOTAL', 'ADMIN_DEPARTAMENTO']:
            return view_func(request, *args, **kwargs)
        else:
            messages.error(request, "No tienes permisos para acceder a esta página.")
            return redirect('index')  # O cualquier otra página de redirección
    return wrapper

def admin_department_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, "Debes iniciar sesión para acceder a esta página.")
            return redirect('login')
        
        user_profile = request.user.userprofile
        if user_profile.role == 'ADMIN_DEPARTAMENTO':
            return view_func(request, *args, **kwargs)
        else:
            messages.error(request, "No tienes permisos para acceder a esta página.")
            return redirect('index')  # O cualquier otra página de redirección
    return wrapper