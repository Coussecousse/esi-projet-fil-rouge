# Service Facturation - Gestion de la Facturation

## Technologie
- **Framework**: FastAPI
- **Langage**: Python 3.8
- **Base de données**: MariaDB

## Installation locale

```bash
cd services/service-facturation
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Configuration

Variables d'environnement (`.env`):
```env
MARIADB_URL=mysql://root:password@localhost:3306/medisecure_billing
REDIS_URL=redis://localhost:6379/2
RABBITMQ_URL=amqp://guest:guest@localhost:5672/
PORT=8000
ENVIRONMENT=development
```

## Lancement

```bash
# Mode développement
python app.py

# Mode production avec Uvicorn
uvicorn app:app --host 0.0.0.0 --port 8000 --workers 4
```

## Endpoints

- `GET /health` - Health check
- `GET /docs` - Documentation Swagger automatique
- `GET /api/invoices` - Liste des factures
- `POST /api/invoices` - Créer une facture
- `GET /api/invoices/{id}` - Détails d'une facture
- `PUT /api/invoices/{id}` - Modifier une facture
- `DELETE /api/invoices/{id}` - Supprimer une facture
- `POST /api/invoices/{id}/pay` - Marquer comme payée

## Documentation API

FastAPI génère automatiquement:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## Docker

```bash
# Build
docker build -t service-facturation .

# Run
docker run -p 8000:8000 --env-file .env service-facturation
```

## Tests

```bash
pytest tests/
```
