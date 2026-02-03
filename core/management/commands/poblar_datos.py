"""
Comando de administración para poblar la base de datos con datos de prueba reales para Backyard Bar.
Genera un Staff (Portero), Eventos y Lotes escalonados.
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from core.models import Evento, Lote, Cliente
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal

class Command(BaseCommand):
    help = 'Puebla la base de datos con datos de prueba iniciales.'

    def handle(self, *args, **options):
        self.stdout.write('Iniciando población de datos...')

        # 1. Crear Usuario de Staff (Portero) - Solo Staff, NO Superuser
        portero_user = User.objects.filter(username='portero').first()
        if not portero_user:
            User.objects.create_user(
                username='portero',
                email='portero@backyardbar.com',
                password='admin.portero123',
                is_staff=True,
                is_superuser=False
            )
            self.stdout.write(self.style.SUCCESS('Staff "portero" creado (pass: admin.portero123) - Permisos limitados'))
        else:
            # Asegurarnos de que NO sea superuser si ya existía
            portero_user.is_superuser = False
            portero_user.is_staff = True
            portero_user.save()
            self.stdout.write('El staff "portero" ya existe (se aseguraron permisos limitados).')

        # 2. Crear Eventos de Ejemplo
        evento1, created = Evento.objects.get_or_create(
            titulo='Backyard Summer Bash 2026',
            defaults={
                'descripcion': 'La fiesta más grande del verano en el patio de Backyard. DJ en vivo, barras premium y el mejor ambiente de la ciudad.',
                'fecha_inicio': timezone.now() + timedelta(days=30, hours=21),
                'ubicacion': 'Backyard Bar Garden - Montevideo',
                'activo': True,
                'cobra_comision': True,
                'valor_comision': Decimal('50.00')
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'Evento "{evento1.titulo}" creado.'))
            # Crear Lotes para el Evento 1
            Lote.objects.create(
                evento=evento1,
                nombre='Early Bird (Pre-venta 1)',
                precio=Decimal('450.00'),
                cantidad_total=50,
                orden=1
            )
            Lote.objects.create(
                evento=evento1,
                nombre='General (Pre-venta 2)',
                precio=Decimal('600.00'),
                cantidad_total=100,
                orden=2
            )
            Lote.objects.create(
                evento=evento1,
                nombre='VIP Individual',
                precio=Decimal('1200.00'),
                cantidad_total=30,
                orden=3
            )
            self.stdout.write(self.style.SUCCESS('Lotes para Evento 1 creados.'))

        evento2, created = Evento.objects.get_or_create(
            titulo='Noche de Jazz & Wine',
            defaults={
                'descripcion': 'Una velada íntima con los mejores exponentes del Jazz local acompañados de una selección premium de bodegas nacionales.',
                'fecha_inicio': timezone.now() + timedelta(days=15, hours=20),
                'ubicacion': 'Backyard Lounge',
                'activo': True,
                'cobra_comision': False,
                'valor_comision': Decimal('0.00')
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'Evento "{evento2.titulo}" creado.'))
            # Crear Lotes para el Evento 2
            Lote.objects.create(
                evento=evento2,
                nombre='Entrada General',
                precio=Decimal('850.00'),
                cantidad_total=80,
                orden=1
            )
            self.stdout.write(self.style.SUCCESS('Lote para Evento 2 creado.'))

        # 3. Crear un Cliente de prueba (opcional)
        cliente_test, created = Cliente.objects.get_or_create(
            email='cliente@ejemplo.com',
            defaults={
                'cedula': '12345678',
                'nombre': 'Juan',
                'apellido': 'Pérez',
                'fecha_nacimiento': '1995-05-20',
                'telefono': '099123456',
            }
        )
        if created:
            cliente_test.set_password('cliente123')
            cliente_test.save()
            self.stdout.write(self.style.SUCCESS('Cliente de prueba "Juan Pérez" creado (pass: cliente123)'))

        self.stdout.write(self.style.SUCCESS('Población de datos finalizada con éxito.'))
