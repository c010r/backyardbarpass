from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, AuthenticationFailed
from django.conf import settings
from .models import Cliente
from django.contrib.auth.models import User

class DualJWTAuthentication(JWTAuthentication):
    """
    Autenticación personalizada para manejar dos tipos de usuarios:
    1. Staff (User de Django) -> Para validación de QRs y admin.
    2. Cliente (Modelo independiente) -> Para compras y ver entradas.
    """
    def get_user(self, validated_token):
        user_id = validated_token.get('user_id')
        
        if not user_id:
            raise InvalidToken("El token no contiene un ID de usuario válido.")

        # 1. Intentamos buscar en Staff (User original de Django)
        try:
            user = User.objects.get(id=user_id)
            if user.is_staff:
                return user
        except User.DoesNotExist:
            pass

        # 2. Si no es Staff, buscamos en nuestra tabla de Clientes
        try:
            cliente = Cliente.objects.get(id=user_id)
            # Para que DRF lo reconozca como autenticado, le "fingimos" algunas propiedades
            # ya que Cliente no hereda de AbstractUser.
            cliente.is_authenticated = True
            return cliente
        except Cliente.DoesNotExist:
            raise AuthenticationFailed("Usuario o Cliente no encontrado.", code='user_not_found')

        return None
