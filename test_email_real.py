import os
import django
import uuid
from django.utils import timezone

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backyard_bar.settings')
django.setup()

from core.models import Cliente, Lote, Evento, Orden
from core.services_compra import confirmar_pago_orden

def run_test():
    try:
        # 1. Obtener o crear cliente de prueba
        email = 'backyard.bar.765@gmail.com'
        from datetime import date
        cliente, _ = Cliente.objects.get_or_create(
            email=email, 
            defaults={
                'nombre': 'Test Admin', 
                'apellido': 'Backyard',
                'cedula': str(uuid.uuid4().hex[:8]),
                'fecha_nacimiento': date(1990, 1, 1),
                'telefono': '099000000',
                'password': 'pbkdf2_sha256$260000$...' # password generic hash
            }
        )
        
        # 2. Obtener evento y lote
        evento = Evento.objects.first()
        lote = Lote.objects.filter(evento=evento).first()
        
        if not lote:
            print("Error: No hay lotes disponibles para el test.")
            return

        # 3. Crear orden pendiente
        orden = Orden.objects.create(
            cliente=cliente,
            evento=evento,
            lote=lote,
            cantidad_entradas=1,
            monto_subtotal=30,
            monto_total=30,
            estado='PENDIENTE'
        )
        print(f"Orden de prueba #{orden.id} creada exitosamente.")

        # 4. Simular confirmación de pago (esto dispara el email)
        print("Enviando email de prueba via Brevo...")
        confirmar_pago_orden(orden.id, f"TEST_PAYMENT_{uuid.uuid4().hex[:6]}")
        
        print("\n--------------------------------------------------")
        print("✅ PRUEBA COMPLETADA CON ÉXITO")
        print(f"Destinatario: {email}")
        print("Revisa tu bandeja de entrada (y la carpeta de SPAM).")
        print("--------------------------------------------------")

    except Exception as e:
        print(f"\n❌ ERROR DURANTE LA PRUEBA: {str(e)}")

if __name__ == "__main__":
    run_test()
