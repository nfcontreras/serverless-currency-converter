#!/usr/bin/env python3
"""
Cliente de ejemplo para probar la API del historial de conversiones.
Reemplaza BASE_URL con tu URL de API Gateway después del despliegue.
"""

import json
import requests
from datetime import datetime, timezone

# ⚠️ CAMBIA ESTA URL POR TU URL DE API GATEWAY DESPUÉS DEL DESPLIEGUE
BASE_URL = "https://tu-api-gateway-url.amazonaws.com/dev"

class HistoryAPIClient:
    def __init__(self, base_url):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
    
    def get_history(self, limit=20):
        """GET /history - Obtener historial"""
        url = f"{self.base_url}/history"
        params = {'limit': limit} if limit != 20 else {}
        
        response = self.session.get(url, params=params)
        return response.json(), response.status_code
    
    def create_conversion(self, conversion_data):
        """POST /history - Crear conversión"""
        url = f"{self.base_url}/history"
        
        response = self.session.post(url, json=conversion_data)
        return response.json(), response.status_code
    
    def get_conversion_by_id(self, conversion_id):
        """GET /history/{id} - Obtener conversión por ID"""
        url = f"{self.base_url}/history/{conversion_id}"
        
        response = self.session.get(url)
        return response.json(), response.status_code
    
    def update_conversion(self, conversion_id, updates):
        """PUT /history/{id} - Actualizar conversión"""
        url = f"{self.base_url}/history/{conversion_id}"
        
        response = self.session.put(url, json=updates)
        return response.json(), response.status_code
    
    def delete_conversion(self, conversion_id):
        """DELETE /history/{id} - Eliminar conversión"""
        url = f"{self.base_url}/history/{conversion_id}"
        
        response = self.session.delete(url)
        return response.json(), response.status_code


def demo_crud_operations():
    """Demostración completa del CRUD"""
    client = HistoryAPIClient(BASE_URL)
    
    print("🚀 Demostración del CRUD de Historial de Conversiones\n")
    
    # 1. Obtener historial inicial
    print("1️⃣ Obteniendo historial inicial...")
    data, status = client.get_history(limit=5)
    print(f"Status: {status}")
    print(f"Registros encontrados: {len(data.get('history', []))}")
    print(f"Fuente: {data.get('source', 'unknown')}\n")
    
    # 2. Crear nueva conversión
    print("2️⃣ Creando nueva conversión...")
    new_conversion = {
        "from": "USD",
        "to": "EUR",
        "amount": 250,
        "result": 223.75,
        "rate": 0.895,
        "last_updated": datetime.now(timezone.utc).isoformat()
    }
    
    data, status = client.create_conversion(new_conversion)
    print(f"Status: {status}")
    print(f"Éxito: {data.get('success', False)}")
    if data.get('data'):
        created_id = data['data'].get('timestamp')
        print(f"ID creado: {created_id}")
    else:
        created_id = None
    print()
    
    # 3. Obtener la conversión creada por ID
    if created_id:
        print("3️⃣ Obteniendo conversión por ID...")
        data, status = client.get_conversion_by_id(created_id)
        print(f"Status: {status}")
        print(f"Éxito: {data.get('success', False)}")
        if data.get('conversion'):
            conv = data['conversion']
            print(f"Conversión: {conv['amount']} {conv['from']} -> {conv['result']} {conv['to']}")
        print()
        
        # 4. Actualizar la conversión
        print("4️⃣ Actualizando conversión...")
        updates = {
            "amount": 300,
            "result": 268.50
        }
        
        data, status = client.update_conversion(created_id, updates)
        print(f"Status: {status}")
        print(f"Éxito: {data.get('success', False)}")
        print(f"Mensaje: {data.get('message', '')}")
        print()
        
        # 5. Verificar la actualización
        print("5️⃣ Verificando actualización...")
        data, status = client.get_conversion_by_id(created_id)
        if data.get('conversion'):
            conv = data['conversion']
            print(f"Conversión actualizada: {conv['amount']} {conv['from']} -> {conv['result']} {conv['to']}")
            print(f"Última actualización: {conv.get('last_updated', 'N/A')}")
        print()
        
        # 6. Eliminar la conversión
        print("6️⃣ Eliminando conversión...")
        data, status = client.delete_conversion(created_id)
        print(f"Status: {status}")
        print(f"Éxito: {data.get('success', False)}")
        print(f"Mensaje: {data.get('message', '')}")
        print()
        
        # 7. Verificar eliminación
        print("7️⃣ Verificando eliminación...")
        data, status = client.get_conversion_by_id(created_id)
        print(f"Status: {status}")
        print(f"Encontrado: {data.get('conversion') is not None}")
        print()
    
    # 8. Obtener historial final
    print("8️⃣ Historial final...")
    data, status = client.get_history(limit=5)
    print(f"Status: {status}")
    print(f"Registros: {len(data.get('history', []))}")
    print()
    
    print("✅ Demostración completada!")


def test_error_cases():
    """Prueba casos de error"""
    client = HistoryAPIClient(BASE_URL)
    
    print("🧪 Probando casos de error...\n")
    
    # JSON inválido
    print("❌ Probando creación con datos inválidos...")
    data, status = client.create_conversion({"from": "USD"})  # Faltan campos
    print(f"Status esperado 400: {status}")
    print(f"Mensaje: {data.get('message', '')}\n")
    
    # ID inexistente
    print("❌ Probando obtener ID inexistente...")
    data, status = client.get_conversion_by_id("2000-01-01T00:00:00Z")
    print(f"Status esperado 404: {status}")
    print(f"Mensaje: {data.get('message', '')}\n")
    
    print("✅ Pruebas de error completadas!")


if __name__ == "__main__":
    if BASE_URL == "https://tu-api-gateway-url.amazonaws.com/dev":
        print("⚠️ IMPORTANTE: Actualiza BASE_URL con tu URL real de API Gateway")
        print("Después de hacer 'serverless deploy', actualiza la variable BASE_URL")
        print("y ejecuta este script nuevamente.\n")
    
    try:
        print("🔄 Intentando conectar con la API...\n")
        demo_crud_operations()
        print("\n" + "="*50 + "\n")
        test_error_cases()
        
    except requests.exceptions.ConnectionError:
        print("❌ Error de conexión. Verifica que:")
        print("1. Hayas hecho 'serverless deploy'")
        print("2. La URL de API Gateway sea correcta")
        print("3. Los endpoints estén disponibles")
        
    except Exception as e:
        print(f"❌ Error inesperado: {e}")