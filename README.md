# 💱 Serverless Currency Converter

Aplicación web basada en **arquitectura Serverless (FaaS)**, que permite:

- 🔁 Convertir divisas entre USD, EUR y COP
- 📊 Consultar tasas de cambio desde una API externa
- 📚 Obtener un historial de conversiones simulado

El proyecto usa **AWS Lambda**, **API Gateway** y **Serverless Framework**, con una SPA en HTML, CSS y JS.

---

## 🌐 Endpoints públicos

Desplegados en AWS:

| Función             | Método | Endpoint                                                                 |
|---------------------|--------|--------------------------------------------------------------------------|
| `convertCurrency`   | POST   | [https://k5uwumi7m2.execute-api.us-east-1.amazonaws.com/dev/convert](https://k5uwumi7m2.execute-api.us-east-1.amazonaws.com/dev/convert) |
| `getExchangeRates`  | GET    | [https://k5uwumi7m2.execute-api.us-east-1.amazonaws.com/dev/rates](https://k5uwumi7m2.execute-api.us-east-1.amazonaws.com/dev/rates)     |
| `getHistory`        | GET    | [https://k5uwumi7m2.execute-api.us-east-1.amazonaws.com/dev/history](https://k5uwumi7m2.execute-api.us-east-1.amazonaws.com/dev/history)   |

---

## 🧱 Arquitectura

```plaintext
[Frontend SPA] (HTML + JS)
        ↓
   API Gateway (AWS)
        ↓
+---------------------------+
|   Funciones Lambda (FaaS) |
|---------------------------|
| convertCurrency           | --> llama a ExchangeRate-API
| getExchangeRates          | --> retorna todas las tasas
| getHistory                | --> retorna historial simulado
+---------------------------+
        ↓
   Módulo compartido `shared/` para lógica común
```

## 📂 Estructura del proyecto
```plaintext
serverless-currency-converter/
├── backend/
│   ├── convert_currency/
│   │   ├── handler.py
│   │   ├── requirements.txt
│   ├── get_exchange_rates/
│   │   ├── handler.py
│   │   ├── requirements.txt
│   ├── get_history/
│   │   ├── handler.py
│   │   ├── requirements.txt
│   ├── shared/
│   │   ├── __init__.py
│   │   ├── exchange.py       
│   │   ├── storage.py          
│   │   ├── requirements.txt
│   └── serverless.yml
├── frontend/
│   ├── index.html
│   ├── script.js
│   └── style.css
├── README.md

```

## 🚀 Despliegue con Serverless Framework
### Requisitos:
+ Node.js + NPM
+ Python 3.11
+ AWS CLI (aws configure)
+ Serverless Framework (npm i -g serverless)

### Deploy:
```sh
cd backend
serverless deploy
```

## 📚 Funciones Lambda
convertCurrency (POST /convert)

Convierte una cantidad de una divisa a otra usando tasas reales.

Payload:
```json
{ "from": "USD", "to": "EUR", "amount": 100 }
```

Respuesta:
```json
{ "result": 93.1, "rate": 0.931 }
```

getExchangeRates (GET /rates)

Retorna todas las tasas de cambio desde una divisa base.

Respuesta parcial:
```json
{
  "base": "USD",
  "rates": {
    "EUR": 0.931,
    "COP": 3950.42,
    ...
  }
}
```

getHistory (GET /history)

Historial de conversiones simulado desde el módulo shared/storage.py.

Respuesta:
```json
{
  "success": true,
  "history": [
    {
      "from": "USD",
      "to": "EUR",
      "amount": 100,
      "result": 93.1,
      "timestamp": "2025-10-28T10:00:00Z"
    }
  ]
}
```