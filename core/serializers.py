"""
Serializers para la API REST de Backyard Bar.
Manejo de serialización/deserialización de datos con validaciones personalizadas.
"""

from rest_framework import serializers
from .models import Cliente, Evento, Lote, Orden, Entrada
from django.utils import timezone
from datetime import timedelta


# ===================================
# SERIALIZERS DE USUARIOS
# ===================================

class ClienteRegistroSerializer(serializers.ModelSerializer):
    """Serializer para el registro de nuevos clientes"""
    password_confirm = serializers.CharField(write_only=True, required=True)
    
    class Meta:
        model = Cliente
        fields = [
            'cedula', 'nombre', 'apellido', 'fecha_nacimiento',
            'email', 'telefono', 'password', 'password_confirm'
        ]
        extra_kwargs = {
            'password': {'write_only': True}
        }
    
    def validate_cedula(self, value):
        """Valida que la cédula tenga el formato correcto"""
        # Remover puntos y guiones
        cedula_limpia = value.replace('.', '').replace('-', '')
        if not cedula_limpia.isdigit():
            raise serializers.ValidationError("La cédula debe contener solo números.")
        if len(cedula_limpia) < 6 or len(cedula_limpia) > 8:
            raise serializers.ValidationError("La cédula debe tener entre 6 y 8 dígitos.")
        return value
    
    def validate_fecha_nacimiento(self, value):
        """Valida que el cliente sea mayor de edad (18 años)"""
        hoy = timezone.now().date()
        edad = hoy.year - value.year - ((hoy.month, hoy.day) < (value.month, value.day))
        if edad < 18:
            raise serializers.ValidationError("Debes ser mayor de 18 años para registrarte.")
        return value
    
    def validate(self, data):
        """Valida que las contraseñas coincidan"""
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError({"password": "Las contraseñas no coinciden."})
        return data
    
    def create(self, validated_data):
        """Crea el cliente con la contraseña hasheada"""
        validated_data.pop('password_confirm')
        cliente = Cliente(**validated_data)
        cliente.set_password(validated_data['password'])
        cliente.save()
        return cliente


class ClienteSerializer(serializers.ModelSerializer):
    """Serializer para mostrar información del cliente (sin contraseña)"""
    
    class Meta:
        model = Cliente
        fields = [
            'id', 'cedula', 'nombre', 'apellido', 'fecha_nacimiento',
            'email', 'telefono', 'fecha_registro'
        ]
        read_only_fields = ['id', 'fecha_registro']


class ClienteLoginSerializer(serializers.Serializer):
    """Serializer para el login de clientes o staff"""
    email = serializers.CharField(required=True) # Puede ser email o username
    password = serializers.CharField(required=True, write_only=True)


# ===================================
# SERIALIZERS DE EVENTOS Y LOTES
# ===================================

class LoteSerializer(serializers.ModelSerializer):
    """Serializer para los lotes de entradas"""
    stock_disponible = serializers.ReadOnlyField()
    porcentaje_vendido = serializers.ReadOnlyField()
    
    class Meta:
        model = Lote
        fields = [
            'id', 'nombre', 'precio', 'cantidad_total', 'cantidad_vendida',
            'stock_disponible', 'porcentaje_vendido', 'orden', 'activo'
        ]
        read_only_fields = ['id', 'cantidad_vendida']


class EventoListSerializer(serializers.ModelSerializer):
    """Serializer simplificado para listar eventos"""
    stock_total_disponible = serializers.ReadOnlyField()
    
    class Meta:
        model = Evento
        fields = [
            'id', 'titulo', 'fecha_inicio', 'ubicacion', 'imagen',
            'activo', 'stock_total_disponible'
        ]


class EventoDetalleSerializer(serializers.ModelSerializer):
    """Serializer completo para el detalle de un evento con sus lotes"""
    lotes = LoteSerializer(many=True, read_only=True)
    stock_total_disponible = serializers.ReadOnlyField()
    
    class Meta:
        model = Evento
        fields = [
            'id', 'titulo', 'descripcion', 'fecha_inicio', 'ubicacion',
            'imagen', 'activo', 'cobra_comision', 'valor_comision',
            'lotes', 'stock_total_disponible'
        ]


# ===================================
# SERIALIZERS DE ÓRDENES Y ENTRADAS
# ===================================

class CrearOrdenSerializer(serializers.Serializer):
    """Serializer para crear una nueva orden de compra"""
    evento_id = serializers.IntegerField(required=True)
    cantidad = serializers.IntegerField(required=True, min_value=1, max_value=10)
    
    def validate_cantidad(self, value):
        """Valida que la cantidad sea razonable"""
        if value > 10:
            raise serializers.ValidationError("No puedes comprar más de 10 entradas por orden.")
        return value
    
    def validate_evento_id(self, value):
        """Valida que el evento exista y esté activo"""
        try:
            evento = Evento.objects.get(id=value)
            if not evento.activo:
                raise serializers.ValidationError("Este evento no está disponible para venta.")
        except Evento.DoesNotExist:
            raise serializers.ValidationError("El evento especificado no existe.")
        return value


