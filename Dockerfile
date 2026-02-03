# Usar una imagen oficial de Python como base
FROM python:3.11-slim

# Establecer variables de entorno
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV DJANGO_SETTINGS_MODULE backyard_bar.settings

# Establecer el directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    libjpeg-dev \
    zlib1g-dev \
    netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

# Copiar el archivo de requerimientos e instalar dependencias
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el archivo entrypoint explícitamente primero
COPY backend_entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Copiar el resto del proyecto
COPY . /app/

# Crear directorios para estáticos y media
RUN mkdir -p /app/staticfiles /app/media

# Exponer el puerto
EXPOSE 8000

# Usar el script de entrada para esperar a la DB y aplicar migraciones
ENTRYPOINT ["/app/entrypoint.sh"]

# Comando final que arranca el servidor a través de Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "3", "backyard_bar.wsgi:application"]
