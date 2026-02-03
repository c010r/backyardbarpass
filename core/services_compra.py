"""
Servicios de negocio para el proceso de compra en Backyard Bar.
Maneja la lógica transaccional, reserva de stock y comunicación con Mercado Pago.
"""

import mercadopago
from django.db import transaction
from django.utils import timezone
from django.conf import settings
from django.core.exceptions import ValidationError
from .models import Evento, Lote, Orden, Cliente, Entrada
from .utils import generar_qr_entrada, enviar_email_entradas
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)

def crear_preferencia_mercadopago(orden):
    """
    Genera una preferencia de pago en Mercado Pago para una orden específica.
    """
    try:
        sdk = mercadopago.SDK(settings.MP_ACCESS_TOKEN)
        
        # Estructura del item para Mercado Pago
        # Nos aseguramos de que unit_price sea float y no tenga demasiados decimales
        unit_price = round(float(orden.monto_total / orden.cantidad_entradas), 2)
        
        item_data = {
            "id": str(orden.lote.id),
            "title": f"Entrada: {orden.evento.titulo}",
            "description": f"Acceso a {orden.evento.titulo} - Lote: {orden.lote.nombre}",
            "category_id": "events",
            "quantity": orden.cantidad_entradas,
            "unit_price": unit_price,
            "currency_id": "UYU"
        }

        # DETERMINAR URLS DE RETORNO (Usa FRONTEND_URL si existe, sino usa BASE_URL)
        # En producción esto debería ser la URL del frontend
        base_url_retorno = getattr(settings, 'FRONTEND_URL', settings.BASE_URL)
        if base_url_retorno.endswith('/'):
            base_url_retorno = base_url_retorno[:-1]

        preference_data = {
            "items": [item_data],
            "payer": {
                "name": orden.cliente.nombre,
                "surname": orden.cliente.apellido,
                "email": orden.cliente.email,
            },
            "back_urls": {
                "success": f"{base_url_retorno}/compra/exito",
                "failure": f"{base_url_retorno}/compra/fallo",
                "pending": f"{base_url_retorno}/compra/pendiente"
            },
            # auto_return SOLAMENTE funciona con HTTPS en algunas versiones de la API/Regiones
            # Lo habilitamos solo si la URL es HTTPS para evitar errores 400 en localhost
            "auto_return": "approved" if base_url_retorno.startswith('https') else "",
            "external_reference": str(orden.id),
            "binary_mode": True, # Para que sea Aprobado o Rechazado, sin estados intermedios raros
        }

        # Comentamos notification_url si es localhost ya que MP puede dar error 400
        if not "localhost" in settings.BASE_URL and not "127.0.0.1" in settings.BASE_URL:
            preference_data["notification_url"] = f"{settings.BASE_URL}/api/pagos/webhook/"

        preference_result = sdk.preference().create(preference_data)
        
        if preference_result["status"] == 201:
            return {
                "id": preference_result["response"]["id"],
                "init_point": preference_result["response"]["init_point"]
            }
        else:
            print(f"--- ERROR MERCADO PAGO ---")
            print(f"Status: {preference_result['status']}")
            print(f"Response: {preference_result['response']}")
            logger.error(f"Error al crear preferencia MP: {preference_result}")
            return None

    except Exception as e:
        logger.error(f"Excepción en crear_preferencia_mercadopago: {str(e)}")
        return None


