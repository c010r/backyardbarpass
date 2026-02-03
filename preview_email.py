import os
import django
from django.template.loader import render_to_string
from django.conf import settings
from datetime import date

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backyard_bar.settings')
django.setup()

def generate_preview():
    # Datos de prueba para el template
    context = {
        'cliente': {'nombre': 'Usuario de Prueba'},
        'evento': {
            'titulo': 'BACKYARD - OPENING SEASON',
            'fecha_inicio': date(2026, 2, 14),
            'ubicacion': 'Parque Rodó, Montevideo'
        },
        'orden': {
            'id': 'ORD-12345',
            'lote': {'nombre': 'Early Bird'},
            'cantidad_entradas': 2
        },
        'entradas_con_cid': [
            {
                'cid': 'qr_1',
                'id_resumido': 'B1C2D3E4',
            },
            {
                'cid': 'qr_2',
                'id_resumido': 'F5G6H7I8',
            }
        ],
        'frontend_url': 'http://localhost:5173'
    }

    # Renderizar
    html_content = render_to_string('emails/confirmacion_entrada.html', context)
    
    # Reemplazar CIDs por una imagen de QR de ejemplo para que se vea en el browser
    example_qr = "https://api.qrserver.com/v1/create-qr-code/?size=200x200&data=Example"
    html_content = html_content.replace('cid:qr_1', example_qr)
    html_content = html_content.replace('cid:qr_2', example_qr)

    # Guardar archivo
    output_path = os.path.join(os.getcwd(), 'email_preview.html')
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"✅ Previsualización generada en: {output_path}")
    print("Podés abrir este archivo con tu navegador para ver el diseño.")

if __name__ == "__main__":
    generate_preview()
