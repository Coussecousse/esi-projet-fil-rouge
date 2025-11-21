# Service RDV - Gestion des Rendez-vous

## Technologie
- **Framework**: Flask 2.0
- **Langage**: Python 3.9
- **Base de données**: MongoDB

## Installation locale

```bash
cd services/service-rdv
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Configuration

Variables d'environnement (`.env`):
```env
MONGODB_URL=mongodb://localhost:27017/medisecure_appointments
RABBITMQ_URL=amqp://guest:guest@localhost:5672/
REDIS_URL=redis://localhost:6379/0
FLASK_ENV=development
PORT=5000
```

## Lancement

```bash
# Mode développement
python app.py

# Mode production avec Gunicorn
gunicorn --bind 0.0.0.0:5000 --workers 4 app:app
```

## Endpoints

- `GET /health` - Health check
- `GET /api/appointments` - Liste des rendez-vous
- `POST /api/appointments` - Créer un rendez-vous
- `GET /api/appointments/{id}` - Détails d'un rendez-vous
- `PUT /api/appointments/{id}` - Modifier un rendez-vous
- `DELETE /api/appointments/{id}` - Annuler un rendez-vous

## Docker

```bash
# Build
docker build -t service-rdv .

# Run
docker run -p 5000:5000 --env-file .env service-rdv
```

## Tests

```bash
pytest tests/
```
