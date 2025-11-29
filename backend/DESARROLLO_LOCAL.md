# 🚀 Desarrollo Local - Currency Converter

Esta guía te ayuda a levantar el proyecto en local para desarrollo sin afectar nada en producción.

## 📋 Requisitos Previos

Antes de comenzar, asegúrate de tener instalado:

- **Python 3.12+** - [Descargar aquí](https://python.org/)
- **Node.js 18+** - [Descargar aquí](https://nodejs.org/)
- **npm** (viene con Node.js)

## 🛠️ Configuración Automática (Recomendado)

El método más fácil es usar el script de configuración automática:

```bash
python setup_local_dev.py
```

Este script:
- ✅ Verifica que tengas todos los requisitos
- ✅ Instala todas las dependencias Python y Node.js
- ✅ Configura DynamoDB local
- ✅ Crea scripts de desarrollo
- ✅ Configura variables de entorno

## 🚀 Iniciar Servidor Local

Después de la configuración automática, puedes iniciar el servidor de varias formas:

### Opción 1: Script de inicio (Windows)
```bash
start-dev.bat
```

### Opción 2: Script de inicio (Linux/Mac)
```bash
./start-dev.sh
```

### Opción 3: npm directamente
```bash
npm run dev
```

## 📍 Endpoints Disponibles

Una vez iniciado el servidor local, tendrás disponibles estos endpoints:

```
Base URL: http://localhost:3000/dev
```

### Conversión de Monedas
- `POST /dev/convert` - Convertir moneda

### Tasas de Cambio  
- `GET /dev/rates` - Obtener tasas de cambio

### Historial CRUD
- `GET /dev/history` - Obtener historial
- `POST /dev/history` - Crear conversión
- `GET /dev/history/{id}` - Obtener por ID
- `PUT /dev/history/{id}` - Actualizar conversión
- `DELETE /dev/history/{id}` - Eliminar conversión

## 🧪 Probar la API

### Opción 1: Cliente Python
```bash
python test_api_client_local.py
```

### Opción 2: cURL
```bash
# Obtener historial
curl http://localhost:3000/dev/history

# Crear conversión
curl -X POST http://localhost:3000/dev/history \
  -H "Content-Type: application/json" \
  -d '{"from":"USD","to":"EUR","amount":100,"result":89.45}'

# Convertir moneda
curl -X POST http://localhost:3000/dev/convert \
  -H "Content-Type: application/json" \
  -d '{"from":"USD","to":"EUR","amount":100}'
```

### Opción 3: Postman
Importa esta colección para probar todos los endpoints:

```json
{
  "info": {
    "name": "Currency Converter Local",
    "description": "API local para desarrollo"
  },
  "item": [
    {
      "name": "Get History",
      "request": {
        "method": "GET",
        "url": "http://localhost:3000/dev/history"
      }
    },
    {
      "name": "Convert Currency",
      "request": {
        "method": "POST", 
        "url": "http://localhost:3000/dev/convert",
        "header": [{"key": "Content-Type", "value": "application/json"}],
        "body": {
          "raw": "{\"from\":\"USD\",\"to\":\"EUR\",\"amount\":100}"
        }
      }
    }
  ]
}
```

## 🗄️ Base de Datos Local

El proyecto usa **DynamoDB Local** que corre en:
```
http://localhost:8000
```

### Datos de Prueba
Se incluyen datos de ejemplo automáticamente:
- 4 conversiones de prueba
- Diferentes pares de monedas (USD/EUR, EUR/COP, GBP/USD, USD/JPY)

### Administrar DynamoDB Local
```bash
# Ver tablas (requiere AWS CLI)
aws dynamodb list-tables --endpoint-url http://localhost:8000

# Ver datos de una tabla
aws dynamodb scan --table-name aws-currency-converter-history --endpoint-url http://localhost:8000
```

## 📁 Archivos Creados para Desarrollo

- `package.json` - Dependencias y scripts npm
- `.env` - Variables de entorno locales
- `start-dev.bat` - Script de inicio Windows
- `start-dev.sh` - Script de inicio Unix
- `test_api_client_local.py` - Cliente de pruebas local
- `seed-data/history.json` - Datos de prueba

## 🔧 Configuración Manual (Avanzado)

Si prefieres configurar manualmente:

### 1. Instalar dependencias Python
```bash
pip install -r requirements.txt
pip install boto3
```

### 2. Instalar dependencias Node.js
```bash
npm install -g serverless
npm install
```

### 3. Configurar variables de entorno
```bash
# Windows
set IS_OFFLINE=true
set DYNAMODB_ENDPOINT=http://localhost:8000

# Linux/Mac
export IS_OFFLINE=true
export DYNAMODB_ENDPOINT=http://localhost:8000
```

### 4. Iniciar servidor
```bash
serverless offline start --host 0.0.0.0 --port 3000
```

## 🐛 Troubleshooting

### Error: "Cannot find module 'serverless'"
```bash
npm install -g serverless
```

### Error: "DynamoDB local not accessible" 
- Verifica que el puerto 8000 esté libre
- Reinicia el servidor con `npm run dev`

### Error: Python modules not found
```bash
pip install -r requirements.txt
pip install boto3
```

### Puerto 3000 ocupado
Cambia el puerto en `package.json`:
```json
"dev": "serverless offline start --host 0.0.0.0 --port 3001"
```

## ✅ Ventajas del Desarrollo Local

- 🚀 **Rápido**: No hay deploy, cambios inmediatos
- 💰 **Gratis**: No consume recursos AWS
- 🔒 **Seguro**: No afecta producción  
- 🧪 **Completo**: DynamoDB local con datos de prueba
- 📊 **Debug**: Logs detallados en terminal
- 🔄 **Hot reload**: Cambios automáticos

## 🚀 Siguiente Paso: Deploy a AWS

Cuando estés listo para desplegar:

```bash
# Instalar y configurar AWS CLI si no lo tienes
aws configure

# Deploy a AWS
serverless deploy

# Ver endpoints desplegados
serverless info
```

---

¡Listo! Ahora puedes desarrollar localmente sin preocupaciones. 🎉