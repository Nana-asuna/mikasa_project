# Backend Orphanage Management

## Structure du dossier

```
backend/
│
├── apps/                  # Toutes les applications Django personnalisées
├── orphanage_backend/     # Configuration principale du projet Django (settings, urls, celery, etc.)
├── templates/             # Templates HTML globaux (emails, etc.)
├── scripts/               # Scripts utilitaires (ex: seed_data.py)
├── logs/                  # Dossier pour les logs générés par Django
├── manage.py              # Commande d'administration Django
├── requirements.txt       # Dépendances Python
├── Dockerfile             # Docker pour le backend
├── docker-compose.yml     # Docker Compose (si utilisé)
└── .env                   # Variables d'environnement (à ne pas versionner)
```

## Conseils
- Place toutes tes apps Django dans `apps/`.
- La configuration globale (settings, urls, celery, etc.) est dans `orphanage_backend/`.
- Les templates d'emails ou globaux sont dans `templates/`.
- Les scripts utilitaires sont dans `scripts/`.
- Les logs générés automatiquement sont dans `logs/`.
- Le fichier `.env` contient toutes les variables d'environnement nécessaires (voir exemple dans la documentation principale).

## Lancement rapide

1. Crée un environnement virtuel Python :
   ```sh
   python -m venv venv
   .\venv\Scripts\activate
   pip install -r requirements.txt
   ```
2. Ajoute un fichier `.env` (voir exemple dans la doc principale).
3. Applique les migrations :
   ```sh
   python manage.py migrate
   ```
4. Lance le serveur :
   ```sh
   python manage.py runserver
   ``` 