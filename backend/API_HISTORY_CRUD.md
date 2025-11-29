# API de Historial de Conversiones - CRUD Completo

Esta documentación describe los endpoints disponibles para el manejo completo del historial de conversiones de moneda, **incluyendo la integración completa con el frontend** que proporciona una interfaz visual para todas las operaciones CRUD.

## ✨ Integración Frontend

El frontend incluye **interfaz visual completa** para todas las operaciones:
- **📋 Listar**: Tabla con historial de conversiones
- **✏️ Editar**: Modal con formulario pre-poblado para modificar conversiones
- **🗑️ Eliminar**: Modal de confirmación con advertencias de seguridad
- **➕ Crear**: Se crea automáticamente al usar el conversor
- **🔍 Ver detalles**: Información completa de cada conversión

### Características de UX
- ✅ **Modales responsivos** con animaciones suaves
- ✅ **Validación en tiempo real** de formularios  
- ✅ **Confirmación de eliminación** con doble verificación
- ✅ **Auto-refresh** del historial después de cambios
- ✅ **Manejo completo de errores** con mensajes descriptivos
- ✅ **Íconos modernos** sin elementos visuales innecesarios

---

## Endpoints Disponibles

### 1. GET /history - Obtener Historial
Obtiene una lista de todas las conversiones realizadas.

**URL:** `GET /history`
**Query Parameters:**
- `limit` (opcional): Número máximo de registros a retornar (default: 20)

**Ejemplo de Request:**
```bash
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

**Frontend:** Se ejecuta automáticamente al cargar la página y al hacer clic en "Cargar historial".

---

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

**Frontend:** Se ejecuta automáticamente cuando se usa el conversor de divisas. No requiere acción manual del usuario.

---

### 3. GET /history/{id} - Obtener Conversión por ID
Obtiene una conversión específica por su ID (timestamp).

**URL:** `GET /history/{id}`
**Path Parameters:**
- `id`: Timestamp de la conversión (usado como ID único)

**Ejemplo de Request:**
```bash
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

**Frontend:** Usado internamente para operaciones de edición y validación.

---

### 4. ✏️ PUT /history/{id} - Actualizar Conversión
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

**Frontend:** 
- **Acción**: Hacer clic en el ícono ✏️ junto a cualquier conversión
- **Interfaz**: Modal con formulario pre-poblado con los datos actuales
- **Validación**: Todos los campos son validados en tiempo real
- **Campos**: Moneda origen/destino (dropdown), cantidad, resultado, tasa (opcional)
- **UX**: Botón "Guardando..." durante la operación, auto-refresh del historial

---

### 5. 🗑️ DELETE /history/{id} - Eliminar Conversión
Elimina una conversión del historial.

**URL:** `DELETE /history/{id}`
**Path Parameters:**
- `id`: Timestamp de la conversión a eliminar

**Ejemplo de Request:**
```bash
DELETE /history/2025-11-29T10:30:15.123Z
```

**Ejemplo de Response:**
```json
{
  "success": true,
  "message": "Conversion deleted successfully"
}
```

**Frontend:**
- **Acción**: Hacer clic en el ícono 🗑️ junto a cualquier conversión  
- **Interfaz**: Modal de confirmación con:
  - ⚠️ Ícono de advertencia
  - Mensaje: "¿Estás seguro de que deseas eliminar esta conversión del historial?"
  - Advertencia: **"Esta acción no se puede deshacer."**
  - Botones: "Cancelar" y "Eliminar"
- **UX**: Auto-refresh del historial después de eliminación exitosa
- **Seguridad**: Doble confirmación requerida

---

## Códigos de Error Comunes

### 400 - Bad Request
- Falta el body en requests POST/PUT
- JSON inválido en el body
- Faltan campos requeridos
- Tipos de datos inválidos

**Frontend:** Muestra mensaje de error descriptivo en la interfaz.

### 404 - Not Found
- ID de conversión no encontrado
- Conversión no existe

**Frontend:** Mensaje "Conversión no encontrada" con opción de recargar historial.

### 500 - Internal Server Error
- Error interno del servidor
- Problema con la base de datos

**Frontend:** Mensaje genérico "Error del servidor, intenta más tarde".

---

## Ejemplo de Uso Completo

### 1. Crear una conversión (Frontend + Backend)
**Frontend:** Usuario ingresa datos en el conversor y hace clic en "Convertir"
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

### 2. Obtener todas las conversiones (Frontend + Backend)
**Frontend:** Se carga automáticamente al abrir la página
```bash
curl https://api-url/history?limit=5
```

### 3. Obtener una conversión específica (Backend)
```bash
curl https://api-url/history/2025-11-29T10:30:15.123Z
```

### 4. ✏️ Actualizar una conversión (Frontend + Backend)
**Frontend:** Click en ✏️ → Modal de edición → Guardar
```bash
curl -X PUT https://api-url/history/2025-11-29T10:30:15.123Z \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 150,
    "result": 134.18
  }'
```

### 5. 🗑️ Eliminar una conversión (Frontend + Backend)
**Frontend:** Click en 🗑️ → Confirmar eliminación
```bash
curl -X DELETE https://api-url/history/2025-11-29T10:30:15.123Z
```

---

## Manejo de IDs y Encoding

### Formato de ID
Los IDs son timestamps en formato ISO 8601:
```
2025-11-29T10:30:15.123456+00:00
```

### URL Encoding
Para requests HTTP, los IDs deben ser encoded correctamente:
```
2025-11-29T10%3A30%3A15.123456%2B00%3A00
```

### Frontend Implementation
```javascript
// El frontend maneja el encoding automáticamente
const encodedId = encodeURIComponent(id);
await request(`/history/${encodedId}`, { method: 'DELETE' });
```

---

## Integración Frontend-Backend

### Flujo de Datos
```plaintext
1. Usuario interactúa con Frontend
2. Frontend valida datos localmente  
3. Frontend envía request HTTP al API
4. Backend procesa y responde
5. Frontend actualiza UI automáticamente
```

### Manejo de Estados
- **Loading**: Botones deshabilitados, texto "Cargando..."
- **Success**: Mensaje verde, auto-refresh
- **Error**: Mensaje rojo, opciones de retry

### Debug y Monitoring
El frontend incluye logs de debug en Console:
```javascript
console.log('Raw ID from entry:', id);
console.log('Encoded ID for URL:', encodeURIComponent(id));  
console.log('Final URL:', `${BASE_URL}/history/${encodeURIComponent(id)}`);
```

---

## Notas Importantes

1. **Persistencia:** Si DynamoDB no está disponible, las operaciones de lectura retornarán datos mock, pero las operaciones de escritura pueden fallar graciosamente.

2. **IDs:** Los IDs de las conversiones son sus timestamps en formato ISO 8601. Esto garantiza unicidad y orden cronológico.

3. **Validación:** Todos los endpoints validan los datos de entrada y retornan errores descriptivos.

4. **CORS:** Todos los endpoints tienen CORS habilitado para uso desde navegadores web.

5. **Integración:** El endpoint `/convert` automáticamente guarda las conversiones en el historial, por lo que no es necesario llamar manualmente a `POST /history` después de cada conversión.

6. **Frontend UX:** La interfaz proporciona una experiencia completa sin necesidad de herramientas externas para testing del CRUD.

7. **Encoding:** El frontend maneja automáticamente el encoding correcto de timestamps con caracteres especiales (`+`, `:`).

8. **Auto-sync:** Todas las operaciones frontend se sincronizan automáticamente con DynamoDB, garantizando consistencia de datos.