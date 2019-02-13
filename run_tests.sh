#!/bin/bash

# Start Docker instances
docker container prune -f
docker-compose up -d

# Install dependencies and run tests
pip3 install -r tests/requirements.txt
pytest-3

# Stop Docker instances
docker-compose down
