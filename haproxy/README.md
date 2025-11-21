# HAProxy Configuration - MediSecure

## Vue d'ensemble

HAProxy (High Availability Proxy) est utilisé comme **Load Balancer** pour:
- Répartir la charge entre plusieurs instances backend/frontend
- Gérer le routage intelligent du trafic
- Fournir du SSL/TLS termination
- Health checking automatique
- Statistiques en temps réel

## Architecture

```
                    Internet
                       |
                   HAProxy
                  (Port 80/443)
                       |
        +--------------+--------------+
        |                             |
    /api/*                        /*
        |                             |
   Backend API                  Frontend
  (FastAPI)                    (React/Vite)
   3+ replicas                  3+ replicas
```

## Ports exposés

| Port | Service | Description |
|------|---------|-------------|
| 80 | HTTP | Trafic HTTP (avec redirection HTTPS optionnelle) |
| 443 | HTTPS | Trafic HTTPS sécurisé (nécessite certificat) |
| 8404 | Stats | Page de statistiques HAProxy |

## Configuration actuelle

### Frontend HTTP (Port 80)
- Routing basé sur le path:
  - `/api/*` → Backend FastAPI
  - `/*` → Frontend React
- ACLs pour identifier le type de requête
- Redirection HTTPS optionnelle (commentée)

### Backend API
- **Balance**: Round Robin
- **Health Check**: GET /health (attendu: 200 OK)
- **Retry**: 3 tentatives
- **Timeout**: 30s
- **Servers**: backend1 (ajustable pour multiple replicas)

### Backend Frontend
- **Balance**: Round Robin
- **Health Check**: GET / (attendu: 200 OK)
- **Retry**: 3 tentatives
- **Timeout**: 30s
- **Servers**: frontend1 (ajustable pour multiple replicas)

## Utilisation avec Docker Compose

Le fichier `haproxy.cfg` est monté en volume dans le conteneur HAProxy:

```yaml
medisecure-haproxy:
  image: haproxy:2.4
  ports:
    - "80:80"
    - "443:443"
    - "8404:8404"
  volumes:
    - ./haproxy/haproxy.cfg:/usr/local/etc/haproxy/haproxy.cfg:ro
```

### Démarrer HAProxy
```bash
docker-compose up -d medisecure-haproxy
```

### Accéder aux statistiques
```
http://localhost:8404/stats
```
- Identifiants: admin / admin (à changer en production)

## Scaling avec HAProxy

### Ajouter des replicas backend

1. **Modifier `haproxy.cfg`**:
```haproxy
backend backend_api
    server backend1 medisecure-backend:8000 check
    server backend2 medisecure-backend-2:8000 check
    server backend3 medisecure-backend-3:8000 check
```

2. **Redémarrer HAProxy**:
```bash
docker-compose restart medisecure-haproxy
```

### Ajouter des replicas frontend

1. **Modifier `haproxy.cfg`**:
```haproxy
backend frontend_app
    server frontend1 medisecure-frontend:3000 check
    server frontend2 medisecure-frontend-2:3000 check
    server frontend3 medisecure-frontend-3:3000 check
```

## Configuration HTTPS/SSL

Pour activer HTTPS en production:

### 1. Générer ou obtenir un certificat SSL

**Option A: Certificat auto-signé (dev/test)**
```bash
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout haproxy/certs/medisecure.key \
  -out haproxy/certs/medisecure.crt

cat haproxy/certs/medisecure.crt haproxy/certs/medisecure.key > haproxy/certs/medisecure.pem
```

**Option B: Let's Encrypt (production)**
```bash
certbot certonly --standalone -d medisecure.example.com
cat /etc/letsencrypt/live/medisecure.example.com/fullchain.pem \
    /etc/letsencrypt/live/medisecure.example.com/privkey.pem > haproxy/certs/medisecure.pem
```

### 2. Décommenter la section HTTPS dans `haproxy.cfg`

```haproxy
frontend https_frontend
    bind *:443 ssl crt /usr/local/etc/haproxy/certs/medisecure.pem
    mode http
    
    http-response set-header Strict-Transport-Security "max-age=31536000"
    http-response set-header X-Frame-Options "SAMEORIGIN"
    
    acl is_api path_beg /api
    use_backend backend_api if is_api
    default_backend frontend_app
```

