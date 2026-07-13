"""
Views pour Saint Joseph - Système de Gestion Hospitalier
Django MVT Architecture
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from django.db.models import Q
from datetime import timedelta
import logging

from .models import (
    Utilisateur, Patient, DossierMedical, Consultation,
    Diagnostic, Prescription, Formulaire, RendezVous,
    Hospitalisation, Archive
)
from .forms import (
    UserForm, UtilisateurForm, PatientForm, ConsultationForm,
    DiagnosticForm, PrescriptionForm, FormulaireForm, RendezVousForm,
    HospitalisationForm, ArchiveForm, SearchPatientForm, FilterConsultationForm
)
from .decorators import role_required, admin_required, medecin_required, infirmier_required

logger = logging.getLogger(__name__)


# ============================================================================
# AUTHENTICATION VIEWS
# ============================================================================

@require_http_methods(["GET", "POST"])
def user_login(request):
    """Vue de connexion utilisateur"""
    if request.user.is_authenticated:
        return redirect('saint_joseph:dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            logger.info(f"Utilisateur {username} connecté")
            messages.success(request, f"Bienvenue {user.get_full_name()}")
            return redirect('saint_joseph:dashboard')
        else:
            logger.warning(f"Tentative de connexion échouée pour {username}")
            messages.error(request, "Nom d'utilisateur ou mot de passe incorrect")
    
    return render(request, 'saint_joseph/auth/login.html')


@login_required(login_url='login')
def user_logout(request):
    """Vue de déconnexion"""
    logger.info(f"Utilisateur {request.user.username} déconnecté")
    logout(request)
    messages.success(request, "Vous avez été déconnecté")
    return redirect('login')


@require_http_methods(["GET", "POST"])
def user_register(request):
    """Vue d'inscription - Admin uniquement"""
    if request.user.is_authenticated:
        try:
            if request.user.profil_utilisateur.role != 'admin':
                messages.error(request, "Seuls les administrateurs peuvent créer des comptes")
                return redirect('saint_joseph:dashboard')
        except:
            messages.error(request, "Seuls les administrateurs peuvent créer des comptes")
            return redirect('saint_joseph:dashboard')
    
    if request.method == 'POST':
        user_form = UserForm(request.POST)
        if user_form.is_valid():
            user = user_form.save()
            Utilisateur.objects.get_or_create(user=user, defaults={'role': 'patient'})
            logger.info(f"Nouvel utilisateur créé: {user.username}")
            messages.success(request, "Compte créé avec succès")
            return redirect('login')
        else:
            for field, errors in user_form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        user_form = UserForm()
    
    return render(request, 'saint_joseph/auth/register.html', {'form': user_form})


# ============================================================================
# DASHBOARD VIEW
# ============================================================================

@login_required(login_url='login')
def dashboard(request):
    """Vue du tableau de bord principal"""
    
    # Statistiques générales
    today = timezone.now().date()
    context = {
        'total_patients': Patient.objects.count(),
        'consultations_today': Consultation.objects.filter(
            date_consultation__date=today
        ).count(),
        'rdv_prevus': RendezVous.objects.filter(
            date_heure__gte=timezone.now(),
            statut__in=['planifie', 'confirme']
        ).count(),
        'hospitalisees': Hospitalisation.objects.filter(
            statut__in=['admission', 'hospitalisee'],
            date_sortie__isnull=True
        ).count(),
        'recent_consultations': Consultation.objects.select_related(
            'dossier_medical__patient__utilisateur__user',
            'medecin__user'
        ).order_by('-date_consultation')[:5],
        'upcoming_appointments': RendezVous.objects.select_related(
            'patient__utilisateur__user',
            'medecin__user'
        ).filter(
            date_heure__gte=timezone.now(),
            statut__in=['planifie', 'confirme']
        ).order_by('date_heure')[:5],
    }
    
    return render(request, 'saint_joseph/dashboard.html', context)


# ============================================================================
# PATIENT VIEWS
# ============================================================================

