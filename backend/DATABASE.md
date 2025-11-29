# Base de Datos - DynamoDB Schema y Configuración

Esta documentación describe la estructura completa de la base de datos DynamoDB para el sistema de gestión del historial de conversiones.

## 🏗️ Arquitectura de Base de Datos

### Proveedor: **Amazon DynamoDB**
- **Tipo**: NoSQL Document Database
- **Modelo de facturación**: Pay-per-request (On-demand)
- **Región**: us-east-1
- **Nombre de tabla**: `aws-currency-converter-history`

### Ventajas de DynamoDB para este proyecto:
- ✅ **Serverless nativo** - perfecta integración con Lambda
- ✅ **Escalabilidad automática** - maneja carga variable sin configuración
- ✅ **Pay-per-use** - costo solo por uso real
- ✅ **Baja latencia** - respuestas sub-10ms consistentes
- ✅ **Alta disponibilidad** - 99.99% uptime SLA

---

## 🗃️ Estructura de Tabla

### Esquema de Claves
```yaml
Primary Key:
  Partition Key (HASH): pk (String)
  Sort Key (RANGE): sk (String)

Billing Mode: PAY_PER_REQUEST
```

### Patrón de Acceso
```plaintext
Partition Key: "conversion#history"  # Fijo para todas las conversiones
Sort Key: Timestamp (ISO 8601)       # Único por conversión, ordena cronológicamente
```

#### Ejemplo de clave:
```json
{
  "pk": "conversion#history",
  "sk": "2025-11-29T10:30:15.123456+00:00"
}
```

---

## 📋 Estructura de Item

### Schema Completo
```json
{
  "pk": "conversion#history",              // Partition Key (fijo)
  "sk": "2025-11-29T10:30:15.123456+00:00", // Sort Key (timestamp)
  "from": "USD",                           // Moneda origen
  "to": "EUR",                             // Moneda destino  
  "amount": 100.50,                        // Cantidad (Decimal)
  "result": 89.45,                         // Resultado (Decimal)
  "rate": 0.8945,                          // Tasa de cambio (Decimal, opcional)
  "last_updated": "2025-11-29T10:00:00Z"   // Última actualización tasas (String, opcional)
}
```

### Tipos de Datos DynamoDB
```yaml
pk: S           # String
sk: S           # String (timestamp ISO 8601)
from: S         # String (USD, EUR, COP, etc.)
to: S           # String (USD, EUR, COP, etc.)
amount: N       # Number (Decimal precision)
result: N       # Number (Decimal precision) 
rate: N         # Number (Decimal precision, opcional)
last_updated: S # String (timestamp ISO 8601, opcional)
```

---

## 🔧 Configuración Serverless (serverless.yml)

### Definición de Tabla
```yaml
resources:
  Resources:
    ConversionHistoryTable:
      Type: AWS::DynamoDB::Table
      Properties:
        TableName: aws-currency-converter-history
        AttributeDefinitions:
          - AttributeName: pk
            AttributeType: S
          - AttributeName: sk  
            AttributeType: S
        KeySchema:
          - AttributeName: pk
            KeyType: HASH
          - AttributeName: sk
            KeyType: RANGE
        BillingMode: PAY_PER_REQUEST
```

### Permisos IAM
```yaml
iam:
  role:
    statements:
      - Effect: Allow
        Action:
          - dynamodb:DescribeTable
          - dynamodb:PutItem      # Crear conversiones
          - dynamodb:Query        # Listar historial
          - dynamodb:GetItem      # Obtener conversión específica
          - dynamodb:UpdateItem   # ✏️ Editar conversiones
          - dynamodb:DeleteItem   # 🗑️ Eliminar conversiones
        Resource:
          - arn:aws:dynamodb:${self:provider.region}:*:table/aws-currency-converter-history
```

---

## 🌱 Datos de Prueba (Seed Data)

