"""
Decorators pour authentification et permissions
"""

from functools import wraps
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import redirect
from django.contrib import messages


def role_required(*roles):
    """
    Décorateur pour vérifier le rôle de l'utilisateur
    
    Usage:
        @role_required('medecin', 'admin')
        def ma_vue(request):
            ...
    """
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def wrapper(request, *args, **kwargs):
            try:
                if request.user.profil_utilisateur.role in roles:
                    return view_func(request, *args, **kwargs)
                else:
                    messages.error(request, "Vous n'avez pas la permission d'accéder à cette page.")
                    return redirect('dashboard')
            except:
                messages.error(request, "Erreur de vérification de rôle.")
                return redirect('login')
        return wrapper
    return decorator


def admin_required(view_func):
    """Décorateur pour les administrateurs uniquement"""
    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        try:
            if request.user.profil_utilisateur.role == 'admin':
                return view_func(request, *args, **kwargs)
            else:
                messages.error(request, "Seuls les administrateurs peuvent accéder à cette page.")
                return redirect('dashboard')
        except:
            return redirect('login')
    return wrapper


def medecin_required(view_func):
    """Décorateur pour les médecins"""
    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        try:
            if request.user.profil_utilisateur.role in ['medecin', 'admin']:
                return view_func(request, *args, **kwargs)
            else:
                messages.error(request, "Vous devez être médecin pour accéder à cette page.")
                return redirect('dashboard')
        except:
            return redirect('login')
    return wrapper


def infirmier_required(view_func):
    """Décorateur pour les infirmiers"""
    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        try:
            if request.user.profil_utilisateur.role in ['infirmier', 'medecin', 'admin']:
                return view_func(request, *args, **kwargs)
            else:
                messages.error(request, "Vous devez être infirmier pour accéder à cette page.")
                return redirect('dashboard')
        except:
            return redirect('login')
    return wrapper


def patient_or_medecin_required(view_func):
    """Décorateur pour patients ou médecins"""
    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        try:
            role = request.user.profil_utilisateur.role
            if role in ['patient', 'medecin', 'infirmier', 'admin']:
                return view_func(request, *args, **kwargs)
            else:
                messages.error(request, "Vous n'avez pas accès à cette ressource.")
                return redirect('dashboard')
        except:
            return redirect('login')
    return wrapper
