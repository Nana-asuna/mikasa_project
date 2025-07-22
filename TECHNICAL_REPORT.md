<u>📘 Documentation Technique</u>

---

# Architecture du Projet

Le projet est une application de gestion d'orphelinat composée de deux parties principales :
- **Frontend** : Next.js (React, TypeScript, Tailwind CSS)
- **Backend** : Django (REST API, Django REST Framework, JWT, SQLite)

## 1. Fonctionnalités principales
- Gestion des utilisateurs avec rôles (admin, médecin, soignant, assistant social, logisticien, donateur, parrain, visiteur)
- Authentification sécurisée (JWT, vérification email, gestion des tentatives échouées)
- Gestion des enfants (création, suivi, santé, statut)
- Gestion des familles d'accueil/adoptives et placements
- Gestion des dons et donateurs
- Gestion du stock/inventaire
- Planning (événements, visites médicales, activités)
- Génération de rapports PDF (enfants, statistiques)
- Notifications (emails, alertes)

## 2. Sécurité
- Authentification JWT (tokens d'accès et de rafraîchissement)
- Vérification d'email à l'inscription
- Limitation des tentatives de connexion (ratelimit, blocage IP)
- Historique des mots de passe (pas de réutilisation)
- Permissions par rôle (accès restreint selon le rôle)
- Audit des actions sensibles
- Protection CORS et configuration sécurisée

## 3. Base de données
- Modèles relationnels (utilisateurs, enfants, familles, dons, inventaire, planning)
- Utilisation de UUID pour les identifiants
- Champs d'audit (créé/modifié par, dates, IP, user agent)
- Historique des connexions et des mots de passe

## 4. API REST
- Endpoints RESTful pour toutes les entités principales
- Sérialisation/désérialisation avec Django REST Framework
- Validation avancée (validators, business rules)
- Pagination, filtrage, recherche
- Gestion des erreurs et messages localisés

## 5. Frontend (Next.js)
- Authentification et gestion du token JWT (localStorage)
- Pages protégées selon le rôle (middleware, hooks)
- Tableaux de bord dynamiques (statistiques, actions rapides)
- Formulaires réactifs (création, édition, validation)
- Composants UI réutilisables (cards, badges, alerts, spinners)
- Expérience utilisateur : chargement, feedback, gestion des erreurs
- Utilisation de Tailwind CSS pour le style

## 6. Déploiement & CI/CD
- Dockerisation du backend (Dockerfile, docker-compose)
- Fichiers d'environnement pour la configuration
- Prêt pour déploiement sur un PaaS (Heroku, Render, etc.)
- Instructions de seed et scripts d'initialisation

## 7. Tests & Qualité
- Linting (ESLint, Stylelint, .gitignore)
- Types TypeScript pour la sécurité du frontend
- Gestion des erreurs et logs (backend et frontend)
- Structure de projet modulaire et évolutive


---

Pour toute question ou contribution, voir le README ou contacter l'équipe projet. 
