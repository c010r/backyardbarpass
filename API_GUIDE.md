# 🎫 Backyard Bar Pass - API Backend

Este es el sistema backend para la venta de entradas de **Backyard Bar**. Desarrollado con Django REST Framework, integrando Mercado Pago y seguridad transaccional.

## 🚀 Inicio Rápido

1. **Entorno Virtual:** `.\venv\Scripts\activate` (Windows)
2. **Servidor:** `python manage.py runserver`
3. **Poblar Datos:** `python manage.py poblar_datos` (Si la DB está vacía)

---

## 🔐 Autenticación (Clientes)

El sistema usa **JWT (JSON Web Tokens)**.

| Endpoint | Método | Descripción | Auth |
|----------|--------|-------------|------|
| `/api/auth/registro/` | POST | Registra un nuevo comprador | Libre |
| `/api/auth/login/` | POST | Login de cliente (devuelve Token) | Libre |

---

## 📅 Eventos y Lotes

| Endpoint | Método | Descripción | Auth |
|----------|--------|-------------|------|
| `/api/eventos/` | GET | Listado de eventos activos | Libre |
| `/api/eventos/{id}/` | GET | Detalle del evento con sus lotes | Libre |

---

## 🛒 Proceso de Compra

1. **Reservar:** `POST /api/compras/reservar/`
   * Body: `{"evento_id": 1, "cantidad": 2}`
   * Devuelve: `mp_preference_id`.
   
2. **Pago:** El frontend debe usar el `mp_preference_id` para abrir el checkout de Mercado Pago.
3. **Confirmación:** Mercado Pago avisará a nuestro Webhook (`/api/pagos/webhook/`) y se generarán los QRs.

---

## 🎟️ Mis Entradas

| Endpoint | Método | Descripción | Auth |
|----------|--------|-------------|------|
| `/api/mis-entradas/` | GET | Ver mis tickets comprados y sus QRs | JWT |

---

## 🛡️ Staff / Portería (Admin)

Para validar entradas en la puerta, se usa el usuario de staff:
* **Endpoint:** `POST /api/staff/validar-qr/`
* **Body:** `{"codigo_qr": "UUID-DE-LA-ENTRADA"}`
* **Auth:** JWT de un usuario Staff.

---

## 🧹 Tareas de Mantenimiento

Para liberar stock de reservas que nunca se pagaron:
```bash
python manage.py limpiar_reservas
```
*(Se recomienda configurar esto como un CRON job cada 15 min)*
