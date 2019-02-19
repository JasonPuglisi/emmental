#!/bin/bash

# Start Docker instances
docker container prune -f
docker network prune -f
docker-compose up -d

# Wait for services to come up
sleep 5

# Set MariaDB internal IP address
export MARIADB_IP=`docker inspect -f '{{range.NetworkSettings.Networks}}{{.IPAddress}}{{end}}' mariadb_database`

# Install dependencies and run tests
pip3 install -r tests/requirements.txt
pytest

# Stop Docker instances
docker-compose down
docker network prune -f
docker container prune -f