### 3. Activer la redirection HTTP → HTTPS

```haproxy
frontend http_frontend
    bind *:80
    redirect scheme https code 301 if !{ ssl_fc }
```

### 4. Monter le volume des certificats

```yaml
medisecure-haproxy:
  volumes:
    - ./haproxy/haproxy.cfg:/usr/local/etc/haproxy/haproxy.cfg:ro
    - ./haproxy/certs:/usr/local/etc/haproxy/certs:ro
```

## Rate Limiting

Pour limiter le nombre de requêtes par IP:

```haproxy
frontend http_frontend
    # Table pour tracker les requêtes
    stick-table type ip size 100k expire 30s store http_req_rate(10s)
    
    # Tracker l'IP source
    http-request track-sc0 src
    
    # Bloquer si > 100 req/10s
    http-request deny deny_status 429 if { sc_http_req_rate(0) gt 100 }
```

## Monitoring & Stats

### Page de statistiques
- **URL**: http://localhost:8404/stats
- **Authentification**: admin / admin
- **Informations disponibles**:
  - État des serveurs (UP/DOWN)
  - Nombre de connexions actives
  - Requêtes par seconde
  - Taux d'erreurs
  - Latence moyenne

### Métriques exposées
- Sessions actives/totales
- Bytes in/out
- Request rate
- Error rate
- Queue length
- Response time

### Intégration Prometheus

HAProxy expose naturellement des métriques sur le port 8404.

Dans Kubernetes, Prometheus est configuré pour scraper:
```yaml
- job_name: 'haproxy'
  static_configs:
  - targets: ['haproxy-service:8404']
```

## Logs

### Voir les logs en temps réel
```bash
docker logs -f medisecure-haproxy
```

### Format des logs
```
<date> <frontend> <backend>/<server> <timers> <status> <bytes> <request>
```

Exemple:
```
Nov 21 10:30:45 http_frontend backend_api/backend1 0/0/1/23/24 200 1234 "GET /api/patients HTTP/1.1"
```

## Troubleshooting

### HAProxy ne démarre pas
```bash
# Vérifier la syntaxe de la config
docker run --rm -v $(pwd)/haproxy/haproxy.cfg:/tmp/haproxy.cfg:ro haproxy:2.4 haproxy -c -f /tmp/haproxy.cfg
```

### Backend marqué comme DOWN
- Vérifier que le service backend/frontend est bien démarré
- Vérifier l'endpoint de health check (/health pour backend, / pour frontend)
- Consulter les logs HAProxy

### Requêtes lentes
- Vérifier les statistiques (temps de réponse moyen)
- Augmenter le nombre de replicas
- Ajuster les timeouts dans la configuration

## Configuration avancée

### Compression
```haproxy
frontend http_frontend
    compression algo gzip
    compression type text/html text/plain text/css application/javascript application/json
```

### Headers de sécurité
```haproxy
http-response set-header X-Content-Type-Options "nosniff"
http-response set-header X-XSS-Protection "1; mode=block"
http-response set-header Referrer-Policy "strict-origin-when-cross-origin"
```

### Sticky Sessions (optionnel)
```haproxy
backend backend_api
    balance roundrobin
    cookie SERVERID insert indirect nocache
    server backend1 medisecure-backend:8000 check cookie backend1
    server backend2 medisecure-backend-2:8000 check cookie backend2
```

## Production Checklist

- [ ] Changer le mot de passe des stats (admin/admin)
- [ ] Activer HTTPS avec certificat valide
- [ ] Configurer la redirection HTTP → HTTPS
- [ ] Activer la compression
- [ ] Configurer les headers de sécurité
- [ ] Configurer le rate limiting
- [ ] Ajuster les timeouts selon votre application
- [ ] Configurer le logging vers un système centralisé
- [ ] Monitorer avec Prometheus/Grafana
- [ ] Tester le failover des backends

## Références

- [Documentation HAProxy](http://www.haproxy.org/)
- [HAProxy Configuration Manual](http://cbonte.github.io/haproxy-dconv/2.4/configuration.html)
- [HAProxy Best Practices](https://www.haproxy.com/blog/haproxy-best-practice-http-configurations/)
