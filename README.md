# Serverless Currency Converter

Aplicación serverless que expone tres funciones Lambda (conversión puntual, consulta de tasas y obtención de historial) y una interfaz web ligera para interactuar con ellas.

## Arquitectura

- **Backend (AWS Lambda + API Gateway + DynamoDB)**
  - `POST /convert` (`convert_currency/handler.convert_currency`)
    - Valida entrada, consulta tasas en `https://open.er-api.com/v6/latest/{base}` y calcula la conversión.
    - Intenta persistir el resultado en la tabla DynamoDB `aws-currency-converter-history`.
  - `GET /rates` (`get_exchange_rates/handler.get_exchange_rates`)
    - Devuelve el mapa de tasas para la moneda base solicitada y metadatos de la fuente.
  - `GET /history` (`get_history/handler.get_history`)
    - Lee el historial desde DynamoDB (ordenado por fecha desc). Si no hay datos o no hay permisos, responde con un historial de ejemplo.
  - `shared/exchange.py` encapsula la comunicación con el proveedor de tasas y normaliza errores.
  - `shared/storage.py` gestiona la integración opcional con DynamoDB sin requerir variables de entorno ni intervención manual.
- **Frontend (carpeta `frontend/`)**
  - `index.html` contiene la maquetación y define el atributo `data-api-base` con la URL del API Gateway.
  - `script.js` consume los tres endpoints, renderiza los resultados y señala si el historial proviene de DynamoDB o de los datos mock.
  - `style.css` brinda el estilo responsivo.

## Requisitos previos

- Node.js 18+ y npm (para Serverless Framework y servir el frontend).
- Python 3.12 y `pip` (las Lambdas usan `requests`).
- AWS CLI configurado con credenciales con permisos para Lambda, API Gateway y DynamoDB.
- Serverless Framework (`npm install -g serverless`).

## Despliegue del backend

```bash
cd backend
npm install       # si todavía no existen node_modules para serverless plugins
sls deploy
```

El manifiesto `serverless.yml` crea automáticamente la tabla DynamoDB `aws-currency-converter-history` en la región `us-east-1` y asigna a las Lambdas los permisos mínimos necesarios (`DescribeTable`, `PutItem`, `Query`).

### Pruebas locales

Ejecuta invocaciones locales con Serverless (requieren conexión a Internet para acceder al proveedor de tasas):

```bash
sls invoke local -f convertCurrency --data '{"body":"{\"from\":\"USD\",\"to\":\"EUR\",\"amount\":100}"}'
sls invoke local -f getExchangeRates --data '{"queryStringParameters":{"base":"USD"}}'
sls invoke local -f getHistory
```

Si no hay acceso a Internet, puedes emular la respuesta del proveedor usando `unittest.mock` (ver `shared/exchange.py` para el formato esperado de los datos).

## Frontend

1. Ajusta el atributo `data-api-base` en `frontend/index.html` si tu API Gateway tiene otra URL o stage.
2. Sirve la carpeta `frontend` con tu herramienta preferida, por ejemplo:

   ```bash
   cd frontend
   npx serve .
   ```

3. Abre el navegador en la URL indicada por el comando (por defecto `http://localhost:3000`).

El frontend carga automáticamente las tasas e historial al iniciar y permite realizar conversiones desde la tarjeta principal.

## Observaciones

- Si DynamoDB no está accesible (credenciales ausentes o permisos insuficientes), la aplicación continúa funcionando y `GET /history` regresará el historial de ejemplo indicando `source: "mock"`.
- Cambiar el proveedor de tasas sólo requiere actualizar las variables `EXCHANGE_API_BASE` y `EXCHANGE_API_TIMEOUT` en `serverless.yml`.
- Para entornos distintos de `us-east-1`, actualiza la región en `serverless.yml` y, si lo deseas, el nombre de la tabla en `shared/storage.py` y en la sección `resources`.
