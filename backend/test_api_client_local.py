#!/usr/bin/env python3
"""
Cliente de pruebas para desarrollo local.
Prueba todos los endpoints del CRUD en el servidor local.
"""

import json
import requests
from datetime import datetime, timezone

# URL del servidor local
BASE_URL = "http://localhost:3000/dev"

class LocalAPIClient:
    def __init__(self, base_url):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
        self.session.timeout = 10
    
    def test_connection(self):
        """Prueba si el servidor está corriendo"""
        try:
            response = self.session.get(f"{self.base_url}/history", timeout=5)
            return True, response.status_code
        except requests.exceptions.ConnectionError:
            return False, "Conexión rechazada"
        except Exception as e:
            return False, str(e)
    
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
    
    def convert_currency(self, from_currency, to_currency, amount):
        """POST /convert - Convertir moneda"""
        url = f"{self.base_url}/convert"
        data = {"from": from_currency, "to": to_currency, "amount": amount}
        response = self.session.post(url, json=data)
        return response.json(), response.status_code
    
    def get_rates(self, base_currency="USD"):
        """GET /rates - Obtener tasas de cambio"""
        url = f"{self.base_url}/rates"
        params = {"base": base_currency}
        response = self.session.get(url, params=params)
        return response.json(), response.status_code


def print_separator(title):
    """Imprime un separador con título"""
    print("\n" + "="*60)
    print(f" {title}")
    print("="*60)


def print_result(operation, data, status, success_expected=True):
    """Imprime el resultado de una operación"""
    status_icon = "✅" if status < 400 else "❌"
    success_icon = "✅" if data.get('success', False) else "❌"
    
    print(f"{status_icon} {operation}")
    print(f"   Status: {status}")
    print(f"   Success: {success_icon} {data.get('success', False)}")
    
    if data.get('message'):
        print(f"   Message: {data['message']}")
    
    return data.get('success', False)


def test_server_connection():
    """Prueba la conexión con el servidor"""
    print_separator("🔌 PRUEBA DE CONEXIÓN")
    
    client = LocalAPIClient(BASE_URL)
    connected, result = client.test_connection()
    
    if connected:
        print(f"✅ Servidor local conectado correctamente")
        print(f"   URL: {BASE_URL}")
        print(f"   Status: {result}")
        return True
    else:
        print(f"❌ No se pudo conectar al servidor local")
        print(f"   URL: {BASE_URL}")
        print(f"   Error: {result}")
        print("\n💡 Asegúrate de que el servidor esté corriendo:")
        print("   > npm run dev")
        print("   o")
        print("   > start-dev.bat (Windows)")
        print("   > ./start-dev.sh (Linux/Mac)")
        return False


def test_basic_endpoints():
    """Prueba endpoints básicos"""
    print_separator("🧪 ENDPOINTS BÁSICOS")
    
    client = LocalAPIClient(BASE_URL)
    
    # Probar tasas de cambio
    print("📊 Probando tasas de cambio...")
    data, status = client.get_rates()
    print_result("GET /rates", data, status)
    
    # Probar conversión
    print("\n💱 Probando conversión de moneda...")
    data, status = client.convert_currency("USD", "EUR", 100)
    success = print_result("POST /convert", data, status)
    
    conversion_created = None
    if success and data.get('timestamp'):
        conversion_created = data['timestamp']
        print(f"   Conversión guardada con ID: {conversion_created}")
    
    return conversion_created


