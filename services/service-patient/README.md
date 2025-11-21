# Service Patient - Gestion des Patients

## Technologie
- **Framework**: Django 2.2
- **Langage**: Python 3.7
- **Base de données**: PostgreSQL

## Installation locale

```bash
cd services/service-patient
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Configuration

Variables d'environnement (`.env`):
```env
DB_NAME=medisecure_patients
DB_USER=medisecure_user
DB_PASSWORD=medisecure_password
DB_HOST=localhost
DB_PORT=5432
REDIS_URL=redis://localhost:6379/1
DJANGO_SECRET_KEY=your-secret-key
DJANGO_ALLOWED_HOSTS=*
DJANGO_DEBUG=True
```

## Lancement

```bash
# Migrations
python manage.py migrate

# Créer un superuser
python manage.py createsuperuser

# Lancer le serveur
python manage.py runserver 0.0.0.0:8000

# Mode production avec Gunicorn
gunicorn --bind 0.0.0.0:8000 --workers 4 config.wsgi:application
```

## Endpoints

- `GET /health` - Health check
- `GET /api/patients` - Liste des patients
- `POST /api/patients` - Créer un patient
- `GET /api/patients/{id}` - Détails d'un patient
- `PUT /api/patients/{id}` - Modifier un patient
- `DELETE /api/patients/{id}` - Supprimer un patient

## Admin Django

Accédez à l'interface d'administration sur `http://localhost:8000/admin/`

## Docker

```bash
# Build
docker build -t service-patient .

# Run
docker run -p 8000:8000 --env-file .env service-patient
```

## Tests

```bash
python manage.py test
```
