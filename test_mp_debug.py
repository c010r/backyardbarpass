
import os
import django
from decimal import Decimal
import mercadopago

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backyard_bar.settings')
django.setup()

from django.conf import settings
from core.models import Orden, Cliente, Evento, Lote

def test_debug():
    sdk = mercadopago.SDK(settings.MP_ACCESS_TOKEN)
    cliente = Cliente.objects.first()
    evento = Evento.objects.first()
    lote = Lote.objects.filter(evento=evento).first()
    
    if not (cliente and evento and lote):
        print("Faltan datos")
        return

    item_data = {
        "title": f"Entrada: {evento.titulo} - {lote.nombre}",
        "quantity": 1,
        "unit_price": float(lote.precio),
        "currency_id": "UYU"
    }

    preference_data = {
        "items": [item_data],
        "payer": {
            "email": cliente.email,
        },
        "back_urls": {
            "success": "https://example.com/success",
            "failure": f"{settings.BASE_URL}/compra/fallo/",
            "pending": f"{settings.BASE_URL}/compra/pendiente/"
        },
        "auto_return": "approved",
        "external_reference": "test-uuid-123",
    }
    
    import json
    print("Enviando preferencia...")
    result = sdk.preference().create(preference_data)
    print(f"Status: {result['status']}")
    if result['status'] != 201:
        print(f"Error detail: {json.dumps(result['response'], indent=2)}")

if __name__ == "__main__":
    test_debug()
