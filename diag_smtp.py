import os
import django
from django.core.mail import send_mail
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backyard_bar.settings')
django.setup()

def test_smtp():
    print(f"--- Probando Conexión SMTP ---")
    print(f"Host: {settings.EMAIL_HOST}")
    print(f"Puerto: {settings.EMAIL_PORT}")
    print(f"Usuario: {settings.EMAIL_HOST_USER}")
    print(f"Remitente: {settings.DEFAULT_FROM_EMAIL}")
    
    try:
        sent = send_mail(
            'Test Conexión Backyard',
            'Si ves esto, el SMTP de Brevo funciona correctamente.',
            settings.DEFAULT_FROM_EMAIL,
            ['backyard.bar.765@gmail.com'],
            fail_silently=False,
        )
        if sent:
            print("\n✅ ¡ÉXITO! El mail fue aceptado por el servidor de Brevo.")
        else:
            print("\n❌ El mail no se envió (pero no dio error).")
    except Exception as e:
        print(f"\n❌ ERROR DE SMTP: {str(e)}")

if __name__ == "__main__":
    test_smtp()
