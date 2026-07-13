"""Forms Django pour Saint Joseph"""

from django import forms
from django.contrib.auth.models import User
from .models import (
    Utilisateur, Patient, DossierMedical, Consultation,
    Diagnostic, Prescription, Formulaire, RendezVous,
    Hospitalisation, Archive
)


class PatientForm(forms.ModelForm):
    """Formulaire de création/modification de patient"""
    
    class Meta:
        model = Patient
        fields = (
            'date_naissance', 'sexe', 'groupe_sanguin',
            'telephone', 'email', 'adresse', 'ville', 'code_postal',
            'personne_contact', 'telephone_contact', 'allergies', 'antecedents_medicaux'
        )
        widgets = {
            'date_naissance': forms.DateInput(attrs={
                'class': 'w-full px-4 py-2 border-2 border-gray-300 rounded-lg focus:outline-none focus:border-blue-500',
                'type': 'date'
            }),
            'sexe': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border-2 border-gray-300 rounded-lg focus:outline-none focus:border-blue-500'
            }),
            'groupe_sanguin': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border-2 border-gray-300 rounded-lg focus:outline-none focus:border-blue-500'
            }),
            'telephone': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border-2 border-gray-300 rounded-lg focus:outline-none focus:border-blue-500'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'w-full px-4 py-2 border-2 border-gray-300 rounded-lg focus:outline-none focus:border-blue-500'
            }),
            'adresse': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border-2 border-gray-300 rounded-lg focus:outline-none focus:border-blue-500',
                'rows': 3
            }),
            'ville': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border-2 border-gray-300 rounded-lg focus:outline-none focus:border-blue-500'
            }),
            'code_postal': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border-2 border-gray-300 rounded-lg focus:outline-none focus:border-blue-500'
            }),
            'personne_contact': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border-2 border-gray-300 rounded-lg focus:outline-none focus:border-blue-500'
            }),
            'telephone_contact': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border-2 border-gray-300 rounded-lg focus:outline-none focus:border-blue-500'
            }),
            'allergies': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border-2 border-gray-300 rounded-lg focus:outline-none focus:border-blue-500',
                'rows': 2
            }),
            'antecedents_medicaux': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border-2 border-gray-300 rounded-lg focus:outline-none focus:border-blue-500',
                'rows': 2
            }),
        }


class ConsultationForm(forms.ModelForm):
    """Formulaire de création/modification de consultation"""
    
    class Meta:
        model = Consultation
        fields = ('dossier_medical', 'medecin', 'date_consultation', 'motif', 'statut', 'observations')
        widgets = {
            'dossier_medical': forms.Select(attrs={'class': 'w-full px-4 py-2 border rounded'}),
            'medecin': forms.Select(attrs={'class': 'w-full px-4 py-2 border rounded'}),
            'date_consultation': forms.DateTimeInput(attrs={'class': 'w-full px-4 py-2 border rounded', 'type': 'datetime-local'}),
            'motif': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border rounded', 'placeholder': 'Motif de consultation'}),
            'statut': forms.Select(attrs={'class': 'w-full px-4 py-2 border rounded'}),
            'observations': forms.Textarea(attrs={'class': 'w-full px-4 py-2 border rounded', 'rows': 4}),
        }


class DiagnosticForm(forms.ModelForm):
    """Formulaire de diagnostic"""
    
    class Meta:
        model = Diagnostic
        fields = ('consultation', 'libelle', 'description')
        widgets = {
            'consultation': forms.Select(attrs={'class': 'w-full px-4 py-2 border rounded'}),
            'libelle': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border rounded', 'placeholder': 'Libellé du diagnostic'}),
            'description': forms.Textarea(attrs={'class': 'w-full px-4 py-2 border rounded', 'rows': 4}),
        }


class PrescriptionForm(forms.ModelForm):
    """Formulaire de prescription"""
    
    class Meta:
        model = Prescription
        fields = ('consultation', 'traitement', 'dose', 'duree', 'instructions')
        widgets = {
            'consultation': forms.Select(attrs={'class': 'w-full px-4 py-2 border rounded'}),
            'traitement': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border rounded', 'placeholder': 'Nom du traitement'}),
            'dose': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border rounded', 'placeholder': '1 comprimé x2'}),
            'duree': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border rounded', 'placeholder': '7 jours'}),
            'instructions': forms.Textarea(attrs={'class': 'w-full px-4 py-2 border rounded', 'rows': 3}),
        }


class FormulaireForm(forms.ModelForm):
    """Formulaire de formulaire"""
    
    class Meta:
        model = Formulaire
        fields = ('consultation', 'type_formulaire', 'contenu', 'statut')
        widgets = {
            'consultation': forms.Select(attrs={'class': 'w-full px-4 py-2 border rounded'}),
            'type_formulaire': forms.Select(attrs={'class': 'w-full px-4 py-2 border rounded'}),
            'contenu': forms.Textarea(attrs={'class': 'w-full px-4 py-2 border rounded', 'rows': 6}),
            'statut': forms.Select(attrs={'class': 'w-full px-4 py-2 border rounded'}),
        }


