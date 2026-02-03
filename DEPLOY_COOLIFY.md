# Guía de Despliegue en Coolify - Backyard Bar Pass 🚀

Esta guía detalla los pasos para desplegar con dominios separados:
*   **Frontend**: `https://entradas.backyardbar.fun`
*   **Backend/API**: `https://api.backyardbar.fun`

## 1. Requisitos Previos
*   Dominio `backyardbar.fun` con subdominios `entradas` y `api` apuntando a la IP del VPS.

## 2. Configuración en Coolify
1.  **Nuevo Servicio**: Crea un servicio desde el repositorio GitHub.
2.  **Compose**: Usa el archivo `./docker-compose-coolify.yml`.
3.  **Dominios**:
    *   En el servicio **frontend**, asigna el dominio `https://entradas.backyardbar.fun`.
    *   En el servicio **backend**, asigna el dominio `https://api.backyardbar.fun`.

## 3. Variables de Entorno (Crucial)
Configura estas variables en la pestaña **Environment Variables** de Coolify:

```env
# URL de la API que usará el frontend para compilarse
VITE_API_URL=https://api.backyardbar.fun

# Configuración de seguridad de Django
ALLOWED_HOSTS=api.backyardbar.fun,localhost
CORS_ALLOWED_ORIGINS=https://entradas.backyardbar.fun
CSRF_TRUSTED_ORIGINS=https://entradas.backyardbar.fun,https://api.backyardbar.fun

# Base URL para Mercado Pago (Webhook)
BASE_URL=https://api.backyardbar.fun
```

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
