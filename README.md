# 💱 Serverless Currency Converter

Aplicación web basada en **arquitectura Serverless (FaaS)**, que permite:

- 🔄 Convertir divisas entre USD, EUR y COP
- 📊 Consultar tasas de cambio desde una API externa  
- 📚 Gestión completa del historial de conversiones (CRUD)
- ✏️ **NUEVO:** Editar conversiones existentes con interfaz modal
- 🗑️ **NUEVO:** Eliminar conversiones con confirmación visual
- 🎨 **NUEVO:** Interfaz moderna con íconos y animaciones

El proyecto usa **AWS Lambda**, **API Gateway**, **DynamoDB** y **Serverless Framework**, con una SPA en HTML, CSS y JS.

---

## 🌐 Endpoints públicos

Desplegados en AWS:

| Función             | Método | Endpoint                                                                 | Descripción                    |
|---------------------|--------|--------------------------------------------------------------------------|--------------------------------|
| `convertCurrency`   | POST   | [/convert](https://k5uwumi7m2.execute-api.us-east-1.amazonaws.com/dev/convert) | Convertir divisas |
| `getExchangeRates`  | GET    | [/rates](https://k5uwumi7m2.execute-api.us-east-1.amazonaws.com/dev/rates) | Obtener tasas de cambio |
| `getHistory`        | GET    | [/history](https://k5uwumi7m2.execute-api.us-east-1.amazonaws.com/dev/history) | **Listar** historial |
| `createHistory`     | POST   | [/history](https://k5uwumi7m2.execute-api.us-east-1.amazonaws.com/dev/history) | **Crear** nueva conversión |
| `getHistoryById`    | GET    | [/history/{id}](https://k5uwumi7m2.execute-api.us-east-1.amazonaws.com/dev/history/{id}) | **Obtener** conversión específica |
| `updateHistory`     | PUT    | [/history/{id}](https://k5uwumi7m2.execute-api.us-east-1.amazonaws.com/dev/history/{id}) | **✏️ Editar** conversión |
| `deleteHistory`     | DELETE | [/history/{id}](https://k5uwumi7m2.execute-api.us-east-1.amazonaws.com/dev/history/{id}) | **🗑️ Eliminar** conversión |

---

## 🧱 Arquitectura

```plaintext
[Frontend SPA] (HTML + JS + CSS)
        ↓
   API Gateway (AWS)
        ↓
+---------------------------+
|   Funciones Lambda (FaaS) |
|---------------------------|
| convertCurrency           | --> llama a ExchangeRate-API + guarda en DynamoDB
| getExchangeRates          | --> retorna todas las tasas
| getHistory (CRUD)         | --> DynamoDB operations (Create/Read/Update/Delete)
+---------------------------+
        ↓
   DynamoDB (Persistencia)
   + Módulo compartido `shared/` para lógica común
```

## ✨ Nuevas Funcionalidades Frontend

### 🎯 Gestión Visual del Historial
- **Íconos modernos**: ✏️ para editar, 🗑️ para eliminar
- **Modales elegantes**: Confirmación y edición con animaciones
- **Validación en tiempo real**: Formularios con validación completa
- **Feedback visual**: Estados de carga y mensajes de éxito/error

### 🛡️ Experiencia de Usuario
- **Confirmación de eliminación**: Modal personalizado con advertencias
- **Edición in-situ**: Formulario pre-poblado con datos actuales
- **Manejo de errores**: Gestión completa de códigos HTTP (400, 404, 500)
- **Responsive design**: Funciona en desktop y móvil

### 🔧 Integración API
- **Encoding correcto**: Manejo apropiado de timestamps con caracteres especiales
- **Persistencia**: Todas las operaciones se sincronizan con DynamoDB
- **Auto-refresh**: El historial se actualiza automáticamente después de cambios

---

## 📂 Estructura del proyecto
```plaintext
serverless-currency-converter/
├── backend/
│   ├── convert_currency/
│   │   ├── handler.py
│   │   └── requirements.txt
│   ├── get_exchange_rates/
│   │   ├── handler.py
│   │   └── requirements.txt
│   ├── get_history/                    # ← CRUD completo
│   │   ├── handler.py                  # ← GET, POST, PUT, DELETE
│   │   └── requirements.txt
│   ├── shared/
│   │   ├── __init__.py
│   │   ├── exchange.py
│   │   ├── storage.py                  # ← DynamoDB operations
│   │   └── requirements.txt
│   ├── serverless.yml                  # ← Configuración AWS
│   ├── API_HISTORY_CRUD.md            # ← Documentación API completa
│   ├── curl_examples.sh               # ← Ejemplos de testing
│   └── test_history_crud.py           # ← Tests automatizados
├── frontend/                           # ← ✨ MEJORADO
│   ├── index.html                      # ← UI actualizada
│   ├── script.js                       # ← Funcionalidades CRUD
│   └── style.css                       # ← Estilos modernos con modales
└── README.md                           # ← Esta documentación
```

## 🚀 Despliegue con Serverless Framework

### Requisitos:
- Node.js + NPM
- Python 3.11
- AWS CLI (`aws configure`)
- Serverless Framework (`npm i -g serverless`)

### Deploy:
```bash
cd backend
serverless deploy
```

### Frontend:
El frontend es una SPA estática que se puede servir desde cualquier hosting. Configurar `data-api-base` en `index.html` con la URL de tu API Gateway.

---

## 📚 Funciones Lambda

### convertCurrency (POST /convert)
Convierte una cantidad de una divisa a otra usando tasas reales **y guarda automáticamente en el historial**.

**Payload:**
```json
{ "from": "USD", "to": "EUR", "amount": 100 }
```

**Respuesta:**
```json
{
  "success": true,
  "from": "USD",
  "to": "EUR", 
  "amount": 100,
  "result": 93.1,
  "rate": 0.931,
  "timestamp": "2025-11-29T10:30:15.123Z",
  "last_updated": "2025-11-29T10:00:00Z"
}
```

### getExchangeRates (GET /rates)
Retorna todas las tasas de cambio desde una divisa base.

**Query Parameters:**
- `base` (opcional): Divisa base (default: USD)

**Respuesta:**
```json
{
  "success": true,
  "base": "USD",
  "rates": {
    "EUR": 0.931,
    "COP": 3950.42
  },
  "last_updated": "2025-11-29T10:00:00Z",
  "next_update": "2025-11-29T11:00:00Z"
}
```

### ✨ Historia CRUD (GET/POST/PUT/DELETE /history)

#### 📋 GET /history - Listar conversiones
```bash
curl "https://api-url/history?limit=10"
```

#### ➕ POST /history - Crear conversión
```bash
curl -X POST https://api-url/history \
  -H "Content-Type: application/json" \
  -d '{"from": "USD", "to": "EUR", "amount": 100, "result": 93.1}'
```

#### ✏️ PUT /history/{id} - Editar conversión
```bash
curl -X PUT "https://api-url/history/2025-11-29T10:30:15.123Z" \
  -H "Content-Type: application/json" \
  -d '{"amount": 150, "result": 139.65}'
```

#### 🗑️ DELETE /history/{id} - Eliminar conversión  
```bash
curl -X DELETE "https://api-url/history/2025-11-29T10:30:15.123Z"
```

**Ver documentación completa en:** [`backend/API_HISTORY_CRUD.md`](backend/API_HISTORY_CRUD.md)

---

## 🧪 Testing

### Backend Tests
```bash
cd backend
python test_history_crud.py          # Tests unitarios
python test_api_client.py            # Tests de integración
python test_api_client_local.py      # Tests locales
```

### Frontend Testing
1. Abrir `frontend/index.html` en navegador
2. Abrir DevTools (F12) → Console para logs de debug
3. Probar conversiones, edición y eliminación

### Ejemplos cURL
```bash
cd backend
chmod +x curl_examples.sh
./curl_examples.sh
```

---

## 🔧 Configuración

### Variables de Entorno (Backend)
- `EXCHANGE_API_KEY`: API key para ExchangeRate-API (opcional)
- `DYNAMODB_TABLE`: Nombre de tabla DynamoDB (default: `currency-conversions`)

### Configuración Frontend
Editar `data-api-base` en `frontend/index.html`:
```html
<body data-api-base="https://tu-api-gateway-url/dev">
```

---

## 📖 Documentación Adicional

- [`API_HISTORY_CRUD.md`](backend/API_HISTORY_CRUD.md) - Documentación completa del API
- [`DESARROLLO_LOCAL.md`](backend/DESARROLLO_LOCAL.md) - Setup para desarrollo local
- [`curl_examples.sh`](backend/curl_examples.sh) - Ejemplos de testing con curl

---

## 🎯 Características Destacadas

- ✅ **Arquitectura Serverless completa**
- ✅ **CRUD completo del historial**  
- ✅ **Persistencia en DynamoDB**
- ✅ **Frontend moderno con UX optimizada**
- ✅ **Validación y manejo de errores robusto**
- ✅ **Tests automatizados**
- ✅ **Documentación completa**
- ✅ **Responsive design**
- ✅ **Integración API externa (ExchangeRate-API)**