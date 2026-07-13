"""
Decorators pour authentification et permissions
"""

from functools import wraps
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import redirect
from django.contrib import messages
import logging

logger = logging.getLogger(__name__)


def get_user_role(user):
    """
    Retourne le rôle de l'utilisateur.
    - Si superuser ou staff Django → traité comme 'admin' (tous les droits)
    - Sinon → rôle du profil_utilisateur
    - Si pas de profil → crée un profil 'patient' par défaut
    """
    # Les superusers Django ont tous les droits, toujours
    if user.is_superuser or user.is_staff:
        return 'admin'

    try:
        return user.profil_utilisateur.role
    except Exception:
        # Créer automatiquement le profil s'il n'existe pas
        from .models import Utilisateur
        utilisateur, created = Utilisateur.objects.get_or_create(
            user=user,
            defaults={'role': 'patient'}
        )
        if created:
            logger.warning(f"Profil créé automatiquement pour {user.username} avec rôle 'patient'")
        return utilisateur.role


def role_required(*roles):
    """
    Décorateur pour vérifier le rôle de l'utilisateur.
    Les superusers Django ont accès à tout.

    Usage:
        @role_required('medecin', 'admin')
        def ma_vue(request):
            ...
    """
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def wrapper(request, *args, **kwargs):
            user_role = get_user_role(request.user)

            if user_role in roles:
                return view_func(request, *args, **kwargs)
            else:
                logger.warning(
                    f"Accès refusé pour {request.user.username} "
                    f"(rôle: {user_role}, requis: {roles}) → {request.path}"
                )
                messages.error(
                    request,
                    f"⛔ Accès refusé — Votre rôle actuel ({user_role}) "
                    f"ne permet pas d'accéder à cette page."
                )
                return redirect('saint_joseph:dashboard')
        return wrapper
    return decorator


def admin_required(view_func):
    """Décorateur pour les administrateurs uniquement. Les superusers ont accès."""
    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        user_role = get_user_role(request.user)

        if user_role == 'admin':
            return view_func(request, *args, **kwargs)
        else:
            logger.warning(
                f"Accès admin refusé pour {request.user.username} (rôle: {user_role})"
            )
            messages.error(
                request,
                "⛔ Accès refusé — Seuls les administrateurs peuvent accéder à cette page."
            )
            return redirect('saint_joseph:dashboard')
    return wrapper


def medecin_required(view_func):
    """Décorateur pour les médecins (et admins/superusers)."""
    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        user_role = get_user_role(request.user)

        if user_role in ['medecin', 'admin']:
            return view_func(request, *args, **kwargs)
        else:
            messages.error(
                request,
                "⛔ Accès refusé — Vous devez être médecin pour accéder à cette page."
            )
            return redirect('saint_joseph:dashboard')
    return wrapper


def infirmier_required(view_func):
    """Décorateur pour les infirmiers (et médecins/admins/superusers)."""
    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        user_role = get_user_role(request.user)

        if user_role in ['infirmier', 'medecin', 'admin']:
            return view_func(request, *args, **kwargs)
        else:
            messages.error(
                request,
                "⛔ Accès refusé — Vous devez être infirmier pour accéder à cette page."
            )
            return redirect('saint_joseph:dashboard')
    return wrapper


def patient_or_medecin_required(view_func):
    """Décorateur pour patients, médecins, infirmiers et admins."""
    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        user_role = get_user_role(request.user)

        if user_role in ['patient', 'medecin', 'infirmier', 'admin']:
            return view_func(request, *args, **kwargs)
        else:
            messages.error(
                request,
                "⛔ Accès refusé — Vous n'avez pas accès à cette ressource."
            )
            return redirect('saint_joseph:dashboard')
    return wrapper
