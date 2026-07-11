"""
Django Admin Configuration pour Saint Joseph
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User, Group
from django.utils.html import format_html
from .models import (
    Utilisateur, Patient, DossierMedical, Consultation,
    Diagnostic, Prescription, Formulaire, RendezVous,
    Hospitalisation, Archive
)
from .signals import sync_user_role, GROUP_ROLE_MAP


# ============================================================================
# INLINE : affiche le profil Utilisateur (rôle) dans la page User Django
# ============================================================================

class UtilisateurInline(admin.StackedInline):
    model = Utilisateur
    can_delete = False
    verbose_name = "Profil Saint Joseph"
    verbose_name_plural = "Profil Saint Joseph"
    fields = ('role', 'telephone', 'adresse', 'est_actif')
    extra = 0


# ============================================================================
# CUSTOM USER ADMIN — étend l'admin User Django standard
# ============================================================================

class CustomUserAdmin(BaseUserAdmin):
    inlines = (UtilisateurInline,)
    list_display = (
        'username', 'email', 'first_name', 'last_name',
        'get_role_badge', 'get_groupes', 'is_staff', 'is_superuser'
    )
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups')
    actions = ['sync_roles_from_groups']

    def get_role_badge(self, obj):
        """Affiche le rôle actuel avec une couleur."""
        try:
            role = obj.profil_utilisateur.role
        except Exception:
            role = 'aucun'

        colors = {
            'admin':     '#dc2626',   # rouge
            'medecin':   '#2563eb',   # bleu
            'infirmier': '#059669',   # vert
            'patient':   '#6b7280',   # gris
            'aucun':     '#d97706',   # orange
        }
        labels = {
            'admin':     '🔴 Admin',
            'medecin':   '🔵 Médecin',
            'infirmier': '🟢 Infirmier',
            'patient':   '⚪ Patient',
            'aucun':     '🟠 Sans profil',
        }
        color = colors.get(role, '#6b7280')
        label = labels.get(role, role)
        return format_html(
            '<span style="background:{}; color:white; padding:2px 8px; '
            'border-radius:4px; font-size:11px; font-weight:bold;">{}</span>',
            color, label
        )
    get_role_badge.short_description = 'Rôle'
    get_role_badge.allow_tags = True

    def get_groupes(self, obj):
        """Affiche les groupes de l'utilisateur."""
        groupes = obj.groups.values_list('name', flat=True)
        if groupes:
            return ', '.join(groupes)
        return '—'
    get_groupes.short_description = 'Groupes'

    @admin.action(description='🔄 Synchroniser les rôles depuis les groupes')
    def sync_roles_from_groups(self, request, queryset):
        """Action admin pour synchroniser les rôles de plusieurs users d'un coup."""
        count = 0
        for user in queryset:
            sync_user_role(user)
            count += 1
        self.message_user(request, f"✅ {count} utilisateur(s) synchronisé(s).")


# Désenregistrer l'admin User par défaut et enregistrer le notre
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)



@admin.register(Utilisateur)
class UtilisateurAdmin(admin.ModelAdmin):
    list_display = ('get_nom_complet', 'get_role_badge', 'get_groupes_user', 'est_actif', 'date_creation')
    list_filter = ('role', 'est_actif', 'date_creation')
    search_fields = ('user__first_name', 'user__last_name', 'user__email')
    readonly_fields = ('date_creation', 'date_modification')
    fieldsets = (
        ('Informations Utilisateur', {
            'fields': ('user', 'role')
        }),
        ('Contact', {
            'fields': ('telephone', 'adresse')
        }),
        ('Statut', {
            'fields': ('est_actif',)
        }),
        ('Dates', {
            'fields': ('date_creation', 'date_modification'),
            'classes': ('collapse',)
        }),
    )

    def get_nom_complet(self, obj):
        return obj.user.get_full_name() or obj.user.username
    get_nom_complet.short_description = 'Nom Complet'

    def get_role_badge(self, obj):
        colors = {
            'admin':     '#dc2626',
            'medecin':   '#2563eb',
            'infirmier': '#059669',
            'patient':   '#6b7280',
        }
        labels = {
            'admin':     '🔴 Admin',
            'medecin':   '🔵 Médecin',
            'infirmier': '🟢 Infirmier',
            'patient':   '⚪ Patient',
        }
        color = colors.get(obj.role, '#6b7280')
        label = labels.get(obj.role, obj.role)
        return format_html(
            '<span style="background:{}; color:white; padding:2px 8px; '
            'border-radius:4px; font-size:11px; font-weight:bold;">{}</span>',
            color, label
        )
    get_role_badge.short_description = 'Rôle'

    def get_groupes_user(self, obj):
        groupes = obj.user.groups.values_list('name', flat=True)
        return ', '.join(groupes) if groupes else '—'
    get_groupes_user.short_description = 'Groupes Django'