@login_required(login_url='login')
@role_required('medecin', 'infirmier', 'admin')
def patient_list(request):
    """Liste des patients avec recherche"""
    patients = Patient.objects.select_related('utilisateur__user').all()
    
    # Recherche
    search_form = SearchPatientForm(request.GET)
    if search_form.is_valid() and search_form.cleaned_data.get('query'):
        query = search_form.cleaned_data['query']
        patients = patients.filter(
            Q(numero_patient__icontains=query) |
            Q(utilisateur__user__first_name__icontains=query) |
            Q(utilisateur__user__last_name__icontains=query) |
            Q(email__icontains=query)
        )
    
    # Pagination
    from django.core.paginator import Paginator
    paginator = Paginator(patients, 20)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_form': search_form,
    }
    return render(request, 'saint_joseph/patients/list.html', context)


@login_required(login_url='login')
@role_required('medecin', 'infirmier', 'admin')
def patient_create(request):
    """Créer un nouveau patient"""
    if request.method == 'POST':
        patient_form = PatientForm(request.POST)
        
        if patient_form.is_valid():
            # Générer username automatiquement depuis email
            email = patient_form.cleaned_data.get('email')
            first_name = request.POST.get('first_name', '')
            last_name = request.POST.get('last_name', '')
            
            # Créer un username unique
            import uuid
            username = f"pat_{uuid.uuid4().hex[:8]}"
            
            # Créer l'utilisateur automatiquement
            user = User.objects.create_user(
                username=username,
                email=email,
                first_name=first_name,
                last_name=last_name,
                password=uuid.uuid4().hex[:12]  # Mot de passe temporaire
            )
            
            utilisateur, created = Utilisateur.objects.get_or_create(
                user=user,
                defaults={'role': 'patient'}
            )
            
            patient = patient_form.save(commit=False)
            patient.utilisateur = utilisateur
            patient.save()
            
            # Créer le dossier médical automatiquement
            numero_dossier = f"DM-{patient.id:06d}"
            DossierMedical.objects.create(
                patient=patient,
                numero_dossier=numero_dossier
            )
            
            logger.info(f"Patient créé: {patient.numero_patient}")
            messages.success(request, f"Patient {patient.numero_patient} créé avec succès")
            return redirect('saint_joseph:patient_list')
        else:
            for field, errors in patient_form.errors.items():
                for error in errors:
                    messages.error(request, f"Patient - {field}: {error}")
    else:
        patient_form = PatientForm()
    
    context = {
        'patient_form': patient_form,
        'title': 'Créer un nouveau patient'
    }
    return render(request, 'saint_joseph/patients/form.html', context)


@login_required(login_url='login')
@role_required('medecin', 'infirmier', 'admin')
def patient_detail(request, pk):
    """Détails d'un patient"""
    patient = get_object_or_404(Patient, pk=pk)
    dossier = patient.dossier_medical
    consultations = dossier.consultations.all().order_by('-date_consultation')
    
    context = {
        'patient': patient,
        'dossier': dossier,
        'consultations': consultations,
    }
    return render(request, 'saint_joseph/patients/detail.html', context)


@login_required(login_url='login')
@role_required('medecin', 'infirmier', 'admin')
def patient_print(request, pk):
    """Imprimer les informations d'un patient"""
    patient = get_object_or_404(Patient, pk=pk)
    dossier = getattr(patient, 'dossier_medical', None)
    consultations = dossier.consultations.all().order_by('-date_consultation') if dossier else []
    
    context = {
        'patient': patient,
        'dossier': dossier,
        'consultations': consultations,
        'current_time': timezone.now(),
    }
    return render(request, 'saint_joseph/patients/print.html', context)