### Archivo: `backend/seed-data/history.json`
```json
[
  {
    "pk": "conversion#history",
    "sk": "2025-11-28T10:00:00Z",
    "from": "USD",
    "to": "EUR", 
    "amount": 100,
    "result": 89.45,
    "rate": 0.8945,
    "last_updated": "2025-11-28T09:00:00Z"
  },
  {
    "pk": "conversion#history",
    "sk": "2025-11-28T14:30:00Z",
    "from": "EUR",
    "to": "COP",
    "amount": 50,
    "result": 215000,
    "rate": 4300.00,
    "last_updated": "2025-11-28T14:00:00Z"
  },
  {
    "pk": "conversion#history", 
    "sk": "2025-11-28T16:15:00Z",
    "from": "GBP",
    "to": "USD",
    "amount": 75,
    "result": 94.88,
    "rate": 1.2651,
    "last_updated": "2025-11-28T16:00:00Z"
  },
  {
    "pk": "conversion#history",
    "sk": "2025-11-29T08:20:00Z", 
    "from": "USD",
    "to": "JPY",
    "amount": 200,
    "result": 29800,
    "rate": 149.00,
    "last_updated": "2025-11-29T08:00:00Z"
  }
]
```

### Configuración de Seed
```yaml
# En serverless.yml
custom:
  dynamodb:
    seed:
      domain:
        sources:
          - table: aws-currency-converter-history
            sources: [./seed-data/history.json]
```

---

## 🔄 Operaciones CRUD

### 1. 📋 **CREATE** (Crear conversión)
```python
def store_conversion_record(record: Dict[str, Any]) -> bool:
    item = {
        "pk": "conversion#history",
        "sk": timestamp,  # Auto-generado si no se proporciona
        "from": record.get("from"),
        "to": record.get("to"),
        "amount": _to_decimal(record.get("amount")),
        "result": _to_decimal(record.get("result")),
        "rate": _to_decimal(record.get("rate")),
        "last_updated": record.get("last_updated"),
    }
    table.put_item(Item=item)
```

### 2. 📖 **READ** (Obtener historial)
```python
def fetch_history(limit: int = 20) -> Tuple[List[Dict[str, Any]], bool]:
    response = table.query(
        KeyConditionExpression=Key("pk").eq("conversion#history"),
        ScanIndexForward=False,  # Orden descendente (más recientes primero)
        Limit=limit,
    )
```

### 3. 🔍 **READ BY ID** (Obtener conversión específica)
```python
def get_conversion_by_id(conversion_id: str) -> Tuple[Optional[Dict[str, Any]], bool]:
    response = table.get_item(
        Key={
            "pk": "conversion#history",
            "sk": conversion_id  # timestamp
        }
    )
```

### 4. ✏️ **UPDATE** (Editar conversión)
```python
def update_conversion_record(conversion_id: str, updates: Dict[str, Any]) -> bool:
    # Construye UpdateExpression dinámicamente
    update_expression = "SET " + ", ".join([f"{field} = :{field}" for field in updates])
    
    table.update_item(
        Key={"pk": "conversion#history", "sk": conversion_id},
        UpdateExpression=update_expression,
        ExpressionAttributeValues={f":{k}": v for k, v in updates.items()}
    )
```

### 5. 🗑️ **DELETE** (Eliminar conversión) 
```python
def delete_conversion_record(conversion_id: str) -> bool:
    table.delete_item(
        Key={
            "pk": "conversion#history",
            "sk": conversion_id
        }
    )
```

---

## 🏃‍♂️ Desarrollo Local

### DynamoDB Local
```yaml
# En serverless.yml
custom:
  dynamodb:
    stages:
      - dev
      - local
    start:
      port: 8000
      inMemory: true
      heapInitial: 200m
      heapMax: 1g
      migrate: true
      seed: true
```

### Configuración de Conexión Local
```python
# En storage.py
if os.environ.get('IS_OFFLINE') or os.environ.get('AWS_SAM_LOCAL'):
    resource = boto3.resource(
        "dynamodb",
        endpoint_url="http://localhost:8000",
        region_name="localhost",
        aws_access_key_id="fake",
        aws_secret_access_key="fake"
    )
```

### Comandos de Desarrollo
```bash
# Instalar DynamoDB local
npm install -g dynamodb-local

# Iniciar DynamoDB local
dynamodb-local

# Migrar tabla y seed data
serverless dynamodb migrate
```

---

## 📊 Manejo de Datos

