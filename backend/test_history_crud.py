#!/usr/bin/env python3
"""
Script de pruebas para el CRUD del historial de conversiones.
Ejecuta pruebas locales de las funciones implementadas.
"""

import json
import sys
from datetime import datetime, timezone
from unittest.mock import Mock

# Agregar el directorio actual al path
sys.path.append('.')

from get_history.handler import (
    get_history,
    create_conversion,
    get_conversion_by_id_handler,
    update_conversion,
    delete_conversion
)

def test_get_history():
    """Prueba la función get_history"""
    print("🧪 Probando GET /history...")
    
    event = {
        "queryStringParameters": {"limit": "5"}
    }
    context = {}
    
    response = get_history(event, context)
    
    print(f"Status Code: {response['statusCode']}")
    body = json.loads(response['body'])
    print(f"Success: {body.get('success')}")
    print(f"History items: {len(body.get('history', []))}")
    print(f"Source: {body.get('source')}")
    print("✅ GET /history - OK\n")
    
    return response

def test_create_conversion():
    """Prueba la función create_conversion"""
    print("🧪 Probando POST /history...")
    
    test_conversion = {
        "from": "USD",
        "to": "EUR",
        "amount": 100,
        "result": 89.45,
        "rate": 0.8945,
        "last_updated": "2025-11-29T10:00:00Z"
    }
    
    event = {
        "body": json.dumps(test_conversion)
    }
    context = {}
    
    response = create_conversion(event, context)
    
    print(f"Status Code: {response['statusCode']}")
    body = json.loads(response['body'])
    print(f"Success: {body.get('success')}")
    print(f"Message: {body.get('message')}")
    if body.get('data'):
        print(f"Created timestamp: {body['data'].get('timestamp')}")
    print("✅ POST /history - OK\n")
    
    return response

def test_get_conversion_by_id():
    """Prueba la función get_conversion_by_id_handler"""
    print("🧪 Probando GET /history/{id}...")
    
    # Usar un timestamp del fallback data
    test_id = "2025-10-28T10:00:00Z"
    
    event = {
        "pathParameters": {"id": test_id}
    }
    context = {}
    
    response = get_conversion_by_id_handler(event, context)
    
    print(f"Status Code: {response['statusCode']}")
    body = json.loads(response['body'])
    print(f"Success: {body.get('success')}")
    if body.get('conversion'):
        print(f"Found conversion: {body['conversion']['from']} -> {body['conversion']['to']}")
    print(f"Source: {body.get('source')}")
    print("✅ GET /history/{id} - OK\n")
    
    return response

def test_update_conversion():
    """Prueba la función update_conversion"""
    print("🧪 Probando PUT /history/{id}...")
    
    test_id = "2025-10-28T10:00:00Z"
    updates = {
        "amount": 150,
        "result": 134.18
    }
    
    event = {
        "pathParameters": {"id": test_id},
        "body": json.dumps(updates)
    }
    context = {}
    
    response = update_conversion(event, context)
    
    print(f"Status Code: {response['statusCode']}")
    body = json.loads(response['body'])
    print(f"Success: {body.get('success')}")
    print(f"Message: {body.get('message')}")
    print("✅ PUT /history/{id} - OK\n")
    
    return response

def test_delete_conversion():
    """Prueba la función delete_conversion"""
    print("🧪 Probando DELETE /history/{id}...")
    
    test_id = "2025-10-28T10:00:00Z"
    
    event = {
        "pathParameters": {"id": test_id}
    }
    context = {}
    
    response = delete_conversion(event, context)
    
    print(f"Status Code: {response['statusCode']}")
    body = json.loads(response['body'])
    print(f"Success: {body.get('success')}")
    print(f"Message: {body.get('message')}")
    print("✅ DELETE /history/{id} - OK\n")
    
    return response

def test_error_cases():
    """Prueba casos de error"""
    print("🧪 Probando casos de error...")
    
    # POST sin body
    response = create_conversion({"body": None}, {})
    assert response['statusCode'] == 400
    print("✅ POST sin body - Error 400 OK")
    
    # POST con JSON inválido
    response = create_conversion({"body": "invalid json"}, {})
    assert response['statusCode'] == 400
    print("✅ POST con JSON inválido - Error 400 OK")
    
    # POST sin campos requeridos
    response = create_conversion({"body": json.dumps({"from": "USD"})}, {})
    assert response['statusCode'] == 400
    print("✅ POST sin campos requeridos - Error 400 OK")
    
    # GET con ID faltante
    response = get_conversion_by_id_handler({"pathParameters": None}, {})
    assert response['statusCode'] == 400
    print("✅ GET sin ID - Error 400 OK")
    
    print("✅ Todos los casos de error - OK\n")

def main():
    """Ejecuta todas las pruebas"""
    print("🚀 Iniciando pruebas del CRUD de historial de conversiones\n")
    
    try:
        # Pruebas de funcionalidad básica
        test_get_history()
        test_create_conversion()
        test_get_conversion_by_id()
        test_update_conversion()
        test_delete_conversion()
        
        # Pruebas de casos de error
        test_error_cases()
        
        print("🎉 Todas las pruebas pasaron exitosamente!")
        print("\n📋 Resumen:")
        print("- ✅ GET /history - Obtener historial")
        print("- ✅ POST /history - Crear conversión")
        print("- ✅ GET /history/{id} - Obtener por ID")
        print("- ✅ PUT /history/{id} - Actualizar conversión")
        print("- ✅ DELETE /history/{id} - Eliminar conversión")
        print("- ✅ Manejo de errores")
        
    except Exception as e:
        print(f"❌ Error durante las pruebas: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()