@login_required(login_url='login')
@role_required('medecin', 'infirmier', 'admin')
def patient_edit(request, pk):
    """Modifier un patient"""
    patient = get_object_or_404(Patient, pk=pk)
    
    if request.method == 'POST':
        form = PatientForm(request.POST, instance=patient)
        if form.is_valid():
            patient = form.save()
            
            # Mettre à jour l'utilisateur lié (first_name et last_name)
            user = patient.utilisateur.user
            user.first_name = request.POST.get('first_name', '')
            user.last_name = request.POST.get('last_name', '')
            user.save()
            
            logger.info(f"Patient modifié: {patient.numero_patient}")
            messages.success(request, "Patient modifié avec succès")
            return redirect('saint_joseph:patient_detail', pk=pk)
        else:
            messages.error(request, "Erreur lors de la modification")
    else:
        form = PatientForm(instance=patient)
    
    context = {
        'patient_form': form,
        'patient': patient,
        'title': f'Modifier {patient.numero_patient}',
        'is_edit': True
    }
    return render(request, 'saint_joseph/patients/form.html', context)


@login_required(login_url='login')
@admin_required
def patient_delete(request, pk):
    """Supprimer un patient"""
    patient = get_object_or_404(Patient, pk=pk)
    
    if request.method == 'POST':
        numero = patient.numero_patient
        patient.delete()
        logger.info(f"Patient supprimé: {numero}")
        messages.success(request, f"Patient {numero} supprimé")
        return redirect('saint_joseph:patient_list')
    
    context = {'patient': patient}
    return render(request, 'saint_joseph/patients/confirm_delete.html', context)


# ============================================================================
# CONSULTATION VIEWS
# ============================================================================

@login_required(login_url='login')
@role_required('medecin', 'admin')
def consultation_list(request):
    """Liste des consultations"""
    consultations = Consultation.objects.select_related(
        'dossier_medical__patient',
        'medecin__user'
    ).order_by('-date_consultation')
    
    # Filtrage
    filter_form = FilterConsultationForm(request.GET)
    if filter_form.is_valid():
        if filter_form.cleaned_data.get('statut'):
            consultations = consultations.filter(statut=filter_form.cleaned_data['statut'])
        if filter_form.cleaned_data.get('medecin'):
            consultations = consultations.filter(medecin=filter_form.cleaned_data['medecin'])
    
    # Pagination
    from django.core.paginator import Paginator
    paginator = Paginator(consultations, 20)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'filter_form': filter_form,
    }
    return render(request, 'saint_joseph/consultations/list.html', context)


@login_required(login_url='login')
@role_required('medecin', 'admin')
def consultation_create(request):
    """Créer une consultation"""
    if request.method == 'POST':
        form = ConsultationForm(request.POST)
        if form.is_valid():
            consultation = form.save()
            logger.info(f"Consultation créée: {consultation.id}")
            messages.success(request, "Consultation créée avec succès")
            return redirect('saint_joseph:consultation_detail', pk=consultation.id)
        else:
            messages.error(request, "Erreur lors de la création")
    else:
        form = ConsultationForm()
    
    context = {
        'form': form,
        'title': 'Créer une consultation'
    }
    return render(request, 'saint_joseph/consultations/form.html', context)


@login_required(login_url='login')
@role_required('medecin', 'infirmier', 'admin')
def consultation_detail(request, pk):
    """Détails de la consultation"""
    consultation = get_object_or_404(Consultation, pk=pk)
    diagnostics = consultation.diagnostics.all()
    prescriptions = consultation.prescriptions.all()
    formulaires = consultation.formulaires.all()
    
    context = {
        'consultation': consultation,
        'diagnostics': diagnostics,
        'prescriptions': prescriptions,
        'formulaires': formulaires,
    }
    return render(request, 'saint_joseph/consultations/detail.html', context)


@login_required(login_url='login')
@role_required('medecin', 'infirmier', 'admin')
def consultation_print(request, pk):
    """Imprimer les éléments d'une consultation (diagnostic, prescription ou complet)"""
    consultation = get_object_or_404(Consultation, pk=pk)
    print_type = request.GET.get('type', 'all')
    
    patient = consultation.dossier_medical.patient
    diagnostics = consultation.diagnostics.all()
    prescriptions = consultation.prescriptions.all()
    
    context = {
        'consultation': consultation,
        'patient': patient,
        'diagnostics': diagnostics,
        'prescriptions': prescriptions,
        'print_type': print_type,
        'current_time': timezone.now(),
    }
    return render(request, 'saint_joseph/consultations/print.html', context)


