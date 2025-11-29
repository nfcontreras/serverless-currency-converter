# Ejemplos cURL para la API de Historial de Conversiones

# IMPORTANTE: Reemplaza {API_URL} con tu URL real de API Gateway después del despliegue
# Ejemplo: https://abc123xyz.execute-api.us-east-1.amazonaws.com/dev

# Variables de ejemplo
API_URL="https://abc123xyz.execute-api.us-east-1.amazonaws.com/dev"
CONVERSION_ID="2025-11-29T10:30:15.123Z"

# =============================================================================
# 1. OBTENER HISTORIAL DE CONVERSIONES (GET /history)
# =============================================================================

# Obtener todas las conversiones (límite por defecto: 20)
curl -X GET "${API_URL}/history" \
  -H "Accept: application/json"

# Obtener solo las últimas 5 conversiones
curl -X GET "${API_URL}/history?limit=5" \
  -H "Accept: application/json"

# =============================================================================
# 2. CREAR NUEVA CONVERSIÓN (POST /history)
# =============================================================================

# Crear conversión con todos los campos
curl -X POST "${API_URL}/history" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -d '{
    "from": "USD",
    "to": "EUR",
    "amount": 100,
    "result": 89.45,
    "rate": 0.8945,
    "last_updated": "2025-11-29T10:00:00Z"
  }'

# Crear conversión con campos mínimos requeridos
curl -X POST "${API_URL}/history" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -d '{
    "from": "GBP",
    "to": "USD",
    "amount": 50,
    "result": 62.85
  }'

# =============================================================================
# 3. OBTENER CONVERSIÓN POR ID (GET /history/{id})
# =============================================================================

# Obtener conversión específica por ID (timestamp)
curl -X GET "${API_URL}/history/${CONVERSION_ID}" \
  -H "Accept: application/json"

# Ejemplo con ID específico de los datos de prueba
curl -X GET "${API_URL}/history/2025-10-28T10:00:00Z" \
  -H "Accept: application/json"

# =============================================================================
# 4. ACTUALIZAR CONVERSIÓN (PUT /history/{id})
# =============================================================================

# Actualizar algunos campos de una conversión
curl -X PUT "${API_URL}/history/${CONVERSION_ID}" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -d '{
    "amount": 150,
    "result": 134.18
  }'

# Actualizar todos los campos
curl -X PUT "${API_URL}/history/${CONVERSION_ID}" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -d '{
    "from": "USD",
    "to": "GBP",
    "amount": 200,
    "result": 167.06,
    "rate": 0.8353
  }'

# =============================================================================
# 5. ELIMINAR CONVERSIÓN (DELETE /history/{id})
# =============================================================================

# Eliminar conversión por ID
curl -X DELETE "${API_URL}/history/${CONVERSION_ID}" \
  -H "Accept: application/json"

# Ejemplo con ID específico
curl -X DELETE "${API_URL}/history/2025-10-28T10:00:00Z" \
  -H "Accept: application/json"

# =============================================================================
# EJEMPLOS DE CASOS DE ERROR
# =============================================================================

# Error 400: POST sin body
curl -X POST "${API_URL}/history" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json"

# Error 400: POST con JSON inválido
curl -X POST "${API_URL}/history" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -d 'invalid json'

# Error 400: POST sin campos requeridos
curl -X POST "${API_URL}/history" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -d '{"from": "USD"}'

# Error 404: GET con ID inexistente
curl -X GET "${API_URL}/history/2000-01-01T00:00:00Z" \
  -H "Accept: application/json"

# Error 404: PUT con ID inexistente
curl -X PUT "${API_URL}/history/2000-01-01T00:00:00Z" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -d '{"amount": 100}'

# Error 404: DELETE con ID inexistente
curl -X DELETE "${API_URL}/history/2000-01-01T00:00:00Z" \
  -H "Accept: application/json"

# =============================================================================
# EJEMPLOS CON jq PARA FORMATEAR RESPUESTAS (si tienes jq instalado)
# =============================================================================

# Obtener historial con formato bonito
curl -s -X GET "${API_URL}/history?limit=3" \
  -H "Accept: application/json" | jq '.'

# Crear conversión y mostrar solo el ID generado
curl -s -X POST "${API_URL}/history" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -d '{
    "from": "EUR",
    "to": "USD",
    "amount": 100,
    "result": 111.75
  }' | jq -r '.data.timestamp'

# Obtener solo los IDs de todas las conversiones
curl -s -X GET "${API_URL}/history" \
  -H "Accept: application/json" | jq -r '.history[].id'

# =============================================================================
# SCRIPT COMPLETO DE PRUEBA
# =============================================================================

#!/bin/bash
# Guarda este script como test_crud.sh y ejecuta: bash test_crud.sh

API_URL="https://tu-api-url.amazonaws.com/dev"

echo "🚀 Probando CRUD de Historial de Conversiones"
echo "============================================="

echo ""
echo "1️⃣ Obteniendo historial inicial..."
curl -s -X GET "${API_URL}/history?limit=3" | jq '.success, .history | length'

echo ""
echo "2️⃣ Creando nueva conversión..."
RESPONSE=$(curl -s -X POST "${API_URL}/history" \
  -H "Content-Type: application/json" \
  -d '{
    "from": "USD",
    "to": "EUR",
    "amount": 100,
    "result": 89.45
  }')

echo $RESPONSE | jq '.success, .message'
NEW_ID=$(echo $RESPONSE | jq -r '.data.timestamp // empty')

if [ ! -z "$NEW_ID" ]; then
  echo ""
  echo "3️⃣ Obteniendo conversión creada (ID: $NEW_ID)..."
  curl -s -X GET "${API_URL}/history/${NEW_ID}" | jq '.success, .conversion'
  
  echo ""
  echo "4️⃣ Actualizando conversión..."
  curl -s -X PUT "${API_URL}/history/${NEW_ID}" \
    -H "Content-Type: application/json" \
    -d '{"amount": 150}' | jq '.success, .message'
  
  echo ""
  echo "5️⃣ Eliminando conversión..."
  curl -s -X DELETE "${API_URL}/history/${NEW_ID}" | jq '.success, .message'
fi

echo ""
echo "✅ Pruebas completadas!"