class RendezVousForm(forms.ModelForm):
    """Formulaire de rendez-vous"""
    
    class Meta:
        model = RendezVous
        fields = ('patient', 'medecin', 'date_heure', 'motif', 'statut', 'notes')
        widgets = {
            'patient': forms.Select(attrs={'class': 'w-full px-4 py-2 border rounded'}),
            'medecin': forms.Select(attrs={'class': 'w-full px-4 py-2 border rounded'}),
            'date_heure': forms.DateTimeInput(attrs={'class': 'w-full px-4 py-2 border rounded', 'type': 'datetime-local'}),
            'motif': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border rounded', 'placeholder': 'Motif du rendez-vous'}),
            'statut': forms.Select(attrs={'class': 'w-full px-4 py-2 border rounded'}),
            'notes': forms.Textarea(attrs={'class': 'w-full px-4 py-2 border rounded', 'rows': 3}),
        }


class HospitalisationForm(forms.ModelForm):
    """Formulaire d'hospitalisation"""
    
    class Meta:
        model = Hospitalisation
        fields = (
            'patient', 'date_admission', 'date_sortie', 'lit', 'chambre', 'etage',
            'motif_admission', 'observations', 'statut', 'medecin_responsable'
        )
        widgets = {
            'patient': forms.Select(attrs={'class': 'w-full px-4 py-2 border rounded'}),
            'date_admission': forms.DateTimeInput(attrs={'class': 'w-full px-4 py-2 border rounded', 'type': 'datetime-local'}),
            'date_sortie': forms.DateTimeInput(attrs={'class': 'w-full px-4 py-2 border rounded', 'type': 'datetime-local', 'required': False}),
            'lit': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border rounded', 'placeholder': 'A101'}),
            'chambre': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border rounded', 'placeholder': '101'}),
            'etage': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border rounded', 'placeholder': '1er étage'}),
            'motif_admission': forms.Textarea(attrs={'class': 'w-full px-4 py-2 border rounded', 'rows': 3}),
            'observations': forms.Textarea(attrs={'class': 'w-full px-4 py-2 border rounded', 'rows': 3}),
            'statut': forms.Select(attrs={'class': 'w-full px-4 py-2 border rounded'}),
            'medecin_responsable': forms.Select(attrs={'class': 'w-full px-4 py-2 border rounded'}),
        }


class ArchiveForm(forms.ModelForm):
    """Formulaire d'archivage"""
    
    class Meta:
        model = Archive
        fields = ('dossier_medical', 'motif_archivage', 'archiviste')
        widgets = {
            'dossier_medical': forms.Select(attrs={'class': 'w-full px-4 py-2 border rounded'}),
            'motif_archivage': forms.Textarea(attrs={'class': 'w-full px-4 py-2 border rounded', 'rows': 3}),
            'archiviste': forms.Select(attrs={'class': 'w-full px-4 py-2 border rounded'}),
        }


class UtilisateurForm(forms.ModelForm):
    """Formulaire pour le profil utilisateur"""
    
    class Meta:
        model = Utilisateur
        fields = ('telephone', 'adresse')
        widgets = {
            'telephone': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border-2 border-gray-300 rounded-lg',
                'placeholder': '+243999999999'
            }),
            'adresse': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border-2 border-gray-300 rounded-lg',
                'rows': 3
            }),
        }


class UserForm(forms.ModelForm):
    """Formulaire de création d'utilisateur"""
    
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-2 border-2 border-gray-300 rounded-lg',
            'placeholder': 'Mot de passe'
        })
    )
    password_confirm = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-2 border-2 border-gray-300 rounded-lg',
            'placeholder': 'Confirmer le mot de passe'
        }),
        label='Confirmation mot de passe'
    )
    
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email')
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border-2 border-gray-300 rounded-lg',
                'placeholder': 'Nom d\'utilisateur'
            }),
            'first_name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border-2 border-gray-300 rounded-lg',
                'placeholder': 'Prénom'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border-2 border-gray-300 rounded-lg',
                'placeholder': 'Nom'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'w-full px-4 py-2 border-2 border-gray-300 rounded-lg',
                'placeholder': 'email@example.com'
            }),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')
        
        if password != password_confirm:
            raise forms.ValidationError("Les mots de passe ne correspondent pas")
        
        return cleaned_data
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user


class SearchPatientForm(forms.Form):
    """Formulaire de recherche de patient"""
    
    query = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-2 border rounded',
            'placeholder': 'Rechercher un patient...',
            'autofocus': True,
        })
    )


class FilterConsultationForm(forms.Form):
    """Formulaire de filtrage de consultations"""
    
    statut = forms.ChoiceField(
        choices=[('', 'Tous les statuts')] + Consultation.STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'w-full px-4 py-2 border rounded'})
    )
    medecin = forms.ModelChoiceField(
        queryset=Utilisateur.objects.filter(role='medecin'),
        required=False,
        empty_label="Tous les médecins",
        widget=forms.Select(attrs={'class': 'w-full px-4 py-2 border rounded'})
    )