@login_required(login_url='login')
@role_required('medecin', 'admin')
def consultation_edit(request, pk):
    """Modifier une consultation"""
    consultation = get_object_or_404(Consultation, pk=pk)
    
    if request.method == 'POST':
        form = ConsultationForm(request.POST, instance=consultation)
        if form.is_valid():
            form.save()
            logger.info(f"Consultation modifiée: {pk}")
            messages.success(request, "Consultation modifiée")
            return redirect('saint_joseph:consultation_detail', pk=pk)
    else:
        form = ConsultationForm(instance=consultation)
    
    context = {
        'form': form,
        'consultation': consultation,
        'title': 'Modifier consultation',
        'is_edit': True
    }
    return render(request, 'saint_joseph/consultations/form.html', context)


# ============================================================================
# DIAGNOSTIC VIEWS
# ============================================================================

@login_required(login_url='login')
@role_required('medecin', 'admin')
def diagnostic_create(request, consultation_id):
    """Ajouter un diagnostic à une consultation"""
    consultation = get_object_or_404(Consultation, pk=consultation_id)
    
    if request.method == 'POST':
        form = DiagnosticForm(request.POST)
        if form.is_valid():
            diagnostic = form.save()
            logger.info(f"Diagnostic créé pour consultation {consultation_id}")
            messages.success(request, "Diagnostic ajouté")
            return redirect('saint_joseph:consultation_detail', pk=consultation_id)
    else:
        form = DiagnosticForm(initial={'consultation': consultation})
    
    context = {
        'form': form,
        'consultation': consultation,
        'title': 'Ajouter un diagnostic'
    }
    return render(request, 'saint_joseph/diagnostics/form.html', context)


# ============================================================================
# PRESCRIPTION VIEWS
# ============================================================================

@login_required(login_url='login')
@role_required('medecin', 'admin')
def prescription_create(request, consultation_id):
    """Ajouter une prescription"""
    consultation = get_object_or_404(Consultation, pk=consultation_id)
    
    if request.method == 'POST':
        form = PrescriptionForm(request.POST)
        if form.is_valid():
            prescription = form.save()
            logger.info(f"Prescription créée pour consultation {consultation_id}")
            messages.success(request, "Prescription ajoutée")
            return redirect('saint_joseph:consultation_detail', pk=consultation_id)
    else:
        form = PrescriptionForm(initial={'consultation': consultation})
    
    context = {
        'form': form,
        'consultation': consultation,
        'title': 'Ajouter une prescription'
    }
    return render(request, 'saint_joseph/prescriptions/form.html', context)


# ============================================================================
# FORMULAIRE VIEWS
# ============================================================================

@login_required(login_url='login')
@role_required('medecin', 'infirmier', 'admin')
def formulaire_list(request):
    """Liste des formulaires"""
    formulaires = Formulaire.objects.select_related(
        'consultation__dossier_medical__patient'
    ).order_by('-date_creation')
    
    # Pagination
    from django.core.paginator import Paginator
    paginator = Paginator(formulaires, 20)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    context = {'page_obj': page_obj}
    return render(request, 'saint_joseph/formulaires/list.html', context)


@login_required(login_url='login')
@role_required('medecin', 'admin')
def formulaire_create(request, consultation_id):
    """Créer un formulaire"""
    consultation = get_object_or_404(Consultation, pk=consultation_id)
    
    if request.method == 'POST':
        form = FormulaireForm(request.POST)
        if form.is_valid():
            formulaire = form.save()
            logger.info(f"Formulaire créé pour consultation {consultation_id}")
            messages.success(request, "Formulaire créé")
            return redirect('saint_joseph:formulaire_detail', pk=formulaire.id)
    else:
        form = FormulaireForm(initial={'consultation': consultation})
    
    context = {
        'form': form,
        'consultation': consultation,
        'title': 'Créer un formulaire'
    }
    return render(request, 'saint_joseph/formulaires/form.html', context)