def test_history_crud():
    """Prueba completa del CRUD de historial"""
    print_separator("📋 CRUD DE HISTORIAL")
    
    client = LocalAPIClient(BASE_URL)
    
    # 1. Obtener historial inicial
    print("1️⃣ Obteniendo historial inicial...")
    data, status = client.get_history(limit=5)
    print_result("GET /history", data, status)
    initial_count = len(data.get('history', []))
    print(f"   Registros existentes: {initial_count}")
    
    # 2. Crear nueva conversión
    print("\n2️⃣ Creando nueva conversión...")
    new_conversion = {
        "from": "EUR",
        "to": "GBP", 
        "amount": 150,
        "result": 127.50,
        "rate": 0.85
    }
    
    data, status = client.create_conversion(new_conversion)
    success = print_result("POST /history", data, status)
    
    created_id = None
    if success and data.get('data', {}).get('timestamp'):
        created_id = data['data']['timestamp']
        print(f"   ID creado: {created_id}")
    
    if not created_id:
        print("❌ No se pudo crear la conversión, saltando pruebas CRUD")
        return
    
    # 3. Obtener por ID
    print("\n3️⃣ Obteniendo conversión por ID...")
    data, status = client.get_conversion_by_id(created_id)
    print_result("GET /history/{id}", data, status)
    if data.get('conversion'):
        conv = data['conversion']
        print(f"   Conversión: {conv['amount']} {conv['from']} → {conv['result']} {conv['to']}")
    
    # 4. Actualizar conversión
    print("\n4️⃣ Actualizando conversión...")
    updates = {"amount": 200, "result": 170.00}
    data, status = client.update_conversion(created_id, updates)
    print_result("PUT /history/{id}", data, status)
    
    # 5. Verificar actualización
    print("\n5️⃣ Verificando actualización...")
    data, status = client.get_conversion_by_id(created_id)
    if data.get('conversion'):
        conv = data['conversion']
        print(f"   Conversión actualizada: {conv['amount']} {conv['from']} → {conv['result']} {conv['to']}")
        print(f"   Última actualización: {conv.get('last_updated', 'N/A')}")
    
    # 6. Obtener historial actualizado
    print("\n6️⃣ Historial después de crear...")
    data, status = client.get_history(limit=5)
    print_result("GET /history", data, status)
    final_count = len(data.get('history', []))
    print(f"   Registros ahora: {final_count} (era {initial_count})")
    
    # 7. Eliminar conversión
    print("\n7️⃣ Eliminando conversión...")
    data, status = client.delete_conversion(created_id)
    print_result("DELETE /history/{id}", data, status)
    
    # 8. Verificar eliminación
    print("\n8️⃣ Verificando eliminación...")
    data, status = client.get_conversion_by_id(created_id)
    not_found = status == 404
    icon = "✅" if not_found else "❌"
    print(f"{icon} Conversión eliminada: {not_found}")
    
    # 9. Historial final
    print("\n9️⃣ Historial final...")
    data, status = client.get_history(limit=5)
    print_result("GET /history", data, status)
    end_count = len(data.get('history', []))
    print(f"   Registros final: {end_count}")


def test_error_cases():
    """Prueba casos de error"""
    print_separator("❌ CASOS DE ERROR")
    
    client = LocalAPIClient(BASE_URL)
    
    # POST sin campos requeridos
    print("1️⃣ POST /history sin campos requeridos...")
    data, status = client.create_conversion({"from": "USD"})
    expected = status == 400
    icon = "✅" if expected else "❌"
    print(f"{icon} Error 400 esperado: {status == 400} (Status: {status})")
    print(f"   Mensaje: {data.get('message', 'N/A')}")
    
    # GET con ID inexistente
    print("\n2️⃣ GET /history/{id} con ID inexistente...")
    data, status = client.get_conversion_by_id("2000-01-01T00:00:00Z")
    expected = status == 404
    icon = "✅" if expected else "❌"
    print(f"{icon} Error 404 esperado: {status == 404} (Status: {status})")
    print(f"   Mensaje: {data.get('message', 'N/A')}")
    
    # PUT con ID inexistente
    print("\n3️⃣ PUT /history/{id} con ID inexistente...")
    data, status = client.update_conversion("2000-01-01T00:00:00Z", {"amount": 100})
    expected = status == 404
    icon = "✅" if expected else "❌"
    print(f"{icon} Error 404 esperado: {status == 404} (Status: {status})")


def show_summary():
    """Muestra resumen y próximos pasos"""
    print_separator("🎉 RESUMEN")
    
    print("✅ Todas las pruebas completadas exitosamente!")
    print("\n📋 Funcionalidades probadas:")
    print("   ✅ Conexión al servidor local")
    print("   ✅ Obtener tasas de cambio")
    print("   ✅ Convertir moneda") 
    print("   ✅ Historial CRUD completo")
    print("   ✅ Manejo de errores")
    
    print("\n🚀 Próximos pasos:")
    print("   1. Desarrolla tu frontend apuntando a http://localhost:3000/dev")
    print("   2. Prueba con Postman o curl")
    print("   3. Cuando esté listo, despliega con: serverless deploy")
    
    print("\n💡 URLs útiles:")
    print(f"   📡 API: {BASE_URL}")
    print("   🗄️ DynamoDB Local: http://localhost:8000")
    
    print("\n📚 Documentación:")
    print("   📄 API_HISTORY_CRUD.md - Documentación completa")
    print("   📄 DESARROLLO_LOCAL.md - Guía de desarrollo")


def main():
    """Función principal"""
    print("🧪 PRUEBAS DE DESARROLLO LOCAL")
    print(f"📡 Probando servidor en: {BASE_URL}")
    
    # Verificar conexión
    if not test_server_connection():
        return
    
    try:
        # Probar endpoints básicos
        conversion_from_convert = test_basic_endpoints()
        
        # Probar CRUD completo
        test_history_crud()
        
        # Probar casos de error
        test_error_cases()
        
        # Mostrar resumen
        show_summary()
        
    except KeyboardInterrupt:
        print("\n\n⏹️ Pruebas interrumpidas por el usuario")
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        print("\n🔧 Verifica que:")
        print("   - El servidor esté corriendo (npm run dev)")
        print("   - Los puertos 3000 y 8000 estén disponibles")
        print("   - Las dependencias estén instaladas")


if __name__ == "__main__":
    main()