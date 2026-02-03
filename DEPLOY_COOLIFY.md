# Guía de Despliegue en Coolify - Backyard Bar Pass 🚀

Esta guía detalla los pasos necesarios para desplegar el sistema en un VPS propio utilizando **Coolify** de forma profesional.

## 1. Requisitos Previos
*   Tener Coolify instalado en tu VPS.
*   Tener un dominio apuntando a la IP de tu VPS (ej. `https://backyardpass.uy`).
*   Tener acceso al repositorio: `https://github.com/c010r/backyardbarpass.git`.

## 2. Crear el Proyecto en Coolify
1.  Entra a tu panel de Coolify.
2.  Ve a **Projects** -> **Create New Project** -> Nómbralo como `Backyard Bar`.
3.  Dentro del proyecto, haz clic en **+ New** -> **Service**.
4.  Selecciona **Public Repository** (o conecta con tu GitHub).
5.  Pega la URL: `https://github.com/c010r/backyardbarpass.git`
6.  En el paso de configuración, selecciona **Docker Compose**.

## 3. Configuración del Archivo Compose
Coolify detectará el archivo por defecto, pero nosotros creamos uno optimizado:
1.  En la pestaña **General**, busca el campo **Docker Compose Location**.
2.  Cámbialo a: `./docker-compose-coolify.yml`.
3.  Haz clic en **Save**.

## 4. Configurar el Dominio y Puerto
1.  Busca la lista de servicios y selecciona el que se llama **`frontend`**.
2.  En el campo **Domains**, ingresa tu dominio con https (ej: `https://backyardpass.uy`).
3.  **Importante**: Coolify detectará automáticamente que debe enviar el tráfico al puerto `80` interno de ese contenedor. No necesitas mapear puertos manuales.

## 5. Cargar Variables de Entorno (Environment Variables) 🔐
Esta parte es crucial. Ve a la pestaña **Environment Variables** e importa las siguientes de forma masiva (Bulk Import):

```env
POSTGRES_DB=backyard_db
POSTGRES_USER=backyard_user
POSTGRES_PASSWORD=una_contraseña_segura_aqui
SECRET_KEY=genera_una_clave_larga_aleatoria
DEBUG=False
ALLOWED_HOSTS=tu-dominio.com,localhost
MP_ACCESS_TOKEN=tu_token_real_de_mercado_pago
VITE_API_URL=https://tu-dominio.com
```

## 6. Lanzar el Despliegue
1.  Haz clic en el botón **Deploy** en la parte superior derecha.
2.  Puedes seguir los logs de construcción. Se instalarán las dependencias de Python y se construirá el build de producción de React automáticamente.

## 7. Carga de Datos Iniciales (Usuarios y Eventos)
Una vez que todos los contenedores aparezcan como **Running**, debes inicializar los datos:
1.  Dentro del servicio, busca el contenedor **`backend`**.
2.  Ve a la pestaña **Terminal** del contenedor (o usa el botón "Execute Command").
3.  Ejecuta el siguiente comando para crear los usuarios Admin y Portero:
    ```bash
    python manage.py poblar_datos
    ```

## 8. Mantenimiento y Logs
*   **Worker**: El servicio `worker` ya está corriendo y limpiará el stock de compras no pagadas cada 60 segundos.
*   **Mailpit**: Puedes mapear un dominio a `mailpit` si quieres ver los correos salientes en producción (puerto 8025).
*   **Actualizaciones**: Cada vez que hagas un `git push` a tu rama `main`, puedes darle a **Redeploy** en Coolify para aplicar los cambios.

---
**Backyard Bar Pass System** - *Ready for the night.*
