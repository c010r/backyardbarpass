#!/bin/bash

# --- CONFIGURACIÓN ---
# Cargar variables desde el .env
if [ -f .env ]; then
    export $(cat .env | grep -v '#' | xargs)
fi

CONTAINER_NAME="backyard-db"
DB_USER="backyard_user"
DB_NAME="backyard_db"
BACKUP_DIR="./backups"
DATE=$(date +%Y-%m-%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/backup_$DATE.sql.gz"
RETENTION_DAYS=7

# --- EJECUCIÓN ---

# Crear directorio si no existe
mkdir -p $BACKUP_DIR

echo "### Iniciando backup de la base de datos... ($DATE)"

# Ejecutar el dump dentro del contenedor y comprimirlo
docker exec $CONTAINER_NAME pg_dump -U $DB_USER $DB_NAME | gzip > $BACKUP_FILE

if [ $? -eq 0 ]; then
    echo "### Backup completado exitosamente: $BACKUP_FILE"
else
    echo "### ERROR: Falló el backup de la base de datos."
    exit 1
fi

# Eliminar backups antiguos (más de $RETENTION_DAYS días)
echo "### Limpiando backups antiguos (mayores a $RETENTION_DAYS días)..."
find $BACKUP_DIR -name "backup_*.sql.gz" -mtime +$RETENTION_DAYS -delete

echo "### Proceso de backup finalizado."
