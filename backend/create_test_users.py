#!/usr/bin/env python
import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'orphanage_backend.settings.base')
django.setup()

from apps.accounts.models import User
from django.contrib.auth.hashers import make_password

def create_test_users():
    """Crée les comptes de test pour l'application"""
    
    # Liste des utilisateurs de test
    test_users = [
        {
            'email': 'nanayaguediame@gmail.com',
            'password': 'nana',
            'first_name': 'Admin',
            'last_name': 'diame',
            'role': 'admin',
            'status': 'approved',
            'is_verified': True,
            'is_staff': True,
            'is_superuser': True
        },
        {
            'email': 'dr.sall@orphelinat.com',
            'password': 'admin123',
            'first_name': 'Dr',
            'last_name': 'Sall',
            'role': 'medecin',
            'status': 'approved',
            'is_verified': True
        },
        {
            'email': 'soignant.maryama@orphelinat.com',
            'password': 'admin123',
            'first_name': 'Maryama',
            'last_name': 'Diokh',
            'role': 'soignant',
            'status': 'approved',
            'is_verified': True
        },
        {
            'email': 'assistant.mimi@orphelinat.com',
            'password': 'admin123',
            'first_name': 'Mimi',
            'last_name': 'Dabo',
            'role': 'assistant_social',
            'status': 'approved',
            'is_verified': True
        },
        {
            'email': 'logisticien.awa@orphelinat.com',
            'password': 'admin123',
            'first_name': 'Awa',
            'last_name': 'Ndiaye',
            'role': 'logisticien',
            'status': 'approved',
            'is_verified': True
        },
        {
            'email': 'donateur.adjaratou@example.com',
            'password': 'admin123',
            'first_name': 'Adjaratou',
            'last_name': 'Diop',
            'role': 'donateur',
            'status': 'approved',
            'is_verified': True
        }
    ]
    
    created_count = 0
    updated_count = 0
    
    for user_data in test_users:
        email = user_data['email']
        password = user_data.pop('password')
        user_data['username'] = email.split('@')[0]  # Ajoute un username unique
        
        # Vérifier si l'utilisateur existe déjà
        user, created = User.objects.get_or_create(
            email=email,
            defaults=user_data
        )
        
        if created:
            # Nouvel utilisateur créé
            user.set_password(password)
            user.save()
            print(f"✅ Utilisateur créé : {email} ({user_data['role']})")
            created_count += 1
        else:
            # Utilisateur existant, mettre à jour le mot de passe
            user.set_password(password)
            user.save()
            print(f"🔄 Mot de passe mis à jour : {email} ({user_data['role']})")
            updated_count += 1
    
    print(f"\n📊 Résumé :")
    print(f"   - {created_count} utilisateurs créés")
    print(f"   - {updated_count} utilisateurs mis à jour")
    print(f"   - Total : {created_count + updated_count} utilisateurs")
    
    print(f"\n🔑 Comptes de test disponibles :")
    test_accounts = [
        {'email': 'nanayaguediame@gmail.com', 'password': 'nana', 'role': 'admin'},
        {'email': 'dr.sall@orphelinat.com', 'password': 'admin123', 'role': 'medecin'},
        {'email': 'soignant.maryama@orphelinat.com', 'password': 'admin123', 'role': 'soignant'},
        {'email': 'assistant.mimi@orphelinat.com', 'password': 'admin123', 'role': 'assistant_social'},
        {'email': 'logisticien.awa@orphelinat.com', 'password': 'admin123', 'role': 'logisticien'},
        {'email': 'donateur.adjaratou@example.com', 'password': 'admin123', 'role': 'donateur'}
    ]
    for account in test_accounts:
        print(f"   - {account['email']} / {account['password']} ({account['role']})")

if __name__ == '__main__':
    print("🚀 Création des comptes de test...")
    create_test_users()
    print("\n✅ Terminé !") 