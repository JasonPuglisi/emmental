#!/bin/bash

# Install dependencies and run linter (will exit if failed)
echo -e "\n--------- INSTALLING DEPENDENCIES ----------\n"
pip3 install -r tests/requirements.txt
pip3 install -r config/flask/web/requirements.txt
echo -e "\n--------- RUNNING PYTHON LINTER ----------\n"
pylint src tests || exit $?

# Start Docker containers
echo -e "\n--------- STARTING DOCKER CONTAINERS ----------\n"
docker container prune -f
docker network prune -f
docker-compose up -d

# Wait for services to come up
sleep 10

# Set MariaDB internal IP address
export MARIADB_IP=`docker inspect -f '{{range.NetworkSettings.Networks}}{{.IPAddress}}{{end}}' mariadb`
export MARIADB_USER='databaseuser'
export MARIADB_PASSWORD='securedatabasepassword'
export MARIADB_DATABASE='emmental'

# Run tests
echo -e "\n--------- RUNNING TESTS ----------\n"
pytest

# Stop Docker containers
echo -e "\n--------- STOPPING DOCKER CONTAINERS ----------\n"
docker-compose down
docker network prune -f
docker container prune -f