@login_required(login_url='login')
@role_required('medecin', 'infirmier', 'admin')
def formulaire_detail(request, pk):
    """Détails d'un formulaire"""
    formulaire = get_object_or_404(Formulaire, pk=pk)
    context = {'formulaire': formulaire}
    return render(request, 'saint_joseph/formulaires/detail.html', context)


@login_required(login_url='login')
@role_required('medecin', 'admin')
def formulaire_edit(request, pk):
    """Modifier un formulaire"""
    formulaire = get_object_or_404(Formulaire, pk=pk)
    
    if request.method == 'POST':
        form = FormulaireForm(request.POST, instance=formulaire)
        if form.is_valid():
            form.save()
            messages.success(request, "Formulaire modifié")
            return redirect('saint_joseph:formulaire_detail', pk=pk)
    else:
        form = FormulaireForm(instance=formulaire)
    
    context = {
        'form': form,
        'formulaire': formulaire,
        'is_edit': True
    }
    return render(request, 'saint_joseph/formulaires/form.html', context)


@login_required(login_url='login')
@role_required('medecin', 'infirmier', 'admin')
def formulaire_print(request, pk):
    """Imprimer un formulaire"""
    formulaire = get_object_or_404(Formulaire, pk=pk)
    context = {'formulaire': formulaire}
    return render(request, 'saint_joseph/formulaires/print.html', context)


@login_required(login_url='login')
@role_required('medecin', 'admin')
def dossier_archive(request, pk):
    """Archiver un dossier médical"""
    dossier = get_object_or_404(DossierMedical, pk=pk)
    
    if request.method == 'POST':
        motif = request.POST.get('motif_archivage')
        dossier.est_actif = False
        dossier.save()
        
        try:
            archiviste = request.user.profil_utilisateur
        except Exception:
            from .models import Utilisateur
            archiviste, created = Utilisateur.objects.get_or_create(
                user=request.user,
                defaults={'role': 'patient'}
            )
        
        # Enregistrer l'archive
        Archive.objects.create(
            dossier_medical=dossier,
            motif_archivage=motif,
            archiviste=archiviste
        )
        
        logger.info(f"Dossier médical archivé: {dossier.numero_dossier}")
        messages.success(request, f"Dossier médical {dossier.numero_dossier} archivé")
        return redirect('saint_joseph:dossier_list')
    
    context = {'dossier': dossier}
    return render(request, 'saint_joseph/dossiers/archive_confirm.html', context)


# ============================================================================
# RENDEZ-VOUS VIEWS
# ============================================================================

@login_required(login_url='login')
@role_required('medecin', 'infirmier', 'admin')
def rendez_vous_list(request):
    """Liste des rendez-vous"""
    rdv = RendezVous.objects.select_related(
        'patient__utilisateur__user',
        'medecin__user'
    ).order_by('-date_heure')
    
    # Pagination
    from django.core.paginator import Paginator
    paginator = Paginator(rdv, 20)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    context = {'page_obj': page_obj}
    return render(request, 'saint_joseph/rendez_vous/list.html', context)


@login_required(login_url='login')
@role_required('medecin', 'infirmier', 'admin')
def rendez_vous_create(request):
    """Créer un rendez-vous"""
    if request.method == 'POST':
        form = RendezVousForm(request.POST)
        if form.is_valid():
            rdv = form.save()
            logger.info(f"Rendez-vous créé: {rdv.id}")
            messages.success(request, "Rendez-vous créé")
            return redirect('saint_joseph:rendez_vous_list')
    else:
        form = RendezVousForm()
    
    context = {
        'form': form,
        'title': 'Créer un rendez-vous'
    }
    return render(request, 'saint_joseph/rendez_vous/form.html', context)


