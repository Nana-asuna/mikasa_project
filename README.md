# Orphanage Management System 

Système de gestion complet pour orphelinat avec API REST sécurisée.

## 🏗️ Architecture

### Structure du projet

orphanage_backend/
├── apps/
│   ├── accounts/          # Gestion des utilisateurs et authentification
│   ├── children/          # Gestion des enfants
│   ├── donations/         # Gestion des dons et donateurs
│   ├── inventory/         # Gestion de l'inventaire
│   ├── planning/          # Planification et événements
│   ├── families/          # Familles d'accueil et adoptives
│   ├── reports/           # Rapports et tableaux de bord
│   ├── notifications/     # Système de notifications
│   └── core/              # Utilitaires et permissions
├── orphanage_backend/     # Configuration Django
├── templates/             # Templates d'emails
├── scripts/               # Scripts utilitaires
└── requirements.txt       # Dépendances Python
\`\`\`

## 🚀 Installation et Configuration

### Prérequis
- Python 3.11+
- PostgreSQL 13+
- Redis 6+
- Docker (optionnel)

### Installation locale

1. **Cloner le projet**
\`\`\`bash
git clone <repository-url>
cd orphanage_backend
\`\`\`

2. **Créer un environnement virtuel**
\`\`\`bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows
\`\`\`

3. **Installer les dépendances**
\`\`\`bash
pip install -r requirements.txt
\`\`\`

4. **Configuration de l'environnement**
\`\`\`bash
cp .env.example .env
# Éditer le fichier .env avec vos paramètres
\`\`\`

5. **Configuration de la base de données**
\`\`\`bash
# Créer la base de données PostgreSQL
createdb orphanage_db

# Appliquer les migrations
python manage.py migrate

# Créer un superutilisateur
python manage.py createsuperuser
\`\`\`

6. **Peupler avec des données de test**
\`\`\`bash
python scripts/seed_data.py
\`\`\`

7. **Démarrer le serveur**
\`\`\`bash
python manage.py runserver
\`\`\`

### Installation avec Docker

1. **Démarrer avec Docker Compose**
\`\`\`bash
docker-compose up -d
\`\`\`

2. **Appliquer les migrations**
\`\`\`bash
docker-compose exec web python manage.py migrate
\`\`\`

3. **Créer un superutilisateur**
\`\`\`bash
docker-compose exec web python manage.py createsuperuser
\`\`\`

## 🔧 Configuration

### Variables d'environnement principales

| Variable | Description | Exemple |
|----------|-------------|---------|
| `SECRET_KEY` | Clé secrète Django | `your-secret-key` |
| `DEBUG` | Mode debug | `False` |
| `DB_NAME` | Nom de la base de données | `orphanage_db` |
| `DB_USER` | Utilisateur DB | `orphanage_user` |
| `DB_PASSWORD` | Mot de passe DB | `password` |
| `REDIS_URL` | URL Redis | `redis://localhost:6379/0` |
| `EMAIL_HOST` | Serveur SMTP | `smtp.gmail.com` |

### Rôles utilisateur

| Rôle | Permissions |
|------|-------------|
| `admin` | Accès complet à toutes les fonctionnalités |
| `assistant_social` | Gestion des enfants, familles, rapports |
| `soignant` | Gestion médicale des enfants |
| `logisticien` | Gestion de l'inventaire et des stocks |
| `donateur` | Consultation des dons personnels |
| `parrain` | Consultation des enfants parrainés |
| `visiteur` | Consultation publique limitée |

## 📚 API Documentation

### Authentification
L'API utilise JWT (JSON Web Tokens) pour l'authentification.

**Endpoints d'authentification :**
- `POST /api/auth/login/` - Connexion
- `POST /api/auth/register/` - Inscription
- `POST /api/auth/refresh/` - Renouvellement du token
- `POST /api/auth/logout/` - Déconnexion

