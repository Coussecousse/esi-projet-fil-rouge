#!/bin/bash

# MediSecure - Quick Start Script
# This script starts all microservices and infrastructure

set -e

echo "================================"
echo "MediSecure - Starting Services"
echo "================================"

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "Error: Docker is not running. Please start Docker first."
    exit 1
fi

# Check if .env file exists
if [ ! -f .env ]; then
    echo "Warning: .env file not found. Copying from .env.example..."
    cp .env.example .env
    echo "Please edit .env file with your configuration before running in production."
fi

# Start all services
echo ""
echo "Starting all services with docker-compose..."
docker-compose up -d

# Wait for services to be healthy
echo ""
echo "Waiting for services to be healthy..."
sleep 10

# Check service status
echo ""
echo "Checking service status..."
docker-compose ps

echo ""
echo "================================"
echo "Services started successfully!"
echo "================================"
echo ""
echo "Access URLs:"
echo "  - Frontend:           http://localhost:80"
echo "  - Kong API Gateway:   http://localhost:8000"
echo "  - Keycloak:           http://localhost:8080"
echo "  - RabbitMQ:           http://localhost:15672"
echo "  - Grafana:            http://localhost:3001"
echo "  - Prometheus:         http://localhost:9090"
echo "  - MinIO Console:      http://localhost:9001"
echo ""
echo "To view logs: docker-compose logs -f"
echo "To stop:      docker-compose down"
echo ""
