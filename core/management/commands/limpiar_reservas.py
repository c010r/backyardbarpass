"""
Comando de administración para limpiar reservas expiradas.
Libera el stock de los lotes y marca las órdenes como EXPIRADO.
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import transaction
from core.models import Orden, Lote
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Busca órdenes PENDIENTE que superaron el tiempo límite y libera el stock.'

    def handle(self, *args, **options):
        # 1. Buscar órdenes pendientes cuya fecha de expiración ya pasó
        ordenes_a_vencer = Orden.objects.filter(
            estado='PENDIENTE',
            fecha_expiracion__lt=timezone.now()
        )

        total = ordenes_a_vencer.count()
        if total == 0:
            self.stdout.write(self.style.SUCCESS('No hay órdenes expiradas por procesar.'))
            return

        self.stdout.write(f'Procesando {total} órdenes expiradas...')

        proceso_exitoso = 0
        
        for orden in ordenes_a_vencer:
            try:
                # Usamos transacción atómica por cada orden para asegurar consistencia
                with transaction.atomic():
                    # Bloqueamos la orden y el lote para la actualización
                    orden_bloqueada = Orden.objects.select_for_update().get(id=orden.id)
                    
                    # Verificamos de nuevo el estado por si acaso cambió hace milisegundos
                    if orden_bloqueada.estado != 'PENDIENTE':
                        continue
                    
                    # 1. Marcar como EXPIRADO
                    orden_bloqueada.estado = 'EXPIRADO'
                    orden_bloqueada.save()

                    # 2. Devolver Stock al Lote
                    lote = Lote.objects.select_for_update().get(id=orden_bloqueada.lote.id)
                    lote.cantidad_vendida -= orden_bloqueada.cantidad_entradas
                    lote.save()

                    proceso_exitoso += 1
                    logger.info(f"Orden {orden.id} expirada y stock liberado (+{orden.cantidad_entradas}).")
            
            except Exception as e:
                self.stderr.write(self.style.ERROR(f'Error procesando orden {orden.id}: {str(e)}'))

        self.stdout.write(self.style.SUCCESS(f'Proceso finalizado. Total: {proceso_exitoso}/{total} órdenes expiradas.'))