### Conversión de Tipos
```python
def _to_decimal(value: Any) -> Optional[Decimal]:
    """DynamoDB maneja números como Decimal para precisión."""
    if value is None:
        return None
    return Decimal(str(value))

def _to_float(value: Any) -> Optional[float]:
    """Convierte Decimal a float para respuestas JSON."""
    if isinstance(value, Decimal):
        return float(value)
    return float(value)
```

### Timestamps
- **Formato**: ISO 8601 con timezone (`2025-11-29T10:30:15.123456+00:00`)
- **Uso**: Sort key para orden cronológico y ID único
- **Generación**: `datetime.now(timezone.utc).isoformat()`

### Precisión Numérica
- **DynamoDB**: Usa `Decimal` para evitar errores de floating point
- **Frontend**: Recibe `float` para compatibilidad JavaScript
- **Validación**: Campos numéricos requeridos: `amount`, `result`

---

## 🔍 Patrones de Query

### Query Principal (Obtener historial)
```sql
-- Equivalente SQL conceptual:
SELECT * FROM conversions 
WHERE pk = "conversion#history" 
ORDER BY sk DESC 
LIMIT 20;
```

```python
# DynamoDB Query
table.query(
    KeyConditionExpression=Key("pk").eq("conversion#history"),
    ScanIndexForward=False,  # Orden descendente
    Limit=limit
)
```

### Get Item (Obtener por ID)
```python
# DynamoDB GetItem
table.get_item(
    Key={
        "pk": "conversion#history", 
        "sk": "2025-11-29T10:30:15.123Z"
    }
)
```

---

## 🛡️ Consideraciones de Seguridad

### Validación de Entrada
- **Campos requeridos**: `from`, `to`, `amount`, `result`
- **Tipos válidos**: Strings para monedas, números para cantidades
- **Sanitización**: Conversión automática a Decimal

### Acceso
- **IAM roles**: Permisos mínimos necesarios por función
- **CORS**: Configurado para acceso desde frontend
- **Autenticación**: Actualmente pública (para demo)

### Backup y Recuperación
- **Point-in-time recovery**: Habilitado automáticamente en DynamoDB
- **Backup automático**: Configurar según necesidades de producción

---

## 📈 Optimización y Escalabilidad

### Capacidad
- **Pay-per-request**: Auto-scaling sin configuración
- **Throughput**: Hasta 40,000 read/write units por segundo
- **Latencia**: Sub-10ms consistente

### Indexación
- **Índices secundarios**: No requeridos para el patrón actual
- **Query efficiency**: Single-table design optimizado

### Caching
- **DynamoDB Accelerator (DAX)**: Para casos de alto read throughput
- **Application-level**: Caching en Lambda si es necesario

---

## 🔧 Troubleshooting

### Errores Comunes
```python
# Error de conexión
BotoCoreError: No credentials found

# Solución: Configurar AWS CLI
aws configure

# Error de tabla no encontrada
ClientError: Requested resource not found

# Solución: Desplegar recursos
serverless deploy
```

### Logs de Debug
```python
import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# En cada operación
logger.info(f"Executing query with pk={pk}, sk={sk}")
```

### Monitoreo
- **CloudWatch**: Métricas automáticas de DynamoDB
- **AWS X-Ray**: Tracing de requests
- **Application logs**: Logs estructurados en CloudWatch

---

## 🚀 Deploy y Configuración

### Despliegue Inicial
```bash
cd backend
serverless deploy
```

### Variables de Entorno
```yaml
# En serverless.yml
provider:
  environment:
    DYNAMODB_TABLE: aws-currency-converter-history
```

### Verificación
```bash
# Verificar tabla creada
aws dynamodb describe-table --table-name aws-currency-converter-history

# Verificar seed data
aws dynamodb scan --table-name aws-currency-converter-history
```

---

**¡Base de datos completamente configurada y optimizada para el CRUD frontend!** 🎯

### Integración con Frontend
- ✅ **IDs únicos**: Timestamps como sort keys
- ✅ **Operaciones CRUD**: Create, Read, Update, Delete
- ✅ **Encoding**: Manejo correcto de caracteres especiales
- ✅ **Validación**: Tipos de datos y campos requeridos
- ✅ **Performance**: Queries optimizadas para UI