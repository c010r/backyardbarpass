"""
Vistas de API para Backyard Bar.
Implementa autenticación de clientes, listado de eventos, reserva de entradas
y procesamiento de webhooks de Mercado Pago.
"""

from rest_framework import viewsets, status, views
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.shortcuts import get_object_or_404
from django.utils import timezone
from .models import Cliente, Evento, Lote, Orden, Entrada
from .serializers import (
    ClienteRegistroSerializer, ClienteSerializer, ClienteLoginSerializer,
    EventoListSerializer, EventoDetalleSerializer, CrearOrdenSerializer,
    OrdenSerializer, EntradaSerializer, ValidarEntradaSerializer, 
    EntradaValidacionSerializer
)
from .services_compra import procesar_reserva_entrada, confirmar_pago_orden, fallar_orden
import mercadopago
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

# ===================================
# AUTENTICACIÓN DE CLIENTES
# ===================================

class RegistroClienteView(views.APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = ClienteRegistroSerializer(data=request.data)
        if serializer.is_valid():
            cliente = serializer.save()
            refresh = RefreshToken.for_user(cliente)
            # Personalizamos el token para que use el ID de Cliente
            refresh['user_id'] = cliente.id
            
            return Response({
                "cliente": ClienteSerializer(cliente).data,
                "token": {
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                }
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginClienteView(views.APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = ClienteLoginSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']
            
            # 1. Intentar como Cliente
            try:
                cliente = Cliente.objects.get(email=email)
                if cliente.check_password(password):
                    refresh = RefreshToken.for_user(cliente)
                    refresh['user_id'] = cliente.id
                    refresh['is_staff'] = False
                    
                    return Response({
                        "cliente": ClienteSerializer(cliente).data,
                        "token": {
                            "refresh": str(refresh),
                            "access": str(refresh.access_token),
                        }
                    }, status=status.HTTP_200_OK)
            except Cliente.DoesNotExist:
                pass

            # 2. Intentar como Staff (User de Django)
            from django.contrib.auth import authenticate
            user = authenticate(username=email, password=password) # O login por email si está configurado
            if not user:
                # Si el username no funciona, intentamos buscar el User por email
                from django.contrib.auth.models import User
                try:
                    user_obj = User.objects.get(email=email)
                    user = authenticate(username=user_obj.username, password=password)
                except User.DoesNotExist:
                    user = None

            if user and user.is_staff:
                refresh = RefreshToken.for_user(user)
                refresh['user_id'] = user.id
                refresh['is_staff'] = True
                refresh['is_superuser'] = user.is_superuser # Añadido para diferenciar Dueño de Portero
                
                return Response({
                    "user": {
                        "id": user.id, 
                        "username": user.username, 
                        "is_staff": True,
                        "is_superuser": user.is_superuser
                    },
                    "token": {
                        "refresh": str(refresh),
                        "access": str(refresh.access_token),
                    }
                }, status=status.HTTP_200_OK)
            
            return Response({"error": "Credenciales inválidas"}, status=status.HTTP_401_UNAUTHORIZED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ===================================
# EVENTOS
# ===================================

class EventoViewSet(viewsets.ReadOnlyModelViewSet):
    """Listado y detalle de eventos (Público)"""
    queryset = Evento.objects.filter(activo=True)
    permission_classes = [AllowAny]

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return EventoDetalleSerializer
        return EventoListSerializer


# ===================================
# COMPRA Y ÓRDENES (Requiere Autenticación)
# ===================================

class CompraEntradaView(views.APIView):
    """Endpoint para iniciar la reserva y compra"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = CrearOrdenSerializer(data=request.data)
        if serializer.is_valid():
            try:
                # request.user ahora es el objeto Cliente gracias a DualJWTAuthentication
                cliente = request.user
                
                if not isinstance(cliente, Cliente):
                    return Response({"error": "Solo los clientes pueden comprar entradas"}, status=status.HTTP_403_FORBIDDEN)
                
                orden = procesar_reserva_entrada(
                    cliente_id=cliente.id,
                    evento_id=serializer.validated_data['evento_id'],
                    cantidad=serializer.validated_data['cantidad']
                )
                
                return Response(OrdenSerializer(orden).data, status=status.HTTP_201_CREATED)
            
            except Cliente.DoesNotExist:
                return Response({"error": "Cliente no identificado"}, status=status.HTTP_401_UNAUTHORIZED)
            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MisEntradasView(views.APIView):
    """Lista las entradas del cliente autenticado"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            cliente = request.user
            if not isinstance(cliente, Cliente):
                return Response({"error": "No eres un cliente válido"}, status=status.HTTP_403_FORBIDDEN)
                
            entradas = Entrada.objects.filter(cliente=cliente)
            return Response(EntradaSerializer(entradas, many=True).data)
        except Exception:
            return Response({"error": "No autorizado"}, status=status.HTTP_401_UNAUTHORIZED)


# ===================================
# WEBHOOK MERCADO PAGO
# ===================================

class MercadoPagoWebhookView(views.APIView):
    """
    Recibe notificaciones de Mercado Pago sobre cambios en el estado de los pagos.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        topic = request.query_params.get('topic') or request.data.get('type')
        resource_id = request.query_params.get('id') or (request.data.get('data', {}).get('id'))

        if topic == 'payment':
            sdk = mercadopago.SDK(settings.MP_ACCESS_TOKEN)
            payment_info = sdk.payment().get(resource_id)
            
            if payment_info["status"] == 200:
                payment_data = payment_info["response"]
                orden_id = payment_data.get('external_reference')
                status_pagos = payment_data.get('status')
                
                if status_pagos == 'approved':
                    confirmar_pago_orden(orden_id, resource_id)
                elif status_pagos in ['rejected', 'cancelled', 'refunded']:
                    fallar_orden(orden_id)
                
                return Response(status=status.HTTP_200_OK)
        
        return Response(status=status.HTTP_200_OK)


class ConfirmarPagoManualView(views.APIView):
    """
    Endpoint para que el frontend confirme el pago tras ser redirigido.
    Útil especialmente en desarrollo cuando los webhooks no llegan a localhost.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        payment_id = request.data.get('payment_id')
        
        if not payment_id:
            return Response({"error": "Falta payment_id"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Consultar estado en Mercado Pago
        try:
            sdk = mercadopago.SDK(settings.MP_ACCESS_TOKEN)
            payment_info = sdk.payment().get(payment_id)
            
            if payment_info["status"] == 200:
                payment_data = payment_info["response"]
                orden_id = payment_data.get('external_reference')
                status_pago = payment_data.get('status')
                
                if status_pago == 'approved':
                    orden = confirmar_pago_orden(orden_id, payment_id)
                    if orden:
                        return Response(OrdenSerializer(orden).data, status=status.HTTP_200_OK)
                    else:
                        return Response({"error": "No se pudo procesar la orden"}, status=status.HTTP_404_NOT_FOUND)
                else:
                    return Response({"error": f"El pago no está aprobado (Estado: {status_pago})"}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({"error": "No se pudo obtener información del pago"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error en ConfirmarPagoManualView: {str(e)}")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ===================================
# VALIDACIÓN DE ENTRADAS (STAFF)
# ===================================

class ValidarEntradaView(views.APIView):
    """Endpoint para que el portero valide el QR"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if not request.user.is_staff:
            return Response({"error": "Solo el staff puede validar entradas"}, status=status.HTTP_403_FORBIDDEN)
            
        serializer = ValidarEntradaSerializer(data=request.data)
        if serializer.is_valid():
            try:
                entrada = Entrada.objects.get(id=serializer.validated_data['codigo_qr'])
                
                if entrada.usada:
                    return Response({
                        "mensaje": "¡ALERTA! Esta entrada ya fue utilizada",
                        "es_valida": False,
                        "detalle": EntradaValidacionSerializer(entrada).data
                    }, status=status.HTTP_200_OK)
                
                entrada.marcar_como_usada(usuario_validador=request.user)
                
                return Response({
                    "mensaje": "Entrada validada correctamente",
                    "es_valida": True,
                    "detalle": EntradaValidacionSerializer(entrada).data
                }, status=status.HTTP_200_OK)
            except Entrada.DoesNotExist:
                return Response({"error": "QR no válido"}, status=status.HTTP_404_NOT_FOUND)
            
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DashboardStatsView(views.APIView):
    """
    Proporciona métricas generales para el panel de administración.
    Solo accesible para Staff.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not request.user.is_staff:
            return Response({"error": "No autorizado"}, status=status.HTTP_403_FORBIDDEN)

        eventos = Evento.objects.filter(activo=True)
        stats_eventos = []

        total_recaudado_global = 0

        for evento in eventos:
            ordenes_aprobadas = Orden.objects.filter(evento=evento, estado='APROBADO')
            entradas_vendidas = Entrada.objects.filter(lote__evento=evento)
            entradas_usadas = entradas_vendidas.filter(usada=True).count()
            
            recaudado_evento = sum(o.monto_total for o in ordenes_aprobadas)
            total_recaudado_global += recaudado_evento

            stats_eventos.append({
                "id": evento.id,
                "titulo": evento.titulo,
                "vendidas": entradas_vendidas.count(),
                "usadas": entradas_usadas,
                "recaudado": float(recaudado_evento),
                "stock_total": sum(l.cantidad_total for l in evento.lotes.all())
            })

        return Response({
            "total_eventos_activos": eventos.count(),
            "total_recaudado_global": float(total_recaudado_global),
            "eventos": stats_eventos
        }, status=status.HTTP_200_OK)


class ExportGuestListView(views.APIView):
    """
    Genera un archivo CSV con la lista de asistentes para un evento.
    Solo accesible para Staff.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, evento_id):
        if not request.user.is_staff:
            return Response({"error": "No autorizado"}, status=status.HTTP_403_FORBIDDEN)

        import csv
        from django.http import HttpResponse
        
        evento = get_object_or_404(Evento, id=evento_id)
        entradas = Entrada.objects.filter(lote__evento=evento).select_related('cliente', 'lote')

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="lista_{evento.titulo}_{timezone.now().date()}.csv"'

        writer = csv.writer(response)
        writer.writerow(['Ticket ID', 'Nombre', 'Apellido', 'Cédula', 'Email', 'Lote', 'Costo', 'Estado', 'Fecha Uso'])

        for e in entradas:
            writer.writerow([
                str(e.id)[:8].upper(),
                e.cliente.nombre,
                e.cliente.apellido,
                e.cliente.cedula,
                e.cliente.email,
                e.lote.nombre,
                e.lote.precio,
                'Ingresó' if e.usada else 'Pendiente',
                e.fecha_uso.strftime('%Y-%m-%d %H:%M') if e.fecha_uso else '-'
            ])

        return response
