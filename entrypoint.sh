#!/bin/bash

# Salir inmediatamente si un comando falla
set -e

# Esperar a que la base de datos esté lista
if [ "$DATABASE" = "postgres" ]
then
    echo "Esperando a postgres..."

    while ! nc -z $SQL_HOST $SQL_PORT; do
      sleep 0.1
    done

    echo "Postgres iniciado"
fi

# Aplicar migraciones
echo "Aplicando migraciones..."
python manage.py migrate

# Recopilar archivos estáticos (Necesario para producción)
echo "Recopilando archivos estáticos..."
python manage.py collectstatic --noinput

# Iniciar el servidor
echo "Iniciando servidor..."
exec "$@"
