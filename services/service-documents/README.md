# Service Documents - Gestion des Documents Médicaux

## Technologie
- **Framework**: .NET Core 3.1 (ASP.NET Core)
- **Langage**: C#
- **Stockage**: MinIO (S3-compatible)

## Installation locale

```bash
cd services/service-documents

# Restaurer les packages NuGet
dotnet restore

# Build
dotnet build
```

## Configuration

`appsettings.json`:
```json
{
  "MinIO": {
    "Endpoint": "localhost:9000",
    "AccessKey": "minio_admin",
    "SecretKey": "minio_password",
    "BucketName": "medisecure-documents"
  }
}
```

Variables d'environnement:
```env
MinIO__Endpoint=localhost:9000
MinIO__AccessKey=minio_admin
MinIO__SecretKey=minio_password
ASPNETCORE_URLS=http://+:5000
```

## Lancement

```bash
# Mode développement
dotnet run

# Mode production
dotnet publish -c Release
dotnet bin/Release/netcoreapp3.1/service-documents.dll
```

## Endpoints

- `GET /health` - Health check
- `GET /swagger` - Documentation Swagger
- `GET /api/documents` - Liste des documents
- `POST /api/documents` - Upload un document
- `GET /api/documents/{id}` - Télécharger un document
- `DELETE /api/documents/{id}` - Supprimer un document

## Swagger UI

Documentation interactive disponible sur `http://localhost:5000/swagger`

## Docker

```bash
# Build
docker build -t service-documents .

# Run
docker run -p 5000:5000 --env-file .env service-documents
```

## Tests

```bash
dotnet test
```