@login_required(login_url='login')
@role_required('medecin', 'infirmier', 'admin')
def rendez_vous_detail(request, pk):
    """Détails d'un rendez-vous"""
    rdv = get_object_or_404(RendezVous, pk=pk)
    context = {'rdv': rdv}
    return render(request, 'saint_joseph/rendez_vous/detail.html', context)


@login_required(login_url='login')
@role_required('medecin', 'infirmier', 'admin')
def rendez_vous_edit(request, pk):
    """Modifier un rendez-vous"""
    rdv = get_object_or_404(RendezVous, pk=pk)
    
    if request.method == 'POST':
        form = RendezVousForm(request.POST, instance=rdv)
        if form.is_valid():
            form.save()
            messages.success(request, "Rendez-vous modifié")
            return redirect('saint_joseph:rendez_vous_detail', pk=pk)
    else:
        form = RendezVousForm(instance=rdv)
    
    context = {
        'form': form,
        'rdv': rdv,
        'is_edit': True
    }
    return render(request, 'saint_joseph/rendez_vous/form.html', context)


@login_required(login_url='login')
@role_required('medecin', 'infirmier', 'admin')
def rendez_vous_cancel(request, pk):
    """Annuler un rendez-vous"""
    rdv = get_object_or_404(RendezVous, pk=pk)
    
    if request.method == 'POST':
        rdv.statut = 'annule'
        rdv.save()
        logger.info(f"Rendez-vous annulé: {pk}")
        messages.success(request, "Rendez-vous annulé")
        return redirect('saint_joseph:rendez_vous_list')
    
    context = {'rdv': rdv}
    return render(request, 'saint_joseph/rendez_vous/cancel_confirm.html', context)


# ============================================================================
# HOSPITALISATION VIEWS
# ============================================================================

@login_required(login_url='login')
@role_required('medecin', 'infirmier', 'admin')
def hospitalisation_list(request):
    """Liste des hospitalisations"""
    hospitalisations = Hospitalisation.objects.select_related(
        'patient__utilisateur__user',
        'medecin_responsable__user'
    ).order_by('-date_admission')
    
    # Pagination
    from django.core.paginator import Paginator
    paginator = Paginator(hospitalisations, 20)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    context = {'page_obj': page_obj}
    return render(request, 'saint_joseph/hospitalisations/list.html', context)


@login_required(login_url='login')
@role_required('medecin', 'admin')
def hospitalisation_create(request):
    """Créer une hospitalisation"""
    if request.method == 'POST':
        form = HospitalisationForm(request.POST)
        if form.is_valid():
            hospitalisation = form.save()
            logger.info(f"Hospitalisation créée: {hospitalisation.id}")
            messages.success(request, "Hospitalisation créée")
            return redirect('saint_joseph:hospitalisation_detail', pk=hospitalisation.id)
    else:
        form = HospitalisationForm()
    
    context = {
        'form': form,
        'title': 'Créer une hospitalisation'
    }
    return render(request, 'saint_joseph/hospitalisations/form.html', context)


@login_required(login_url='login')
@role_required('medecin', 'infirmier', 'admin')
def hospitalisation_detail(request, pk):
    """Détails d'une hospitalisation"""
    hospitalisation = get_object_or_404(Hospitalisation, pk=pk)
    context = {'hospitalisation': hospitalisation}
    return render(request, 'saint_joseph/hospitalisations/detail.html', context)


@login_required(login_url='login')
@role_required('medecin', 'admin')
def hospitalisation_edit(request, pk):
    """Modifier une hospitalisation"""
    hospitalisation = get_object_or_404(Hospitalisation, pk=pk)
    
    if request.method == 'POST':
        form = HospitalisationForm(request.POST, instance=hospitalisation)
        if form.is_valid():
            form.save()
            messages.success(request, "Hospitalisation modifiée")
            return redirect('saint_joseph:hospitalisation_detail', pk=pk)
    else:
        form = HospitalisationForm(instance=hospitalisation)
    
    context = {
        'form': form,
        'hospitalisation': hospitalisation,
        'is_edit': True
    }
    return render(request, 'saint_joseph/hospitalisations/form.html', context)


