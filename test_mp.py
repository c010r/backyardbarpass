import os
import mercadopago
from decouple import Config, RepositoryEnv

# Cargar .env manualmente para el test
env_path = 'c:/Users/avale/Desktop/dev/Backyard-Bar-Pass/.env'
config = Config(RepositoryEnv(env_path))

MP_ACCESS_TOKEN = config('MP_ACCESS_TOKEN')

def test_mp():
    print(f"Probando token: {MP_ACCESS_TOKEN[:15]}...")
    sdk = mercadopago.SDK(MP_ACCESS_TOKEN)
    
    preference_data = {
        "items": [
            {
                "title": "Test Item",
                "quantity": 1,
                "unit_price": 10.0,
                "currency_id": "UYU"
            }
        ]
    }
    
    result = sdk.preference().create(preference_data)
    print(f"Status: {result['status']}")
    print(f"Response: {result['response']}")

if __name__ == "__main__":
    test_mp()
