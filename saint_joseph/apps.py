from django.apps import AppConfig


class SaintJosephConfig(AppConfig):
    name = 'saint_joseph'
    verbose_name = 'Saint Joseph'

    def ready(self):
        """Connecter les signals au démarrage."""
        import saint_joseph.signals  # noqa: F401 — enregistre les signals

        # Créer les groupes APRÈS les migrations (évite le RuntimeWarning)
        from django.db.models.signals import post_migrate
        post_migrate.connect(self._create_groups_on_migrate, sender=self)

    @staticmethod
    def _create_groups_on_migrate(sender, **kwargs):
        """Crée les groupes Django après chaque migration."""
        try:
            from django.contrib.auth.models import Group
            for name in ['Administrateurs', 'Médecins', 'Infirmiers']:
                Group.objects.get_or_create(name=name)
        except Exception:
            pass