class EntradaSerializer(serializers.ModelSerializer):
    """Serializer para las entradas/tickets"""
    evento_titulo = serializers.CharField(source='lote.evento.titulo', read_only=True)
    lote_nombre = serializers.CharField(source='lote.nombre', read_only=True)
    codigo_qr = serializers.ReadOnlyField()
    
    class Meta:
        model = Entrada
        fields = [
            'id', 'evento_titulo', 'lote_nombre', 'usada', 'fecha_uso',
            'fecha_creacion', 'codigo_qr', 'imagen_qr'
        ]
        read_only_fields = ['id', 'usada', 'fecha_uso', 'fecha_creacion']


class OrdenSerializer(serializers.ModelSerializer):
    """Serializer para las órdenes de compra"""
    cliente = ClienteSerializer(read_only=True)
    evento = EventoListSerializer(read_only=True)
    lote = LoteSerializer(read_only=True)
    entradas = EntradaSerializer(many=True, read_only=True)
    esta_expirada = serializers.ReadOnlyField()
    mp_init_point = serializers.CharField(read_only=True, required=False)
    
    class Meta:
        model = Orden
        fields = [
            'id', 'cliente', 'evento', 'lote', 'cantidad_entradas',
            'monto_subtotal', 'monto_comision', 'monto_total',
            'estado', 'fecha_creacion', 'fecha_aprobacion',
            'fecha_expiracion', 'esta_expirada', 'entradas',
            'mp_preference_id', 'mp_init_point'
        ]
        read_only_fields = [
            'id', 'monto_subtotal', 'monto_comision', 'monto_total',
            'estado', 'fecha_creacion', 'fecha_aprobacion', 'fecha_expiracion'
        ]


class OrdenDetalleSerializer(serializers.ModelSerializer):
    """Serializer detallado para una orden específica con toda la información"""
    cliente_nombre = serializers.CharField(source='cliente.nombre', read_only=True)
    cliente_apellido = serializers.CharField(source='cliente.apellido', read_only=True)
    cliente_email = serializers.CharField(source='cliente.email', read_only=True)
    evento_titulo = serializers.CharField(source='evento.titulo', read_only=True)
    evento_fecha = serializers.DateTimeField(source='evento.fecha_inicio', read_only=True)
    evento_ubicacion = serializers.CharField(source='evento.ubicacion', read_only=True)
    lote_nombre = serializers.CharField(source='lote.nombre', read_only=True)
    entradas = EntradaSerializer(many=True, read_only=True)
    esta_expirada = serializers.ReadOnlyField()
    
    class Meta:
        model = Orden
        fields = [
            'id', 'cliente_nombre', 'cliente_apellido', 'cliente_email',
            'evento_titulo', 'evento_fecha', 'evento_ubicacion',
            'lote_nombre', 'cantidad_entradas',
            'monto_subtotal', 'monto_comision', 'monto_total',
            'estado', 'fecha_creacion', 'fecha_aprobacion',
            'fecha_expiracion', 'esta_expirada', 'entradas',
            'mp_preference_id', 'mp_payment_id'
        ]


# ===================================
# SERIALIZERS PARA VALIDACIÓN DE ENTRADAS (Staff)
# ===================================

class ValidarEntradaSerializer(serializers.Serializer):
    """Serializer para validar una entrada con código QR"""
    codigo_qr = serializers.UUIDField(required=True)
    
    def validate_codigo_qr(self, value):
        """Valida que el código QR exista"""
        try:
            entrada = Entrada.objects.get(id=value)
        except Entrada.DoesNotExist:
            raise serializers.ValidationError("El código QR no es válido.")
        return value


class EntradaValidacionSerializer(serializers.ModelSerializer):
    """Serializer completo para la respuesta de validación de entrada"""
    cliente_nombre = serializers.CharField(source='cliente.nombre', read_only=True)
    cliente_apellido = serializers.CharField(source='cliente.apellido', read_only=True)
    evento_titulo = serializers.CharField(source='lote.evento.titulo', read_only=True)
    evento_fecha = serializers.DateTimeField(source='lote.evento.fecha_inicio', read_only=True)
    lote_nombre = serializers.CharField(source='lote.nombre', read_only=True)
    validador_username = serializers.CharField(source='usuario_validador.username', read_only=True)
    
    class Meta:
        model = Entrada
        fields = [
            'id', 'cliente_nombre', 'cliente_apellido',
            'evento_titulo', 'evento_fecha', 'lote_nombre',
            'usada', 'fecha_uso', 'validador_username', 'fecha_creacion'
        ]
