# API de Historial de Conversiones - CRUD Completo

Esta documentación describe los endpoints disponibles para el manejo completo del historial de conversiones de moneda.

## Endpoints Disponibles

### 1. GET /history - Obtener Historial
Obtiene una lista de todas las conversiones realizadas.

**URL:** `GET /history`
**Query Parameters:**
- `limit` (opcional): Número máximo de registros a retornar (default: 20)

**Ejemplo de Request:**
```
GET /history?limit=10
```

**Ejemplo de Response:**
```json
{
  "success": true,
  "history": [
    {
      "id": "2025-11-29T10:30:15.123Z",
      "from": "USD",
      "to": "EUR",
      "amount": 100,
      "result": 89.45,
      "rate": 0.8945,
      "timestamp": "2025-11-29T10:30:15.123Z",
      "last_updated": "2025-11-29T10:00:00Z"
    }
  ],
  "source": "dynamodb"
}
```

### 2. POST /history - Crear Nueva Conversión
Crea una nueva entrada en el historial de conversiones.

**URL:** `POST /history`
**Content-Type:** `application/json`

**Body Required:**
```json
{
  "from": "USD",
  "to": "EUR",
  "amount": 100,
  "result": 89.45,
  "rate": 0.8945,
  "last_updated": "2025-11-29T10:00:00Z"
}
```

**Campos requeridos:**
- `from`: Moneda de origen (string)
- `to`: Moneda de destino (string)
- `amount`: Cantidad a convertir (number)
- `result`: Resultado de la conversión (number)

**Campos opcionales:**
- `rate`: Tipo de cambio utilizado (number)
- `last_updated`: Timestamp de última actualización de tasas (string)
- `timestamp`: Timestamp de la conversión (se genera automáticamente si no se proporciona)

**Ejemplo de Response:**
```json
{
  "success": true,
  "message": "Conversion record created successfully",
  "data": {
    "from": "USD",
    "to": "EUR",
    "amount": 100,
    "result": 89.45,
    "rate": 0.8945,
    "timestamp": "2025-11-29T10:30:15.123Z",
    "last_updated": "2025-11-29T10:00:00Z"
  }
}
```

### 3. GET /history/{id} - Obtener Conversión por ID
Obtiene una conversión específica por su ID (timestamp).

**URL:** `GET /history/{id}`
**Path Parameters:**
- `id`: Timestamp de la conversión (usado como ID único)

**Ejemplo de Request:**
```
GET /history/2025-11-29T10:30:15.123Z
```

**Ejemplo de Response:**
```json
{
  "success": true,
  "conversion": {
    "id": "2025-11-29T10:30:15.123Z",
    "from": "USD",
    "to": "EUR",
    "amount": 100,
    "result": 89.45,
    "rate": 0.8945,
    "timestamp": "2025-11-29T10:30:15.123Z",
    "last_updated": "2025-11-29T10:00:00Z"
  },
  "source": "dynamodb"
}
```

### 4. PUT /history/{id} - Actualizar Conversión
Actualiza una conversión existente.

**URL:** `PUT /history/{id}`
**Content-Type:** `application/json`
**Path Parameters:**
- `id`: Timestamp de la conversión a actualizar

**Body (todos los campos son opcionales):**
```json
{
  "from": "USD",
  "to": "GBP",
  "amount": 150,
  "result": 125.30,
  "rate": 0.8353
}
```

**Campos actualizables:**
- `from`: Moneda de origen
- `to`: Moneda de destino
- `amount`: Cantidad
- `result`: Resultado
- `rate`: Tipo de cambio

**Nota:** El campo `last_updated` se actualiza automáticamente.

**Ejemplo de Response:**
```json
{
  "success": true,
  "message": "Conversion updated successfully",
  "conversion": {
    "id": "2025-11-29T10:30:15.123Z",
    "from": "USD",
    "to": "GBP",
    "amount": 150,
    "result": 125.30,
    "rate": 0.8353,
    "timestamp": "2025-11-29T10:30:15.123Z",
    "last_updated": "2025-11-29T11:00:00.000Z"
  }
}
```

### 5. DELETE /history/{id} - Eliminar Conversión
Elimina una conversión del historial.

**URL:** `DELETE /history/{id}`
**Path Parameters:**
- `id`: Timestamp de la conversión a eliminar

**Ejemplo de Request:**
```
DELETE /history/2025-11-29T10:30:15.123Z
```

**Ejemplo de Response:**
```json
{
  "success": true,
  "message": "Conversion deleted successfully"
}
```

## Códigos de Error Comunes

### 400 - Bad Request
- Falta el body en requests POST/PUT
- JSON inválido en el body
- Faltan campos requeridos
- Tipos de datos inválidos

### 404 - Not Found
- ID de conversión no encontrado
- Conversión no existe

### 500 - Internal Server Error
- Error interno del servidor
- Problema con la base de datos

## Ejemplo de Uso Completo

### 1. Crear una conversión
```bash
curl -X POST https://api-url/history \
  -H "Content-Type: application/json" \
  -d '{
    "from": "USD",
    "to": "EUR", 
    "amount": 100,
    "result": 89.45,
    "rate": 0.8945
  }'
```

### 2. Obtener todas las conversiones
```bash
curl https://api-url/history?limit=5
```

### 3. Obtener una conversión específica
```bash
curl https://api-url/history/2025-11-29T10:30:15.123Z
```

### 4. Actualizar una conversión
```bash
curl -X PUT https://api-url/history/2025-11-29T10:30:15.123Z \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 150,
    "result": 134.18
  }'
```

### 5. Eliminar una conversión
```bash
curl -X DELETE https://api-url/history/2025-11-29T10:30:15.123Z
```

## Notas Importantes

1. **Persistencia:** Si DynamoDB no está disponible, las operaciones de lectura retornarán datos mock, pero las operaciones de escritura pueden fallar graciosamente.

2. **IDs:** Los IDs de las conversiones son sus timestamps en formato ISO 8601. Esto garantiza unicidad y orden cronológico.

3. **Validación:** Todos los endpoints validan los datos de entrada y retornan errores descriptivos.

4. **CORS:** Todos los endpoints tienen CORS habilitado para uso desde navegadores web.

5. **Integración:** El endpoint `/convert` automáticamente guarda las conversiones en el historial, por lo que no es necesario llamar manualmente a `POST /history` después de cada conversión.