@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ('numero_patient', 'get_nom_patient', 'date_naissance', 'groupe_sanguin', 'telephone')
    list_filter = ('sexe', 'groupe_sanguin', 'ville', 'date_inscription')
    search_fields = ('numero_patient', 'utilisateur__user__first_name', 'utilisateur__user__last_name', 'email')
    readonly_fields = ('numero_patient', 'date_inscription', 'date_modification')
    
    fieldsets = (
        ('Informations Patient', {
            'fields': ('numero_patient', 'utilisateur')
        }),
        ('Données Personnelles', {
            'fields': ('date_naissance', 'sexe', 'groupe_sanguin')
        }),
        ('Contact', {
            'fields': ('telephone', 'email', 'adresse', 'ville', 'code_postal')
        }),
        ('Personne de Contact', {
            'fields': ('personne_contact', 'telephone_contact')
        }),
        ('Données Médicales', {
            'fields': ('allergies', 'antecedents_medicaux')
        }),
        ('Dates', {
            'fields': ('date_inscription', 'date_modification'),
            'classes': ('collapse',)
        }),
    )
    
    def get_nom_patient(self, obj):
        return obj.utilisateur.user.get_full_name()
    get_nom_patient.short_description = 'Nom Complet'


@admin.register(DossierMedical)
class DossierMedicalAdmin(admin.ModelAdmin):
    list_display = ('numero_dossier', 'get_patient', 'date_ouverture', 'get_statut')
    list_filter = ('est_actif', 'date_ouverture')
    search_fields = ('numero_dossier', 'patient__numero_patient')
    readonly_fields = ('numero_dossier', 'date_ouverture', 'date_modification')
    
    fieldsets = (
        ('Informations Dossier', {
            'fields': ('numero_dossier', 'patient')
        }),
        ('Contenu', {
            'fields': ('observations_generales',)
        }),
        ('Statut', {
            'fields': ('est_actif',)
        }),
        ('Dates', {
            'fields': ('date_ouverture', 'date_modification'),
            'classes': ('collapse',)
        }),
    )
    
    def get_patient(self, obj):
        return obj.patient.numero_patient
    get_patient.short_description = 'Patient'
    
    def get_statut(self, obj):
        color = 'green' if obj.est_actif else 'red'
        status = 'Actif' if obj.est_actif else 'Inactif'
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            status
        )
    get_statut.short_description = 'Statut'


@admin.register(Consultation)
class ConsultationAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_patient', 'medecin', 'date_consultation', 'statut')
    list_filter = ('statut', 'date_consultation', 'medecin')
    search_fields = ('dossier_medical__patient__numero_patient', 'motif')
    readonly_fields = ('date_creation', 'date_modification')
    
    fieldsets = (
        ('Patient & Médecin', {
            'fields': ('dossier_medical', 'medecin')
        }),
        ('Détails de la Consultation', {
            'fields': ('date_consultation', 'motif', 'statut')
        }),
        ('Observations', {
            'fields': ('observations',)
        }),
        ('Dates', {
            'fields': ('date_creation', 'date_modification'),
            'classes': ('collapse',)
        }),
    )
    
    def get_patient(self, obj):
        return obj.dossier_medical.patient.numero_patient
    get_patient.short_description = 'Patient'


@admin.register(Diagnostic)
class DiagnosticAdmin(admin.ModelAdmin):
    list_display = ('libelle', 'get_consultation', 'date_diagnostic')
    list_filter = ('date_diagnostic',)
    search_fields = ('libelle', 'description')
    readonly_fields = ('date_diagnostic',)
    
    fieldsets = (
        ('Consultation', {
            'fields': ('consultation',)
        }),
        ('Diagnostic', {
            'fields': ('libelle', 'description')
        }),
        ('Date', {
            'fields': ('date_diagnostic',),
            'classes': ('collapse',)
        }),
    )
    
    def get_consultation(self, obj):
        return f"Consultation {obj.consultation.id}"
    get_consultation.short_description = 'Consultation'


