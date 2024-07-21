#!/bin/bash
echo "Deploying Debezium connector"
curl -X POST http://debezium:8083/connectors \
     -H "Content-Type: application/json" \
     -d @/init/postgres_connector.json
