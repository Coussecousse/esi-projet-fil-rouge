# Backend Monolithique - DEPRECATED

⚠️ **CE SERVICE EST OBSOLÈTE** ⚠️

## Pourquoi ce service n'est plus utilisé ?

Ce répertoire `medisecure-backend` contenait une architecture monolithique qui a été remplacée par une **architecture microservices**.

## Nouvelle architecture

Les fonctionnalités de ce backend ont été réparties dans les microservices suivants :

- **Patient Management** → `services/service-patient/` (Django)
- **Appointment Management** → `services/service-rdv/` (Flask)
- **Document Management** → `services/service-documents/` (.NET Core)
- **Billing Management** → `services/service-facturation/` (FastAPI)

## API Gateway

Le routage et la gestion centralisée des API sont maintenant assurés par :
- **Kong API Gateway** (port 8000/8001)
- **HAProxy Load Balancer** (port 80/443)

## Migration

Si vous avez besoin de récupérer du code de ce backend :
1. Les modèles de données sont dans `shared/`
2. Les controllers sont répartis dans les microservices correspondants
3. La configuration est dans chaque service individuel

## Suppression

Ce répertoire peut être supprimé une fois la migration complètement terminée et validée.