@admin.register(Prescription)
class PrescriptionAdmin(admin.ModelAdmin):
    list_display = ('traitement', 'dose', 'duree', 'get_consultation', 'date_prescription')
    list_filter = ('date_prescription',)
    search_fields = ('traitement', 'instructions')
    readonly_fields = ('date_prescription',)
    
    fieldsets = (
        ('Consultation', {
            'fields': ('consultation',)
        }),
        ('Traitement', {
            'fields': ('traitement', 'dose', 'duree')
        }),
        ('Instructions', {
            'fields': ('instructions',)
        }),
        ('Date', {
            'fields': ('date_prescription',),
            'classes': ('collapse',)
        }),
    )
    
    def get_consultation(self, obj):
        return f"Consultation {obj.consultation.id}"
    get_consultation.short_description = 'Consultation'


@admin.register(Formulaire)
class FormulaireAdmin(admin.ModelAdmin):
    list_display = ('id', 'type_formulaire', 'get_patient', 'statut', 'date_creation')
    list_filter = ('type_formulaire', 'statut', 'date_creation')
    search_fields = ('consultation__dossier_medical__patient__numero_patient',)
    readonly_fields = ('date_creation', 'date_modification', 'date_archivage')
    
    fieldsets = (
        ('Consultation', {
            'fields': ('consultation',)
        }),
        ('Formulaire', {
            'fields': ('type_formulaire', 'statut')
        }),
        ('Contenu', {
            'fields': ('contenu',)
        }),
        ('Archivage', {
            'fields': ('date_archivage', 'motif_archivage')
        }),
        ('Dates', {
            'fields': ('date_creation', 'date_modification'),
            'classes': ('collapse',)
        }),
    )
    
    def get_patient(self, obj):
        return obj.consultation.dossier_medical.patient.numero_patient
    get_patient.short_description = 'Patient'


@admin.register(RendezVous)
class RendezVousAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_patient', 'medecin', 'date_heure', 'statut')
    list_filter = ('statut', 'date_heure', 'medecin')
    search_fields = ('patient__numero_patient', 'motif')
    readonly_fields = ('date_creation', 'date_modification')
    
    fieldsets = (
        ('Patient & Médecin', {
            'fields': ('patient', 'medecin')
        }),
        ('Rendez-vous', {
            'fields': ('date_heure', 'motif', 'statut')
        }),
        ('Notes', {
            'fields': ('notes',)
        }),
        ('Dates', {
            'fields': ('date_creation', 'date_modification'),
            'classes': ('collapse',)
        }),
    )
    
    def get_patient(self, obj):
        return obj.patient.numero_patient
    get_patient.short_description = 'Patient'


@admin.register(Hospitalisation)
class HospitalisationAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_patient', 'medecin_responsable', 'date_admission', 'statut', 'lit')
    list_filter = ('statut', 'date_admission', 'medecin_responsable')
    search_fields = ('patient__numero_patient', 'motif_admission')
    readonly_fields = ('date_creation', 'date_modification')
    
    fieldsets = (
        ('Patient', {
            'fields': ('patient', 'medecin_responsable')
        }),
        ('Admission', {
            'fields': ('date_admission', 'date_sortie', 'motif_admission')
        }),
        ('Localisation', {
            'fields': ('lit', 'chambre', 'etage')
        }),
        ('Statut', {
            'fields': ('statut',)
        }),
        ('Observations', {
            'fields': ('observations',)
        }),
        ('Dates', {
            'fields': ('date_creation', 'date_modification'),
            'classes': ('collapse',)
        }),
    )
    
    def get_patient(self, obj):
        return obj.patient.numero_patient
    get_patient.short_description = 'Patient'


@admin.register(Archive)
class ArchiveAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_formulaire', 'get_archiviste', 'date_archivage')
    list_filter = ('date_archivage', 'archiviste')
    search_fields = ('formulaire__consultation__dossier_medical__patient__numero_patient',)
    readonly_fields = ('date_archivage',)
    
    fieldsets = (
        ('Formulaire Archivé', {
            'fields': ('formulaire',)
        }),
        ('Archivage', {
            'fields': ('archiviste', 'motif_archivage')
        }),
        ('Date', {
            'fields': ('date_archivage',),
            'classes': ('collapse',)
        }),
    )
    
    def get_formulaire(self, obj):
        return f"{obj.formulaire.get_type_formulaire_display()}"
    get_formulaire.short_description = 'Type Formulaire'
    
    def get_archiviste(self, obj):
        return obj.archiviste.user.get_full_name() if obj.archiviste else 'N/A'
    get_archiviste.short_description = 'Archiviste'


# Customize admin site
admin.site.site_header = "Saint Joseph - Administration"
admin.site.site_title = "Saint Joseph Admin"
admin.site.index_title = "Bienvenue à Saint Joseph"
