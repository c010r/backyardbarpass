
import os
import django
from decimal import Decimal

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backyard_bar.settings')
django.setup()

from core.models import Orden, Cliente, Evento, Lote
from core.services_compra import crear_preferencia_mercadopago

def test_actual_function():
    print("Probando crear_preferencia_mercadopago con datos reales...")
    
    # Obtener o crear datos de prueba
    cliente = Cliente.objects.first()
    evento = Evento.objects.first()
    lote = Lote.objects.filter(evento=evento).first()
    
    if not cliente or not evento or not lote:
        print("Faltan datos en la DB para probar.")
        return

    # Crear una orden de prueba (sin guardar si preferimos, pero el servicio espera el objeto)
    orden = Orden(
        cliente=cliente,
        evento=evento,
        lote=lote,
        cantidad_entradas=2,
        monto_subtotal=lote.precio * 2,
        monto_comision=Decimal('100.00'),
        monto_total=(lote.precio * 2) + Decimal('100.00'),
        estado='PENDIENTE'
    )
    # Necesitamos ID para external_reference
    import uuid
    orden.id = uuid.uuid4()
    
    pref_id = crear_preferencia_mercadopago(orden)
    if pref_id:
        print(f"ÉXITO: Preference ID = {pref_id}")
    else:
        print("FALLO: No se obtuvo Preference ID")

if __name__ == "__main__":
    test_actual_function()
