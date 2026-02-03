"""
Modelos de datos para Backyard Bar.
Sistema de venta de entradas con precios escalonados (Lotes) e integración con Mercado Pago.

MÓDULOS:
- Usuarios: Cliente (compradores finales, autenticación independiente)
- Eventos: Evento, Lote (sistema de precios escalonados)
- Ventas: Orden (reservas y pagos), Entrada (tickets finales con QR)
"""

from django.db import models
from django.contrib.auth.hashers import make_password, check_password
import uuid
from django.utils import timezone


# ===================================
# MÓDULO DE USUARIOS
# ===================================

class Cliente(models.Model):
    """
    Compradores finales del sitio.
    Autenticación independiente de django.contrib.auth.User
    El modelo User de Django se reserva SOLO para Staff (Admins y Porteros).
    """
    id = models.AutoField(primary_key=True)
    cedula = models.CharField(max_length=20, unique=True, db_index=True, verbose_name="Cédula")
    nombre = models.CharField(max_length=100, verbose_name="Nombre")
    apellido = models.CharField(max_length=100, verbose_name="Apellido")
    fecha_nacimiento = models.DateField(verbose_name="Fecha de Nacimiento")
    email = models.EmailField(unique=True, db_index=True, verbose_name="Email")
    telefono = models.CharField(max_length=20, verbose_name="Teléfono")
    password = models.CharField(max_length=128, verbose_name="Contraseña")  # Almacena hash
    fecha_registro = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Registro")

    class Meta:
        verbose_name = "Cliente"
        verbose_name_plural = "Clientes"
        ordering = ['-fecha_registro']

    def __str__(self):
        return f"{self.nombre} {self.apellido} ({self.cedula})"
    
    def set_password(self, raw_password):
        """Hashea y guarda la contraseña"""
        self.password = make_password(raw_password)
    
    def check_password(self, raw_password):
        """Verifica si la contraseña es correcta"""
        return check_password(raw_password, self.password)


# ===================================
# MÓDULO DE EVENTOS
# ===================================

class Evento(models.Model):
    """
    Evento donde se venden entradas.
    Puede tener múltiples lotes de precios escalonados.
    """
    id = models.AutoField(primary_key=True)
    titulo = models.CharField(max_length=200, verbose_name="Título")
    descripcion = models.TextField(blank=True, null=True, verbose_name="Descripción")
    fecha_inicio = models.DateTimeField(verbose_name="Fecha de Inicio")
    ubicacion = models.CharField(max_length=255, verbose_name="Ubicación")
    imagen = models.ImageField(upload_to='eventos/', blank=True, null=True, verbose_name="Imagen")
    activo = models.BooleanField(default=True, verbose_name="Activo")
    
    # Control de comisiones
    cobra_comision = models.BooleanField(default=False, verbose_name="Cobra Comisión")
    valor_comision = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0,
        verbose_name="Valor de Comisión"
    )
    
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")
    fecha_modificacion = models.DateTimeField(auto_now=True, verbose_name="Fecha de Modificación")

    class Meta:
        verbose_name = "Evento"
        verbose_name_plural = "Eventos"
        ordering = ['fecha_inicio']

    def __str__(self):
        return self.titulo
    
    @property
    def stock_total_disponible(self):
        """Retorna el stock total disponible sumando todos los lotes activos"""
        return sum(lote.stock_disponible for lote in self.lotes.filter(activo=True))


class Lote(models.Model):
    """
    Lógica de precios escalonados (Tiered Pricing).
    Ejemplo: Lote 1 (Early Bird - $100) -> Lote 2 (General - $150) -> Lote 3 (VIP - $200)
    
    IMPORTANTE: cantidad_vendida incluye las reservas PENDIENTES que no han expirado.
    Esto evita overselling mientras el cliente completa el pago.
    """
    id = models.AutoField(primary_key=True)
    evento = models.ForeignKey(
        Evento, 
        related_name='lotes', 
        on_delete=models.CASCADE,
        verbose_name="Evento"
    )
    nombre = models.CharField(max_length=100, verbose_name="Nombre del Lote")
    precio = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Precio")
    cantidad_total = models.PositiveIntegerField(verbose_name="Cantidad Total")
    cantidad_vendida = models.PositiveIntegerField(default=0, verbose_name="Cantidad Vendida")
    orden = models.PositiveIntegerField(default=1, verbose_name="Orden")  # 1 se vende primero
    activo = models.BooleanField(default=True, verbose_name="Activo")
    
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")

    class Meta:
        verbose_name = "Lote"
        verbose_name_plural = "Lotes"
        ordering = ['evento', 'orden']
        unique_together = [['evento', 'orden']]

    def __str__(self):
        return f"{self.evento.titulo} - {self.nombre} (${self.precio})"
    
    @property
    def stock_disponible(self):
        """Calcula el stock disponible en tiempo real"""
        return self.cantidad_total - self.cantidad_vendida
    
    @property
    def porcentaje_vendido(self):
        """Retorna el porcentaje de entradas vendidas"""
        if self.cantidad_total == 0:
            return 0
        return (self.cantidad_vendida / self.cantidad_total) * 100


