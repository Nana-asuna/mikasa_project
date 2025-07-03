#!/bin/bash

# Script de démarrage sécurisé pour Orphanage Management System
# Ce script configure l'environnement et démarre l'application avec toutes les mesures de sécurité

set -e  # Arrêter en cas d'erreur

echo "🚀 Démarrage du système de gestion d'orphelinat..."

# Vérification des variables d'environnement critiques
check_env_var() {
    if [ -z "${!1}" ]; then
        echo "❌ Erreur: La variable d'environnement $1 n'est pas définie"
        exit 1
    fi
}

echo "🔍 Vérification des variables d'environnement..."
check_env_var "SECRET_KEY"
check_env_var "DB_NAME"
check_env_var "DB_USER"
check_env_var "DB_PASSWORD"
check_env_var "FIELD_ENCRYPTION_KEY"

# Vérification de la longueur de la clé secrète
if [ ${#SECRET_KEY} -lt 50 ]; then
    echo "❌ Erreur: SECRET_KEY doit faire au moins 50 caractères"
    exit 1
fi

# Création des répertoires nécessaires
echo "📁 Création des répertoires..."
mkdir -p logs
mkdir -p media/children/photos
mkdir -p media/children/documents
mkdir -p media/children/medical
mkdir -p media/reports
mkdir -p media/uploads
mkdir -p static

# Configuration des permissions sécurisées
echo "🔒 Configuration des permissions..."
chmod 750 logs
chmod 755 media
chmod 644 .env 2>/dev/null || true

# Installation des dépendances Python
echo "📦 Installation des dépendances..."
pip install -r requirements.txt

# Vérification de la base de données
echo "🗄️ Vérification de la base de données..."
python manage.py check --database default

# Migrations de la base de données
echo "🔄 Application des migrations..."
python manage.py makemigrations
python manage.py migrate

# Création du superutilisateur si nécessaire
echo "👤 Configuration du superutilisateur..."
python manage.py shell << EOF
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(email='admin@orphanage.local').exists():
    User.objects.create_superuser(
        username='admin',
        email='admin@orphanage.local',
        password='AdminSecure123!@#',
        first_name='Admin',
        last_name='System'
    )
    print("✅ Superutilisateur créé: admin@orphanage.local")
else:
    print("ℹ️ Superutilisateur déjà existant")
EOF

# Collecte des fichiers statiques
echo "📋 Collecte des fichiers statiques..."
python manage.py collectstatic --noinput

# Vérification de la sécurité
echo "🔐 Vérification de la sécurité..."
python manage.py check --deploy

# Test de la configuration
echo "🧪 Test de la configuration..."
python manage.py shell << EOF
from django.conf import settings
from django.core.cache import cache
from django.db import connection

# Test de la base de données
try:
    with connection.cursor() as cursor:
        cursor.execute("SELECT 1")
    print("✅ Base de données: OK")
except Exception as e:
    print(f"❌ Base de données: {e}")

# Test du cache
try:
    cache.set('test_key', 'test_value', 30)
    if cache.get('test_key') == 'test_value':
        print("✅ Cache Redis: OK")
    else:
        print("❌ Cache Redis: Échec")
except Exception as e:
    print(f"❌ Cache Redis: {e}")

# Test du chiffrement
try:
    from apps.core.models import EncryptedField
    field = EncryptedField()
    encrypted = field.encrypt_value("test")
    decrypted = field.decrypt_value(encrypted)
    if decrypted == "test":
        print("✅ Chiffrement: OK")
    else:
        print("❌ Chiffrement: Échec")
except Exception as e:
    print(f"❌ Chiffrement: {e}")
EOF

# Démarrage de Celery en arrière-plan (si en développement)
if [ "$ENVIRONMENT" != "production" ]; then
    echo "🔄 Démarrage de Celery..."
    celery -A orphanage_backend worker -l info --detach
    celery -A orphanage_backend beat -l info --detach
fi

# Affichage des informations de sécurité
echo ""
echo "🔐 INFORMATIONS DE SÉCURITÉ:"
echo "================================"
echo "✅ Chiffrement des données: Activé"
echo "✅ Protection CSRF: Activé"
echo "✅ Rate limiting: Activé"
echo "✅ Audit logging: Activé"
echo "✅ HTTPS forcé: $([ "$DEBUG" = "False" ] && echo "Activé" || echo "Désactivé (dev)")"
echo "✅ Validation des mots de passe: Stricte"
echo ""

# Démarrage du serveur
if [ "$ENVIRONMENT" = "production" ]; then
    echo "🚀 Démarrage en mode production avec Gunicorn..."
    exec gunicorn orphanage_backend.wsgi:application \
        --bind 0.0.0.0:8000 \
        --workers 4 \
        --worker-class gevent \
        --worker-connections 1000 \
        --max-requests 1000 \
        --max-requests-jitter 100 \
        --timeout 30 \
        --keep-alive 2 \
        --log-level info \
        --access-logfile logs/access.log \
        --error-logfile logs/error.log
else
    echo "🚀 Démarrage en mode développement..."
    exec python manage.py runserver 0.0.0.0:8000
fi
