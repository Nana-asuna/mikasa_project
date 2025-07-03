#!/usr/bin/env python
"""
Script pour initialiser la base de données avec des données de test sécurisées
Utilisant des noms sénégalais
"""

import os
import sys
import django
from datetime import date, datetime, timedelta
from django.contrib.auth.hashers import make_password

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'orphanage_backend.settings.base')
django.setup()

from django.contrib.auth import get_user_model
from apps.children.models import Child, ChildNote, MedicalRecord
from apps.donations.models import Donation, Donor
from apps.inventory.models import InventoryItem, Category
from apps.families.models import Family, FamilyMember
from apps.core.models import GDPRConsent

# type: ignore[attr-defined]

User = get_user_model()

def create_secure_users():
    """Crée des utilisateurs de test avec des noms sénégalais"""
    print("👤 Création des utilisateurs de test...")
    
    users_data = [
        {
            'username': 'admin_mikasa',
            'email': 'admin@mikasa.sn',
            'password': 'AdminMikasa2024!@#',
            'first_name': 'Ousmane',
            'last_name': 'Diallo',
            'role': 'admin',
            'is_verified': True,
            'status': 'approved'
        },
        {
            'username': 'dr_diop',
            'email': 'aminata.diop@mikasa.sn',
            'password': 'DrDiop2024!@#',
            'first_name': 'Aminata',
            'last_name': 'Diop',
            'role': 'medecin',
            'is_verified': True,
            'status': 'approved',
            'specialization': 'Pédiatrie'
        },
        {
            'username': 'soignant_ba',
            'email': 'mariama.ba@mikasa.sn',
            'password': 'Soignant2024!@#',
            'first_name': 'Mariama',
            'last_name': 'Ba',
            'role': 'soignant',
            'is_verified': True,
            'status': 'approved',
            'specialization': 'Infirmière pédiatrique'
        },
        {
            'username': 'fatou_seck',
            'email': 'fatou.seck@mikasa.sn',
            'password': 'Assistant2024!@#',
            'first_name': 'Fatou',
            'last_name': 'Seck',
            'role': 'assistant_social',
            'is_verified': True,
            'status': 'approved'
        },
        {
            'username': 'ndeye_mbaye',
            'email': 'ndeye.mbaye@mikasa.sn',
            'password': 'Logistique2024!@#',
            'first_name': 'Ndeye',
            'last_name': 'Mbaye',
            'role': 'logisticien',
            'is_verified': True,
            'status': 'approved'
        },
        {
            'username': 'donateur_seck',
            'email': 'moussa.seck@email.sn',
            'password': 'Donateur2024!@#',
            'first_name': 'Moussa',
            'last_name': 'Seck',
            'role': 'donateur',
            'is_verified': True,
            'status': 'approved'
        }
    ]
    
    created_users = {}
    for user_data in users_data:
        user, created = User.objects.get_or_create(
            email=user_data['email'],
            defaults=user_data
        )
        if created:
            user.set_password(user_data['password'])
            user.save()
            print(f"✅ Utilisateur créé: {user.first_name} {user.last_name} ({user.role})")
        else:
            print(f"ℹ️ Utilisateur existant: {user.first_name} {user.last_name}")
        
        created_users[user_data['role']] = user
    
    return created_users

