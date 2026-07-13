#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script pour creer les donnees initiales Saint Joseph
"""

import os
import django
import sys

# Ensure UTF-8 encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'archive.settings')
django.setup()

from django.contrib.auth.models import User
from saint_joseph.models import Utilisateur

# Creer superuser
if not User.objects.filter(username='admin').exists():
    user = User.objects.create_superuser(
        username='admin',
        email='admin@saintjoseph.com',
        password='Admin@123456'
    )
    
    # Creer le profil utilisateur (ou le mettre a jour s'il a ete cree par le signal)
    Utilisateur.objects.update_or_create(
        user=user,
        defaults={
            'role': 'admin',
            'telephone': '+243999999999'
        }
    )
    
    print("[OK] Superuser cree: admin / Admin@123456")
else:
    print("[OK] Admin existe deja")

# Creer des utilisateurs test
roles = [('medecin', 'Dr', 'Smith'), ('infirmier', 'Infirmier', 'Jean'), ('patient', 'Patient', 'Paul')]

for role, first, last in roles:
    username = f'{role}1'
    if not User.objects.filter(username=username).exists():
        user = User.objects.create_user(
            username=username,
            email=f'{username}@saintjoseph.com',
            password='Test@123456',
            first_name=first,
            last_name=last
        )
        
        Utilisateur.objects.update_or_create(
            user=user,
            defaults={
                'role': role,
                'telephone': '+243999999999'
            }
        )
        
        print(f"[OK] Utilisateur cree: {username} ({role})")

print("\n[DONE] Donnees initiales crees!")
print("\nComptes disponibles:")
print("  Admin: admin / Admin@123456")
print("  Medecin: medecin1 / Test@123456")
print("  Infirmier: infirmier1 / Test@123456")
print("  Patient: patient1 / Test@123456")
