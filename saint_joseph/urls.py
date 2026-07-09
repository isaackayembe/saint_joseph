"""
URL Configuration pour Saint Joseph App
"""

from django.urls import path
from . import views

app_name = 'saint_joseph'

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='dashboard'),
    
    # Authentification
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('register/', views.user_register, name='register'),
    
    # Patients
    path('patients/', views.patient_list, name='patient_list'),
    path('patients/create/', views.patient_create, name='patient_create'),
    path('patients/<int:pk>/', views.patient_detail, name='patient_detail'),
    path('patients/<int:pk>/edit/', views.patient_edit, name='patient_edit'),
    path('patients/<int:pk>/delete/', views.patient_delete, name='patient_delete'),
    
    # Consultations
    path('consultations/', views.consultation_list, name='consultation_list'),
    path('consultations/create/', views.consultation_create, name='consultation_create'),
    path('consultations/<int:pk>/', views.consultation_detail, name='consultation_detail'),
    path('consultations/<int:pk>/edit/', views.consultation_edit, name='consultation_edit'),
    
    # Diagnostics
    path('diagnostics/create/<int:consultation_id>/', views.diagnostic_create, name='diagnostic_create'),
    
    # Prescriptions
    path('prescriptions/create/<int:consultation_id>/', views.prescription_create, name='prescription_create'),
    
    # Formulaires
    path('formulaires/', views.formulaire_list, name='formulaire_list'),
    path('formulaires/create/<int:consultation_id>/', views.formulaire_create, name='formulaire_create'),
    path('formulaires/<int:pk>/', views.formulaire_detail, name='formulaire_detail'),
    path('formulaires/<int:pk>/edit/', views.formulaire_edit, name='formulaire_edit'),
    path('formulaires/<int:pk>/print/', views.formulaire_print, name='formulaire_print'),
    path('formulaires/<int:pk>/archive/', views.formulaire_archive, name='formulaire_archive'),
    
    # Rendez-vous
    path('rendez-vous/', views.rendez_vous_list, name='rendez_vous_list'),
    path('rendez-vous/create/', views.rendez_vous_create, name='rendez_vous_create'),
    path('rendez-vous/<int:pk>/', views.rendez_vous_detail, name='rendez_vous_detail'),
    path('rendez-vous/<int:pk>/edit/', views.rendez_vous_edit, name='rendez_vous_edit'),
    path('rendez-vous/<int:pk>/cancel/', views.rendez_vous_cancel, name='rendez_vous_cancel'),
    
    # Hospitalisations
    path('hospitalisations/', views.hospitalisation_list, name='hospitalisation_list'),
    path('hospitalisations/create/', views.hospitalisation_create, name='hospitalisation_create'),
    path('hospitalisations/<int:pk>/', views.hospitalisation_detail, name='hospitalisation_detail'),
    path('hospitalisations/<int:pk>/edit/', views.hospitalisation_edit, name='hospitalisation_edit'),
    path('hospitalisations/<int:pk>/discharge/', views.hospitalisation_discharge, name='hospitalisation_discharge'),
    
    # Dossiers Médicaux
    path('dossiers/', views.dossier_list, name='dossier_list'),
    path('dossiers/<int:patient_id>/', views.dossier_detail, name='dossier_detail'),
    
    # Archives
    path('archives/', views.archive_list, name='archive_list'),
    
    # Profil
    path('profil/', views.user_profile, name='user_profile'),
    path('profil/edit/', views.user_profile_edit, name='user_profile_edit'),
]
