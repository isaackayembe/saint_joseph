#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'archive.settings')
django.setup()

from django.contrib.auth.models import User
from saint_joseph.models import Utilisateur

# Trouve l'utilisateur isaac
try:
    user = User.objects.get(username='isaac')
    print(f"Utilisateur trouvé: {user.username}")
    
    # Trouve ou crée son profil
    utilisateur, created = Utilisateur.objects.get_or_create(user=user)
    print(f"Profil créé: {created}")
    
    # Change son rôle en admin
    utilisateur.role = 'admin'
    utilisateur.save()
    
    print(f"✓ Rôle de {user.username} changé en: {utilisateur.role}")
except User.DoesNotExist:
    print("✗ Utilisateur isaac non trouvé")
except Exception as e:
    print(f"✗ Erreur: {e}")