**Headers requis :**
\`\`\`
Authorization: Bearer <access_token>
Content-Type: application/json
\`\`\`

### Endpoints principaux

#### Enfants
- `GET /api/children/` - Liste des enfants
- `POST /api/children/` - Créer un enfant
- `GET /api/children/{id}/` - Détails d'un enfant
- `GET /api/children/public/` - Enfants à parrainer (public)
- `GET /api/children/statistics/` - Statistiques

#### Dons
- `GET /api/donations/` - Liste des dons
- `POST /api/donations/` - Enregistrer un don
- `GET /api/donations/donors/` - Liste des donateurs
- `GET /api/donations/statistics/` - Statistiques des dons

#### Inventaire
- `GET /api/inventory/items/` - Articles d'inventaire
- `POST /api/inventory/items/` - Ajouter un article
- `GET /api/inventory/movements/` - Mouvements de stock
- `POST /api/inventory/items/bulk-update/` - Mise à jour en lot

#### Planning
- `GET /api/planning/events/` - Événements
- `POST /api/planning/events/` - Créer un événement
- `GET /api/planning/events/calendar/` - Événements pour calendrier
- `GET /api/planning/tasks/` - Tâches

#### Familles
- `GET /api/families/` - Familles d'accueil
- `POST /api/families/` - Ajouter une famille
- `GET /api/families/placements/` - Placements
- `POST /api/families/{id}/approve/` - Approuver une famille

### Documentation interactive
- Swagger UI : `http://localhost:8000/api/docs/`
- ReDoc : `http://localhost:8000/api/redoc/`
- Schéma OpenAPI : `http://localhost:8000/api/schema/`

## 🔒 Sécurité

### Mesures de sécurité implémentées

1. **Authentification et autorisation**
   - JWT avec rotation des tokens
   - Vérification par email obligatoire
   - Limitation des tentatives de connexion
   - Historique des mots de passe

2. **Protection des données**
   - Chiffrement des données sensibles
   - Anonymisation pour les visiteurs
   - Contrôle d'accès basé sur les rôles
   - Audit trail complet

3. **Sécurité réseau**
   - CORS configuré
   - Headers de sécurité
   - Rate limiting
   - Protection CSRF

4. **Monitoring**
   - Logs de sécurité
   - Détection d'intrusion
   - Alertes automatiques

## 🔄 Tâches automatisées (Celery)

### Tâches programmées

| Tâche | Fréquence | Description |
|-------|-----------|-------------|
| `process_recurring_donations` | Quotidienne | Traite les dons récurrents |
| `check_low_stock` | 6 heures | Vérifie les stocks faibles |
| `send_appointment_reminders` | Horaire | Envoie les rappels d'événements |
| `send_daily_reports` | Quotidienne | Génère les rapports programmés |

### Démarrer Celery

\`\`\`bash
# Worker
celery -A orphanage_backend worker -l info

# Beat scheduler
celery -A orphanage_backend beat -l info

# Monitoring
celery -A orphanage_backend flower
\`\`\`

## 📊 Monitoring et Logs

### Logs
Les logs sont organisés par niveau :
- `logs/django.log` - Logs généraux
- `logs/security.log` - Logs de sécurité

### Health checks
- `GET /health/` - Status de base
- `GET /health/status/` - Status détaillé (DB, Cache)

### Métriques
- Intégration Sentry pour le monitoring d'erreurs
- Logs structurés pour l'analyse

## 🧪 Tests

\`\`\`bash
# Lancer tous les tests
python manage.py test

# Tests avec couverture
coverage run --source='.' manage.py test
coverage report
coverage html
\`\`\`

## 🚀 Déploiement

### Déploiement sur Vercel/Railway

1. **Préparer les variables d'environnement**
2. **Configurer la base de données (Neon/Supabase)**
3. **Déployer avec les commandes de build**

### Déploiement Docker

\`\`\`bash
# Build de l'image
docker build -t orphanage-backend .

# Déploiement
docker-compose -f docker-compose.prod.yml up -d
\`\`\`

## 🤝 Contribution

1. Fork le projet
2. Créer une branche feature (`git checkout -b feature/AmazingFeature`)
3. Commit les changements (`git commit -m 'Add AmazingFeature'`)
4. Push vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrir une Pull Request

## 📝 License

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

## 📞 Support

Pour toute question ou support :
- Email : support@orphelinat-espoir.fr
- Documentation : [Wiki du projet]
- Issues : [GitHub Issues]

---

**Développé avec ❤️ pour l'Orphelinat Espoir**
\`\`\`

🎉 **Backend Django complet généré !**

Le backend est maintenant entièrement fonctionnel avec :

✅ **API REST complète** avec tous les endpoints
✅ **Authentification JWT sécurisée** 
✅ **Système de permissions** basé sur les rôles
✅ **Gestion complète** de tous les modules
✅ **Tâches automatisées** avec Celery
✅ **Templates d'emails** 
✅ **Configuration Docker**
✅ **Scripts de déploiement**
✅ **Documentation complète**

Le système est prêt pour la production avec toutes les mesures de sécurité et les bonnes pratiques Django !