# ===================================
# MÓDULO DE VENTAS
# ===================================

class Orden(models.Model):
    """
    Representa una orden de compra.
    
    Estados:
    - PENDIENTE: Reserva activa, esperando pago (15 minutos)
    - APROBADO: Pago confirmado, se generaron las entradas
    - RECHAZADO: Pago fallido, stock liberado
    - EXPIRADO: Tiempo agotado, stock liberado automáticamente
    """
    ESTADOS = [
        ('PENDIENTE', 'Pendiente'),
        ('APROBADO', 'Aprobado'),
        ('RECHAZADO', 'Rechazado'),
        ('EXPIRADO', 'Expirado'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    cliente = models.ForeignKey(
        Cliente, 
        related_name='ordenes', 
        on_delete=models.PROTECT,
        verbose_name="Cliente"
    )
    evento = models.ForeignKey(
        Evento, 
        related_name='ordenes', 
        on_delete=models.PROTECT,
        verbose_name="Evento"
    )
    
    # IMPORTANTE: Guardamos qué lote se reservó y cuántas entradas
    # Esto permite devolver el stock al lote correcto si la orden expira
    lote = models.ForeignKey(
        Lote, 
        related_name='ordenes', 
        on_delete=models.PROTECT,
        verbose_name="Lote"
    )
    cantidad_entradas = models.PositiveIntegerField(default=1, verbose_name="Cantidad de Entradas")
    
    # Montos
    monto_subtotal = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Subtotal")
    monto_comision = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Comisión")
    monto_total = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Monto Total")
    
    estado = models.CharField(max_length=20, choices=ESTADOS, default='PENDIENTE', verbose_name="Estado")
    
    # Integración con Mercado Pago
    mp_preference_id = models.CharField(max_length=100, blank=True, null=True, verbose_name="Preference ID (MP)")
    mp_payment_id = models.CharField(max_length=100, blank=True, null=True, verbose_name="Payment ID (MP)")
    
    # Fechas
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")
    fecha_aprobacion = models.DateTimeField(null=True, blank=True, verbose_name="Fecha de Aprobación")
    fecha_expiracion = models.DateTimeField(null=True, blank=True, verbose_name="Fecha de Expiración")

    class Meta:
        verbose_name = "Orden"
        verbose_name_plural = "Órdenes"
        ordering = ['-fecha_creacion']

    def __str__(self):
        return f"Orden {self.id} - {self.cliente.nombre} - {self.estado}"
    
    @property
    def esta_expirada(self):
        """Verifica si la orden ya expiró"""
        if self.estado != 'PENDIENTE':
            return False
        if not self.fecha_expiracion:
            return False
        return timezone.now() > self.fecha_expiracion


class Entrada(models.Model):
    """
    Ticket final (QR) que se genera SOLO si la orden es APROBADA.
    Cada entrada es individual y puede ser validada independientemente.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    orden = models.ForeignKey(
        Orden, 
        related_name='entradas', 
        on_delete=models.CASCADE,
        verbose_name="Orden"
    )
    cliente = models.ForeignKey(
        Cliente, 
        related_name='entradas', 
        on_delete=models.PROTECT,
        verbose_name="Cliente"
    )
    lote = models.ForeignKey(
        Lote, 
        related_name='entradas', 
        on_delete=models.PROTECT,
        verbose_name="Lote"
    )
    
    # Control de uso
    usada = models.BooleanField(default=False, verbose_name="Usada")
    fecha_uso = models.DateTimeField(null=True, blank=True, verbose_name="Fecha de Uso")
    
    # Imagen del QR persistida
    imagen_qr = models.ImageField(upload_to='qrs/', blank=True, null=True, verbose_name="Imagen QR")
    
    usuario_validador = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Validado por",
        help_text="Usuario de staff que validó la entrada"
    )
    
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")

    class Meta:
        verbose_name = "Entrada"
        verbose_name_plural = "Entradas"
        ordering = ['-fecha_creacion']

    def __str__(self):
        return f"Entrada {self.id} - {self.cliente.nombre} - {'Usada' if self.usada else 'Disponible'}"
    
    @property
    def codigo_qr(self):
        """Retorna el código que se debe usar para generar el QR"""
        return str(self.id)
    
    def marcar_como_usada(self, usuario_validador=None):
        """Marca la entrada como usada"""
        self.usada = True
        self.fecha_uso = timezone.now()
        self.usuario_validador = usuario_validador
        self.save()