def create_test_children(users):
    
    print("👶 Création des enfants de test...")
    
    children_data = [
        {
            'first_name': 'Saly',
            'last_name': 'Ndiaye',
            'date_of_birth': date(2015, 3, 15),
            'gender': 'F',
            'arrival_date': date(2020, 1, 10),
            'status': 'a_parrainer',
            'case_worker': users['assistant_social'],
            'arrival_reason': 'Famille en difficulté économique',
            'medical_conditions': 'Aucune condition particulière',
            'education_level': 'CE2',
            'nationality': 'Sénégalaise'
        },
        {
            'first_name': 'Ibrahima',
            'last_name': 'Sarr',
            'date_of_birth': date(2012, 7, 22),
            'gender': 'M',
            'arrival_date': date(2019, 6, 5),
            'status': 'parraine',
            'case_worker': users['assistant_social'],
            'arrival_reason': 'Orphelin de père et mère',
            'medical_conditions': 'Asthme léger',
            'education_level': '6ème',
            'nationality': 'Sénégalaise'
        },
        {
            'first_name': 'Aïcha',
            'last_name': 'Thiam',
            'date_of_birth': date(2017, 11, 8),
            'gender': 'F',
            'arrival_date': date(2021, 3, 20),
            'status': 'en_attente',
            'case_worker': users['assistant_social'],
            'arrival_reason': 'Situation familiale complexe',
            'is_confidential': True,
            'confidentiality_reason': 'Protection de l\'enfant - violence domestique',
            'nationality': 'Sénégalaise'
        },
        {
            'first_name': 'Mamadou',
            'last_name': 'Cissé',
            'date_of_birth': date(2014, 5, 12),
            'gender': 'M',
            'arrival_date': date(2020, 8, 15),
            'status': 'a_parrainer',
            'case_worker': users['assistant_social'],
            'arrival_reason': 'Abandon',
            'medical_conditions': 'Malnutrition (récupérée)',
            'education_level': 'CM1',
            'nationality': 'Sénégalaise'
        },
        {
            'first_name': 'Khadija',
            'last_name': 'Diouf',
            'date_of_birth': date(2016, 9, 3),
            'gender': 'F',
            'arrival_date': date(2021, 1, 8),
            'status': 'parraine',
            'case_worker': users['assistant_social'],
            'arrival_reason': 'Décès des parents',
            'medical_conditions': 'Aucune',
            'education_level': 'CP',
            'nationality': 'Sénégalaise'
        },
        {
            'first_name': 'Ousmane',
            'last_name': 'Gueye',
            'date_of_birth': date(2013, 12, 20),
            'gender': 'M',
            'arrival_date': date(2019, 4, 12),
            'status': 'adopte',
            'case_worker': users['assistant_social'],
            'arrival_reason': 'Orphelin',
            'medical_conditions': 'Aucune',
            'education_level': '5ème',
            'nationality': 'Sénégalaise'
        }
    ]
    
    created_children = []
    for child_data in children_data:
        child, created = Child.objects.get_or_create(
            first_name=child_data['first_name'],
            last_name=child_data['last_name'],
            date_of_birth=child_data['date_of_birth'],
            defaults=child_data
        )
        if created:
            print(f"✅ Enfant créé: {child.first_name} {child.last_name} (statut: {child.status})")
            
            # Créer un consentement RGPD
            GDPRConsent.objects.create(
                child=child,
                consent_type='data_processing',
                purpose='Gestion du dossier de l\'enfant',
                legal_basis='Intérêt légitime - protection de l\'enfant',
                granted=True,
                granted_at=datetime.now(),
                ip_address='127.0.0.1',
                user_agent='System/1.0'
            )
            
        else:
            print(f"ℹ️ Enfant existant: {child.first_name} {child.last_name}")
        
        created_children.append(child)
    
    return created_children

def create_medical_records(children, users):
    """Crée des dossiers médicaux de test"""
    print("🏥 Création des dossiers médicaux...")
    
    for child in children[:4]:  # Pour les 4 premiers enfants
        medical_record = MedicalRecord.objects.create(
            child=child,
            visit_date=datetime.now() - timedelta(days=30),
            visit_type='routine',
            doctor_name='Dr Aminata Diop',
            clinic_hospital='Centre Médical Mikasa',
            diagnosis='Bilan de santé normal',
            treatment='Aucun traitement nécessaire',
            height=120.5 + (child.age * 5),  # Taille approximative selon l'âge
            weight=25.0 + (child.age * 2),   # Poids approximatif selon l'âge
            temperature=36.8,
            notes='Enfant en bonne santé générale',
            created_by=users['medecin']
        )
        print(f"✅ Dossier médical créé pour {child.first_name} {child.last_name}")

