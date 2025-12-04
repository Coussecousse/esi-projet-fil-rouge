#!/bin/bash
# Script to check server health before deployment

echo "=== Server Health Check ==="
echo ""

echo "1. Disk Space:"
df -h /
echo ""

echo "2. Memory Usage:"
free -h
echo ""

echo "3. CPU Load:"
uptime
echo ""

echo "4. Docker Status:"
docker info 2>/dev/null | grep -E "Server Version|Storage Driver|Total Memory|CPUs"
echo ""

echo "5. Running Containers:"
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Size}}"
echo ""

echo "6. Docker Images Size:"
docker images --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}" | head -20
echo ""

echo "7. Network Connectivity Test:"
ping -c 3 8.8.8.8
echo ""

echo "8. Download Speed Test:"
time curl -o /dev/null -s https://speed.cloudflare.com/__down?bytes=10000000
echo ""
