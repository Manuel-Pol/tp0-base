#!/bin/bash

# Se verifica que la cantidad de parametros sea la adecuada
if [ "$#" -ne 2 ]; then
    echo "Por favor ejecute con los parametros: $0 <nombre-del-archivo-de-salida> <cantidad-de-clientes>"
    exit 1
fi

echo "Nombre del archivo de salida: $1"
echo "Cantidad de clientes: $2"

output_file=$1
client_count=$2

cat <<EOF > $output_file
name: tp0
services:
  server:
    container_name: server
    image: server:latest
    entrypoint: python3 /main.py
    environment:
      - PYTHONUNBUFFERED=1
      - LOGGING_LEVEL=DEBUG
    networks:
      - testing_net
EOF

for i in $(seq 1 $client_count); do
    cat <<EOF >> $output_file

  client$i:
    container_name: client$i
    image: client:latest
    entrypoint: /client
    environment:
      - CLI_ID=$i
      - CLI_LOG_LEVEL=DEBUG
    networks:
      - testing_net
    depends_on:
      - server
EOF
done

cat <<EOF >> $output_file

networks:
  testing_net:
    ipam:
      driver: default
      config:
        - subnet: 172.25.125.0/24
EOF

echo "Archivo $output_file generado con $client_count clientes."