@login_required(login_url='login')
@role_required('medecin', 'admin')
def hospitalisation_discharge(request, pk):
    """Sortir un patient de l'hôpital"""
    hospitalisation = get_object_or_404(Hospitalisation, pk=pk)
    
    if request.method == 'POST':
        hospitalisation.date_sortie = timezone.now()
        hospitalisation.statut = 'sortie'
        hospitalisation.save()
        logger.info(f"Patient sorti: {pk}")
        messages.success(request, "Patient sorti de l'hôpital")
        return redirect('saint_joseph:hospitalisation_list')
    
    context = {'hospitalisation': hospitalisation}
    return render(request, 'saint_joseph/hospitalisations/discharge_confirm.html', context)


# ============================================================================
# DOSSIER MEDICAL VIEWS
# ============================================================================

@login_required(login_url='login')
@role_required('medecin', 'infirmier', 'admin')
def dossier_list(request):
    """Liste des dossiers médicaux"""
    dossiers = DossierMedical.objects.select_related(
        'patient__utilisateur__user'
    ).order_by('-date_ouverture')
    
    # Pagination
    from django.core.paginator import Paginator
    paginator = Paginator(dossiers, 20)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    context = {'page_obj': page_obj}
    return render(request, 'saint_joseph/dossiers/list.html', context)


@login_required(login_url='login')
@role_required('medecin', 'infirmier', 'admin')
def dossier_detail(request, patient_id):
    """Détails d'un dossier médical"""
    patient = get_object_or_404(Patient, pk=patient_id)
    dossier = patient.dossier_medical
    
    context = {
        'patient': patient,
        'dossier': dossier,
        'consultations': dossier.consultations.all().order_by('-date_consultation'),
    }
    return render(request, 'saint_joseph/dossiers/detail.html', context)


# ============================================================================
# ARCHIVE VIEWS
# ============================================================================

@login_required(login_url='login')
@role_required('medecin', 'admin')
def archive_list(request):
    """Liste des archives"""
    archives = Archive.objects.select_related(
        'dossier_medical__patient__utilisateur__user',
        'archiviste__user'
    ).order_by('-date_archivage')
    
    # Pagination
    from django.core.paginator import Paginator
    paginator = Paginator(archives, 20)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    context = {'page_obj': page_obj}
    return render(request, 'saint_joseph/archives/list.html', context)


# ============================================================================
# USER PROFILE VIEWS
# ============================================================================

@login_required(login_url='login')
def user_profile(request):
    """Voir le profil de l'utilisateur"""
    try:
        utilisateur = request.user.profil_utilisateur
    except:
        from .models import Utilisateur
        utilisateur, created = Utilisateur.objects.get_or_create(
            user=request.user,
            defaults={'role': 'patient'}
        )
        logger.warning(f"Profil utilisateur créé automatiquement pour {request.user.username}")
    
    context = {'utilisateur': utilisateur}
    return render(request, 'saint_joseph/profile/view.html', context)


@login_required(login_url='login')
def user_profile_edit(request):
    """Modifier le profil de l'utilisateur"""
    try:
        utilisateur = request.user.profil_utilisateur
    except:
        from .models import Utilisateur
        utilisateur, created = Utilisateur.objects.get_or_create(
            user=request.user,
            defaults={'role': 'patient'}
        )
        logger.warning(f"Profil utilisateur créé automatiquement pour {request.user.username}")
    
    if request.method == 'POST':
        form = UtilisateurForm(request.POST, instance=utilisateur)
        if form.is_valid():
            form.save()
            messages.success(request, "Profil modifié avec succès")
            return redirect('saint_joseph:user_profile')
    else:
        form = UtilisateurForm(instance=utilisateur)
    
    context = {
        'form': form,
        'utilisateur': utilisateur,
    }
    return render(request, 'saint_joseph/profile/edit.html', context)
