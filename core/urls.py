"""
Rutas de la API para Backyard Bar.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    RegistroClienteView, LoginClienteView, EventoViewSet,
    CompraEntradaView, MisEntradasView, MercadoPagoWebhookView,
    ValidarEntradaView, ConfirmarPagoManualView, DashboardStatsView,
    ExportGuestListView
)

router = DefaultRouter()
router.register(r'eventos', EventoViewSet, basename='evento')

urlpatterns = [
    # Router (Eventos)
    path('', include(router.urls)),
    
    # Autenticación Clientes
    path('auth/registro/', RegistroClienteView.as_view(), name='cliente-registro'),
    path('auth/login/', LoginClienteView.as_view(), name='cliente-login'),
    
    # Compras y Mis Entradas
    path('compras/reservar/', CompraEntradaView.as_view(), name='comprar-entrada'),
    path('mis-entradas/', MisEntradasView.as_view(), name='mis-entradas'),
    
    # Mercado Pago
    path('pagos/webhook/', MercadoPagoWebhookView.as_view(), name='mp-webhook'),
    path('pagos/confirmar-interactivo/', ConfirmarPagoManualView.as_view(), name='mp-confirmar-manual'),
    
    # Validación (Portería)
    path('staff/validar-qr/', ValidarEntradaView.as_view(), name='validar-qr'),
    # Dashboard y Exportación
    path('staff/stats/', DashboardStatsView.as_view(), name='dashboard-stats'),
    path('staff/export-csv/<int:evento_id>/', ExportGuestListView.as_view(), name='export-guest-list'),
]
