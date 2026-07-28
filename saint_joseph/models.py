"""
Models pour Saint Joseph - Système de gestion hospitalier
Architecture: Django MVT
"""

from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone


class Utilisateur(models.Model):
    """Modèle Utilisateur étendu avec rôles"""
    
    ROLE_CHOICES = [
        ('admin', 'Administrateur'),
        ('medecin', 'Médecin'),
        ('infirmier', 'Infirmier'),
        ('patient', 'Patient'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profil_utilisateur')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='patient')
    telephone = models.CharField(max_length=20, blank=True, null=True)
    adresse = models.TextField(blank=True, null=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    est_actif = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-date_creation']
        verbose_name = 'Utilisateur'
        verbose_name_plural = 'Utilisateurs'
    
    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} ({self.get_role_display()})"


class Patient(models.Model):
    """Modèle Patient"""
    
    SEXE_CHOICES = [
        ('M', 'Masculin'),
        ('F', 'Féminin'),
        ('Autre', 'Autre'),
    ]
    
    GROUPE_SANGUIN_CHOICES = [
        ('O+', 'O+'),
        ('O-', 'O-'),
        ('A+', 'A+'),
        ('A-', 'A-'),
        ('B+', 'B+'),
        ('B-', 'B-'),
        ('AB+', 'AB+'),
        ('AB-', 'AB-'),
    ]
    
    utilisateur = models.OneToOneField(Utilisateur, on_delete=models.CASCADE, related_name='patient_profil')
    numero_patient = models.CharField(max_length=50, unique=True)
    date_naissance = models.DateField()
    sexe = models.CharField(max_length=10, choices=SEXE_CHOICES)
    groupe_sanguin = models.CharField(max_length=5, choices=GROUPE_SANGUIN_CHOICES, blank=True, null=True)
    telephone = models.CharField(max_length=20)
    email = models.EmailField()
    adresse = models.TextField()
    ville = models.CharField(max_length=100)
    code_postal = models.CharField(max_length=20)
    personne_contact = models.CharField(max_length=100)
    telephone_contact = models.CharField(max_length=20)
    allergies = models.TextField(blank=True, null=True)
    antecedents_medicaux = models.TextField(blank=True, null=True)
    date_inscription = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-date_inscription']
        verbose_name = 'Patient'
        verbose_name_plural = 'Patients'
    
    def save(self, *args, **kwargs):
        if not self.numero_patient:
            # Récupérer le dernier patient par ID
            last_patient = Patient.objects.all().order_by('id').last()
            if last_patient:
                next_id = last_patient.id + 1
            else:
                next_id = 1
            self.numero_patient = f"PAT-{next_id:06d}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.numero_patient} - {self.utilisateur.user.get_full_name()}"


class DossierMedical(models.Model):
    """Modèle Dossier Médical - Un dossier par patient"""
    
    patient = models.OneToOneField(Patient, on_delete=models.CASCADE, related_name='dossier_medical')
    numero_dossier = models.CharField(max_length=50, unique=True)
    date_ouverture = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    observations_generales = models.TextField(blank=True, null=True)
    est_actif = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = 'Dossier Médical'
        verbose_name_plural = 'Dossiers Médicaux'
    
    def __str__(self):
        return f"Dossier {self.numero_dossier} - {self.patient.utilisateur.user.get_full_name()}"


class Consultation(models.Model):
    """Modèle Consultation"""
    
    STATUS_CHOICES = [
        ('planifiee', 'Planifiée'),
        ('en_cours', 'En cours'),
        ('terminee', 'Terminée'),
        ('annulee', 'Annulée'),
    ]
    
    dossier_medical = models.ForeignKey(DossierMedical, on_delete=models.CASCADE, related_name='consultations')
    medecin = models.ForeignKey(Utilisateur, on_delete=models.SET_NULL, null=True, limit_choices_to={'role': 'medecin'}, related_name='consultations_effectuees')
    date_consultation = models.DateTimeField()
    motif = models.CharField(max_length=200)
    observations = models.TextField(blank=True, null=True)
    statut = models.CharField(max_length=20, choices=STATUS_CHOICES, default='planifiee')
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-date_consultation']
        verbose_name = 'Consultation'
        verbose_name_plural = 'Consultations'
    
    def __str__(self):
        return f"Consultation {self.id} - {self.dossier_medical.patient.numero_patient} ({self.date_consultation.strftime('%Y-%m-%d')})"


class Diagnostic(models.Model):
    """Modèle Diagnostic"""
    
    consultation = models.ForeignKey(Consultation, on_delete=models.CASCADE, related_name='diagnostics')
    libelle = models.CharField(max_length=200)
    description = models.TextField()
    date_diagnostic = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-date_diagnostic']
        verbose_name = 'Diagnostic'
        verbose_name_plural = 'Diagnostics'
    
    def __str__(self):
        return f"{self.libelle} - Consultation {self.consultation.id}"


class Prescription(models.Model):
    """Modèle Prescription"""
    
    consultation = models.ForeignKey(Consultation, on_delete=models.CASCADE, related_name='prescriptions')
    traitement = models.CharField(max_length=200)
    dose = models.CharField(max_length=100)
    duree = models.CharField(max_length=100)  # ex: "7 jours", "2 semaines"
    date_prescription = models.DateTimeField(auto_now_add=True)
    instructions = models.TextField(blank=True, null=True)
    
    class Meta:
        ordering = ['-date_prescription']
        verbose_name = 'Prescription'
        verbose_name_plural = 'Prescriptions'
    
    def __str__(self):
        return f"{self.traitement} ({self.dose}) - {self.duree}"


class Formulaire(models.Model):
    """Modèle Formulaire"""
    
    TYPE_CHOICES = [
        ('ordonnance', 'Ordonnance'),
        ('certificat', 'Certificat'),
        ('analyse', 'Analyse'),
        ('hospitalisation', 'Hospitalisation'),
        ('conge', 'Congé'),
        ('autre', 'Autre'),
    ]
    
    STATUT_CHOICES = [
        ('brouillon', 'Brouillon'),
        ('finalise', 'Finalisé'),
        ('archive', 'Archivé'),
    ]
    
    consultation = models.ForeignKey(Consultation, on_delete=models.CASCADE, related_name='formulaires')
    type_formulaire = models.CharField(max_length=50, choices=TYPE_CHOICES)
    contenu = models.TextField()
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='brouillon')
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    date_archivage = models.DateTimeField(blank=True, null=True)
    motif_archivage = models.TextField(blank=True, null=True)
    
    class Meta:
        ordering = ['-date_creation']
        verbose_name = 'Formulaire'
        verbose_name_plural = 'Formulaires'
    
    def __str__(self):
        return f"{self.get_type_formulaire_display()} - {self.consultation.dossier_medical.patient.numero_patient}"


class RendezVous(models.Model):
    """Modèle Rendez-vous"""
    
    STATUT_CHOICES = [
        ('planifie', 'Planifié'),
        ('confirme', 'Confirmé'),
        ('en_attente', 'En attente'),
        ('realise', 'Réalisé'),
        ('annule', 'Annulé'),
    ]
    
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='rendez_vous')
    medecin = models.ForeignKey(Utilisateur, on_delete=models.SET_NULL, null=True, limit_choices_to={'role': 'medecin'}, related_name='rendez_vous_prevus')
    date_heure = models.DateTimeField()
    motif = models.CharField(max_length=200)
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='planifie')
    notes = models.TextField(blank=True, null=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['date_heure']
        verbose_name = 'Rendez-vous'
        verbose_name_plural = 'Rendez-vous'
    
    def __str__(self):
        return f"RDV {self.patient.numero_patient} - {self.date_heure.strftime('%Y-%m-%d %H:%M')}"


class Hospitalisation(models.Model):
    """Modèle Hospitalisation"""
    
    STATUT_CHOICES = [
        ('admission', 'Admission'),
        ('hospitalisee', 'Hospitalisée'),
        ('sortie', 'Sortie'),
        ('transfert', 'Transfert'),
    ]
    
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='hospitalisations')
    date_admission = models.DateTimeField()
    date_sortie = models.DateTimeField(blank=True, null=True)
    lit = models.CharField(max_length=50)
    chambre = models.CharField(max_length=50, blank=True, null=True)
    etage = models.CharField(max_length=50, blank=True, null=True)
    motif_admission = models.TextField()
    observations = models.TextField(blank=True, null=True)
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='admission')
    medecin_responsable = models.ForeignKey(Utilisateur, on_delete=models.SET_NULL, null=True, limit_choices_to={'role': 'medecin'}, related_name='hospitalisations_supervisees')
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-date_admission']
        verbose_name = 'Hospitalisation'
        verbose_name_plural = 'Hospitalisations'
    
    def __str__(self):
        return f"Hospitalisation {self.patient.numero_patient} - {self.date_admission.strftime('%Y-%m-%d')}"


class Archive(models.Model):
    """Modèle Archive"""
    
    dossier_medical = models.ForeignKey(DossierMedical, on_delete=models.CASCADE, related_name='archive')
    date_archivage = models.DateTimeField(auto_now_add=True)
    motif_archivage = models.TextField()
    archiviste = models.ForeignKey(Utilisateur, on_delete=models.SET_NULL, null=True, related_name='archives_creees')
    
    class Meta:
        verbose_name = 'Archive'
        verbose_name_plural = 'Archives'
    
    def __str__(self):
        return f"Archive - Dossier {self.dossier_medical.numero_dossier} ({self.date_archivage.strftime('%Y-%m-%d')})"
