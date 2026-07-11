"""
Commande : python manage.py create_default_roles

Crée les groupes Django standards et synchronise les rôles Saint Joseph.
Appelée automatiquement au démarrage Docker (voir docker-compose.yml).
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, User


# Mapping groupe → rôle Saint Joseph
GROUPS = {
    'Administrateurs': 'admin',
    'Médecins':        'medecin',
    'Infirmiers':      'infirmier',
}


class Command(BaseCommand):
    help = "Crée les groupes par défaut (Administrateurs, Médecins, Infirmiers) et synchronise les rôles."

    def add_arguments(self, parser):
        parser.add_argument(
            '--sync-all',
            action='store_true',
            help='Synchronise tous les utilisateurs existants depuis leurs groupes.'
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.MIGRATE_HEADING("=== Saint Joseph — Initialisation des groupes ==="))

        # 1. Créer les groupes Django
        for group_name in GROUPS:
            group, created = Group.objects.get_or_create(name=group_name)
            if created:
                self.stdout.write(self.style.SUCCESS(f"  ✅ Groupe créé : {group_name}"))
            else:
                self.stdout.write(f"  ℹ️  Groupe existant : {group_name}")

        # 2. Synchroniser tous les users si demandé
        if options['sync_all']:
            self.stdout.write(self.style.MIGRATE_HEADING("\n=== Synchronisation des rôles ==="))
            from saint_joseph.signals import sync_user_role
            users = User.objects.all()
            count = 0
            for user in users:
                sync_user_role(user)
                count += 1
            self.stdout.write(self.style.SUCCESS(f"  ✅ {count} utilisateur(s) synchronisé(s)."))

        self.stdout.write(self.style.SUCCESS("\n✅ Initialisation terminée."))
        self.stdout.write(
            "\n💡 Dans le panel admin Django :\n"
            "   Authentification → Groupes → Choisir un groupe → Ajouter des utilisateurs\n"
            "   Le rôle Saint Joseph sera mis à jour automatiquement.\n"
        )
