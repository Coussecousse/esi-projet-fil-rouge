#!/bin/bash
# setup-monitoring.sh - Setup monitoring configuration

MONITORING_DIR="./monitoring"
mkdir -p $MONITORING_DIR

# Create Prometheus configuration
cat > $MONITORING_DIR/prometheus.yml << 'EOF'
global:
  scrape_interval: 15s
  evaluation_interval: 15s
  external_labels:
    cluster: 'medisecure'
    environment: 'production'

scrape_configs:
  # Kong API Gateway
  - job_name: 'kong'
    static_configs:
      - targets: ['kong:8001']
    metrics_path: '/metrics'
  
  # Patient Service
  - job_name: 'service-patient'
    static_configs:
      - targets: ['service-patient:8000']
    metrics_path: '/metrics'
  
  # Appointments Service
  - job_name: 'service-appointments'
    static_configs:
      - targets: ['service-appointments:5000']
    metrics_path: '/metrics'
  
  # Documents Service
  - job_name: 'service-documents'
    static_configs:
      - targets: ['service-documents:5000']
    metrics_path: '/metrics'
  
  # Billing Service
  - job_name: 'service-billing'
    static_configs:
      - targets: ['service-billing:8000']
    metrics_path: '/metrics'
  
  # PostgreSQL Exporter
  - job_name: 'postgres'
    static_configs:
      - targets: ['postgres-patients:5432']
  
  # MongoDB Exporter
  - job_name: 'mongodb'
    static_configs:
      - targets: ['mongodb-appointments:27017']
  
  # RabbitMQ
  - job_name: 'rabbitmq'
    static_configs:
      - targets: ['rabbitmq-broker:15672']
    metrics_path: '/api/metrics'
  
  # Redis
  - job_name: 'redis'
    static_configs:
      - targets: ['redis-cache:6379']
EOF

# Create Grafana datasource configuration
cat > $MONITORING_DIR/grafana-datasources.yml << 'EOF'
apiVersion: 1

datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://prometheus:9090
    isDefault: true
    editable: true
EOF

echo "✅ Monitoring configuration created successfully!"
echo "📊 Access Prometheus at: http://localhost:9090"
echo "📈 Access Grafana at: http://localhost:3001 (admin/check secrets/grafana_admin_password.txt)"
