"""
Signals Django pour synchroniser les Groupes Django ↔ rôles Saint Joseph.

Logique :
  - Groupe "Médecins"         → role = 'medecin'
  - Groupe "Infirmiers"       → role = 'infirmier'
  - Groupe "Administrateurs"  → role = 'admin'
  - Aucun groupe              → role = 'patient' (défaut)
  - is_superuser              → toujours 'admin' (via decorators.py)

Priorité des groupes : admin > medecin > infirmier > patient
"""

import logging
from django.db.models.signals import m2m_changed, post_save
from django.dispatch import receiver
from django.contrib.auth.models import User, Group
from django.db import transaction

logger = logging.getLogger(__name__)

# Mapping Groupe Django → rôle Saint Joseph
GROUP_ROLE_MAP = {
    'Administrateurs': 'admin',
    'Médecins':        'medecin',
    'Infirmiers':      'infirmier',
}

# Priorité des rôles (le plus élevé gagne si user dans plusieurs groupes)
ROLE_PRIORITY = {
    'admin':     3,
    'medecin':   2,
    'infirmier': 1,
    'patient':   0,
}


def compute_role_from_groups(user):
    """
    Calcule le rôle à partir des groupes Django de l'utilisateur.
    Retourne le rôle le plus élevé, ou 'patient' si aucun groupe pertinent.
    """
    if user.is_superuser:
        return 'admin'

    user_groups = set(user.groups.values_list('name', flat=True))
    best_role = 'patient'
    best_priority = -1

    for group_name, role in GROUP_ROLE_MAP.items():
        if group_name in user_groups:
            priority = ROLE_PRIORITY.get(role, 0)
            if priority > best_priority:
                best_role = role
                best_priority = priority

    return best_role


def sync_user_role(user):
    """
    Met à jour le champ `Utilisateur.role` en fonction des groupes Django de l'user.
    Crée le profil Utilisateur si nécessaire.
    """
    from .models import Utilisateur  # import local pour éviter les imports circulaires

    new_role = compute_role_from_groups(user)

    try:
        profil = user.profil_utilisateur
        if profil.role != new_role:
            old_role = profil.role
            profil.role = new_role
            profil.save(update_fields=['role'])
            logger.info(
                f"Rôle mis à jour pour {user.username}: {old_role} → {new_role}"
            )
    except Utilisateur.DoesNotExist:
        # Créer le profil s'il n'existe pas encore
        Utilisateur.objects.create(user=user, role=new_role)
        logger.info(f"Profil créé pour {user.username} avec rôle '{new_role}'")


@receiver(m2m_changed, sender=User.groups.through)
def on_user_groups_changed(sender, instance, action, pk_set, **kwargs):
    """
    Déclenché quand les groupes d'un utilisateur changent.
    Synchronise le rôle Saint Joseph automatiquement.
    """
    if action not in ('post_add', 'post_remove', 'post_clear'):
        return

    # `instance` peut être soit un User soit un Group selon le sens de la M2M
    if isinstance(instance, User):
        # On utilise transaction.on_commit pour s'assurer que la M2M est bien sauvée
        transaction.on_commit(lambda: sync_user_role(instance))

    elif isinstance(instance, Group):
        # Si le groupe lui-même a été modifié, on met à jour tous ses membres
        def sync_all_members():
            for user in instance.user_set.all():
                sync_user_role(user)
        transaction.on_commit(sync_all_members)


@receiver(post_save, sender=User)
def on_user_saved(sender, instance, created, **kwargs):
    """
    Quand un User est créé ou modifié (ex: is_superuser changé),
    synchronise le rôle.
    """
    transaction.on_commit(lambda: sync_user_role(instance))