def create_inventory_items():
    """Crée des éléments d'inventaire de test"""
    print("📦 Création de l'inventaire...")
    
    # Créer des catégories
    categories_data = [
        {'name': 'Alimentation', 'description': 'Produits alimentaires et nutritionnels'},
        {'name': 'Vêtements', 'description': 'Vêtements pour enfants de tous âges'},
        {'name': 'Matériel médical', 'description': 'Équipements et fournitures médicales'},
        {'name': 'Fournitures scolaires', 'description': 'Matériel éducatif et scolaire'},
        {'name': 'Hygiène', 'description': 'Produits d\'hygiène et de soins'}
    ]
    
    categories = {}
    for cat_data in categories_data:
        category, created = Category.objects.get_or_create(
            name=cat_data['name'],
            defaults=cat_data
        )
        categories[cat_data['name']] = category
        if created:
            print(f"✅ Catégorie créée: {category.name}")
    
    # Créer des articles avec des noms locaux
    items_data = [
        {
            'name': 'Céréales Cérélac',
            'category': categories['Alimentation'],
            'quantity': 50,
            'unit': 'boîtes',
            'minimum_threshold': 10,
            'cost_per_unit': 2500  # Prix en FCFA
        },
        {
            'name': 'Lait en poudre Nido',
            'category': categories['Alimentation'],
            'quantity': 30,
            'unit': 'boîtes',
            'minimum_threshold': 8,
            'cost_per_unit': 3500
        },
        {
            'name': 'Uniformes scolaires',
            'category': categories['Vêtements'],
            'quantity': 25,
            'unit': 'pièces',
            'minimum_threshold': 5,
            'cost_per_unit': 5000
        },
        {
            'name': 'Sandales enfants',
            'category': categories['Vêtements'],
            'quantity': 20,
            'unit': 'paires',
            'minimum_threshold': 5,
            'cost_per_unit': 2000
        },
        {
            'name': 'Thermomètres digitaux',
            'category': categories['Matériel médical'],
            'quantity': 5,
            'unit': 'pièces',
            'minimum_threshold': 2,
            'cost_per_unit': 15000
        },
        {
            'name': 'Cahiers d\'écolier',
            'category': categories['Fournitures scolaires'],
            'quantity': 100,
            'unit': 'pièces',
            'minimum_threshold': 20,
            'cost_per_unit': 200
        },
        {
            'name': 'Savon de Marseille',
            'category': categories['Hygiène'],
            'quantity': 40,
            'unit': 'pièces',
            'minimum_threshold': 10,
            'cost_per_unit': 500
        }
    ]
    
    for item_data in items_data:
        item, created = InventoryItem.objects.get_or_create(
            name=item_data['name'],
            defaults=item_data
        )
        if created:
            print(f"✅ Article créé: {item.name} ({item.quantity} {item.unit})")