@transaction.atomic
def procesar_reserva_entrada(cliente_id, evento_id, cantidad):
    """
    Lógica de reserva con bloqueo de base de datos para evitar overselling.
    Sigue el orden de lotes (escalonado).
    """
    # 1. Obtener cliente y evento
    try:
        cliente = Cliente.objects.get(id=cliente_id)
        evento = Evento.objects.select_related().get(id=evento_id, activo=True)
    except (Cliente.DoesNotExist, Evento.DoesNotExist):
        raise ValidationError("Cliente o Evento no encontrado o inactivo.")

    # 2. Buscar lotes con stock disponible usando SELECT FOR UPDATE
    # Esto bloquea las filas de los lotes para que otros procesos esperen hasta que termine esta transacción
    lotes_disponibles = Lote.objects.select_for_update().filter(
        evento=evento, 
        activo=True
    ).order_by('orden')

    lote_seleccionado = None
    
    # 3. Iterar lotes para encontrar uno que tenga stock suficiente para el pedido COMPLETO
    for lote in lotes_disponibles:
        if lote.stock_disponible >= cantidad:
            lote_seleccionado = lote
            break
    
    if not lote_seleccionado:
        raise ValidationError("No hay stock disponible en ningún lote para la cantidad solicitada.")

    # 4. Cálculos de montos
    monto_subtotal = lote_seleccionado.precio * cantidad
    monto_comision = 0
    if evento.cobra_comision:
        monto_comision = evento.valor_comision * cantidad
    
    monto_total = monto_subtotal + monto_comision

    # 5. Actualizar cantidad vendida del lote (reserva de stock)
    lote_seleccionado.cantidad_vendida += cantidad
    lote_seleccionado.save()

    # 6. Crear la Orden en estado PENDIENTE
    fecha_expiracion = timezone.now() + timedelta(minutes=settings.TIEMPO_EXPIRACION_RESERVA_MINUTOS)
    
    orden = Orden.objects.create(
        cliente=cliente,
        evento=evento,
        lote=lote_seleccionado,
        cantidad_entradas=cantidad,
        monto_subtotal=monto_subtotal,
        monto_comision=monto_comision,
        monto_total=monto_total,
        estado='PENDIENTE',
        fecha_expiracion=fecha_expiracion
    )

    # 7. Generar preferencia de Mercado Pago
    mp_pref_data = crear_preferencia_mercadopago(orden)
    
    if mp_pref_data:
        orden.mp_preference_id = mp_pref_data["id"]
        # Guardamos el init_point en un atributo volátil para el serializer si queremos, 
        # o lo manejamos en la vista
        orden.save()
        # Agregamos el init_point al objeto para que el serializer lo tome (si lo configuramos)
        orden.mp_init_point = mp_pref_data["init_point"]
    else:
        # Si falla MP, lanzamos error para que el @transaction.atomic haga rollback del stock
        raise Exception("Error al conectar con la pasarela de pagos. Stock liberado.")

    return orden


@transaction.atomic
def confirmar_pago_orden(orden_id, mp_payment_id):
    """
    Cambia el estado de una orden a APROBADO y genera las entradas con QR.
    """
    try:
        # Bloqueamos la orden para evitar procesamientos duplicados por webhooks simultáneos
        orden = Orden.objects.select_for_update().get(id=orden_id)
        
        if orden.estado == 'APROBADO':
            return orden # Ya procesada anteriormente

        orden.estado = 'APROBADO'
        orden.mp_payment_id = mp_payment_id
        orden.fecha_aprobacion = timezone.now()
        orden.save()

        # Generar las Entradas individuales
        for _ in range(orden.cantidad_entradas):
            entrada = Entrada.objects.create(
                orden=orden,
                cliente=orden.cliente,
                lote=orden.lote
            )
            # Generar y guardar el QR
            qr_file = generar_qr_entrada(entrada.id)
            entrada.imagen_qr.save(f"qr_{entrada.id}.png", qr_file, save=True)
        
        # Enviar email al cliente con los QRs
        enviar_email_entradas(orden)
        
        logger.info(f"Orden {orden.id} aprobada. Entradas y QRs generados y enviados por email.")
        return orden

    except Orden.DoesNotExist:
        logger.error(f"Intento de confirmar pago para orden inexistente: {orden_id}")
        return None


@transaction.atomic
def fallar_orden(orden_id):
    """
    Maneja el rechazo de un pago o expiración. Libera el stock.
    """
    try:
        orden = Orden.objects.select_for_update().get(id=orden_id)
        
        if orden.estado in ['RECHAZADO', 'EXPIRADO']:
            return orden # Ya fallida

        # Cambiamos el estado (por defecto RECHAZADO, el comando de limpieza usará EXPIRADO)
        orden.estado = 'RECHAZADO'
        orden.save()

        # LIBERAR STOCK: Restamos de cantidad_vendida del lote
        lote = Lote.objects.select_for_update().get(id=orden.lote.id)
        lote.cantidad_vendida -= orden.cantidad_entradas
        lote.save()

        logger.info(f"Orden {orden.id} rechazada. Stock {orden.cantidad_entradas} liberado para lote {lote.id}.")
        return orden

    except Orden.DoesNotExist:
        return None
