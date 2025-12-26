# Grafana Provisioning - Files Explanation

## Files in this directory

### datasources/
- **`datasources.yml`** (ACTIF) - Configuration des datasources Grafana
  - Définit où Prometheus se trouve
  - Format: Grafana Provisioning API v1
  - Contient: `apiVersion: 1` et liste des datasources

- **`prometheus.yml`** (DÉPRÉCIÉE) - Fichier vide/commenté
  - Ancien nom qui causait confusion avec Prometheus
  - Renommé en `datasources.yml` pour clarté
  - Garder pour compatibilité, mais ne pas éditer

### dashboards/
- **`dashboards.yml`** - Configuration des dashboards
  - Définit où Grafana cherche les fichiers JSON des dashboards
  - Format: Grafana Provisioning API v1

## Why the rename?

Confusion schémas YAML:
- `prometheus/prometheus.yml` → Schema Prometheus (NO apiVersion)
- `grafana/provisioning/datasources/prometheus.yml` → Schema Grafana (YES apiVersion)

VS Code et les éditeurs appliquaient le schema prometheus.json au fichier dans le répertoire datasources, ce qui causait une erreur car Prometheus n'accepte pas `apiVersion: 1`.

## Solution

✓ Fichier datasources renommé en `datasources.yml`
✓ Pas de conflit de schema
✓ Grafana lit le répertoire entier `/etc/grafana/provisioning/datasources/`
✓ Fonctionne identiquement

Garder `prometheus.yml` comme stub/référence historique.