def create_test_families():
    """Crée des familles d'accueil de test avec des noms sénégalais"""
    print("👨‍👩‍👧‍👦 Création des familles d'accueil...")
    
    families_data = [
        {
            'family_name': 'Famille Diagne',
            'family_type': 'foster',
            'status': 'approved',
            'primary_contact_first_name': 'Abdou',
            'primary_contact_last_name': 'Diagne',
            'primary_contact_email': 'abdou.diagne@email.sn',
            'primary_contact_phone': '+221771234567',
            'secondary_contact_first_name': 'Awa',
            'secondary_contact_last_name': 'Diagne',
            'secondary_contact_email': 'awa.diagne@email.sn',
            'secondary_contact_phone': '+221772345678',
            'address_line1': 'Cité Keur Gorgui, Villa 123',
            'city': 'Dakar',
            'postal_code': '12000',
            'country': 'Sénégal',
            'marital_status': 'married',
            'number_of_children': 2,
            'household_size': 4,
            'max_children_capacity': 2,
            'application_date': date.today() - timedelta(days=180),
            'approval_date': date.today() - timedelta(days=90),
            'background_check_completed': True,
            'home_study_completed': True,
            'references_checked': True,
            'motivation': 'Nous souhaitons offrir un foyer aimant aux enfants dans le besoin'
        },
        {
            'family_name': 'Famille Sy',
            'family_type': 'adoptive',
            'status': 'approved',
            'primary_contact_first_name': 'Cheikh',
            'primary_contact_last_name': 'Sy',
            'primary_contact_email': 'cheikh.sy@email.sn',
            'primary_contact_phone': '+221773456789',
            'secondary_contact_first_name': 'Bineta',
            'secondary_contact_last_name': 'Sy',
            'secondary_contact_email': 'bineta.sy@email.sn',
            'secondary_contact_phone': '+221774567890',
            'address_line1': 'Almadies, Résidence les Palmiers',
            'city': 'Dakar',
            'postal_code': '12500',
            'country': 'Sénégal',
            'marital_status': 'married',
            'number_of_children': 0,
            'household_size': 2,
            'max_children_capacity': 1,
            'application_date': date.today() - timedelta(days=120),
            'approval_date': date.today() - timedelta(days=60),
            'background_check_completed': True,
            'home_study_completed': True,
            'references_checked': True,
            'motivation': 'Nous désirons fonder une famille par l\'adoption'
        }
    ]
    
    for family_data in families_data:
        family, created = Family.objects.get_or_create(
            family_name=family_data['family_name'],
            defaults=family_data
        )
        
        if created:
            print(f"✅ Famille créée: {family.family_name}")
            
            # Ajouter des membres de famille
            if family.family_name == 'Famille Diagne':
                members_data = [
                    {
                        'first_name': 'Abdou',
                        'last_name': 'Diagne',
                        'date_of_birth': date(1980, 5, 15),
                        'relationship': 'parent',
                        'occupation': 'Enseignant'
                    },
                    {
                        'first_name': 'Awa',
                        'last_name': 'Diagne',
                        'date_of_birth': date(1982, 8, 22),
                        'relationship': 'parent',
                        'occupation': 'Infirmière'
                    }
                ]
            else:  # Famille Sy
                members_data = [
                    {
                        'first_name': 'Cheikh',
                        'last_name': 'Sy',
                        'date_of_birth': date(1978, 3, 10),
                        'relationship': 'parent',
                        'occupation': 'Ingénieur'
                    },
                    {
                        'first_name': 'Bineta',
                        'last_name': 'Sy',
                        'date_of_birth': date(1980, 11, 25),
                        'relationship': 'parent',
                        'occupation': 'Comptable'
                    }
                ]
            
            for member_data in members_data:
                member_data['family'] = family
                FamilyMember.objects.create(**member_data)
                print(f"✅ Membre ajouté: {member_data['first_name']} {member_data['last_name']}")

def main():
    """Fonction principale pour initialiser les données de test"""
    print("🌱 Initialisation des données de test - Organisation Mikasa")
    print("=" * 60)
    
    try:
        # Créer les utilisateurs
        users = create_secure_users()
        
        # Créer les enfants
        children = create_test_children(users)
        
        # Créer les dossiers médicaux
        create_medical_records(children, users)
        
        # Créer l'inventaire
        create_inventory_items()
        
        # Créer les familles
        create_test_families()
        
        print("=" * 60)
        print("✅ Initialisation terminée avec succès!")
        print("")
        print("🔐 COMPTES DE TEST CRÉÉS:")
        print("Admin: admin@mikasa.sn / AdminMikasa2024!@#")
        print("Dr Diop: aminata.diop@mikasa.sn / DrDiop2024!@#")
        print("Soignant: mariama.ba@mikasa.sn / Soignant2024!@#")
        print("Assistant: fatou.seck@mikasa.sn / Assistant2024!@#")
        print("Logisticien: ndeye.mbaye@mikasa.sn / Logistique2024!@#")
        print("Donateur: moussa.fall@email.sn / Donateur2024!@#")
        print("")
        print("👶 ENFANTS CRÉÉS:")
        print("- Saly Ndiaye (8 ans, F) - À parrainer")
        print("- Ibrahima Sarr (11 ans, M) - Parrainé")
        print("- Aïcha Thiam (6 ans, F) - En attente (confidentiel)")
        print("- Mamadou Cissé (9 ans, M) - À parrainer")
        print("- Khadija Diouf (7 ans, F) - Parrainée")
        print("- Ousmane Gueye (10 ans, M) - Adopté")
        print("")
        print("⚠️ IMPORTANT: Changez ces mots de passe en production!")
        
    except Exception as e:
        print(f"❌ Erreur lors de l'initialisation: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main()
