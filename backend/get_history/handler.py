import json
import logging
from datetime import datetime, timezone

from shared.storage import (
    fetch_history, 
    store_conversion_record, 
    get_conversion_by_id,
    update_conversion_record,
    delete_conversion_record
)

HEADERS = {
    "Access-Control-Allow-Origin": "*",
    "Content-Type": "application/json",
}

FALLBACK_HISTORY = [
    {
        "id": "2025-10-28T10:00:00Z",
        "from": "USD",
        "to": "EUR",
        "amount": 100,
        "result": 89,
        "timestamp": "2025-10-28T10:00:00Z",
    },
    {
        "id": "2025-10-27T14:30:00Z",
        "from": "EUR",
        "to": "COP",
        "amount": 50,
        "result": 215000,
        "timestamp": "2025-10-27T14:30:00Z",
    },
]

logger = logging.getLogger(__name__)


def _success_response(body):
    return {
        "statusCode": 200,
        "headers": HEADERS,
        "body": json.dumps(body),
    }


def _error_response(status_code, message, error_detail=None):
    data = {"success": False, "message": message}
    if error_detail is not None:
        data["error"] = error_detail
    return {
        "statusCode": status_code,
        "headers": HEADERS,
        "body": json.dumps(data),
    }


def get_history(event, context):
    """GET /history - Obtiene el historial de conversiones"""
    try:
        # Obtener parámetros de query
        query_params = event.get("queryStringParameters") or {}
        limit = int(query_params.get("limit", 20))
        
        history, storage_active = fetch_history(limit)
        if not history:
            history = FALLBACK_HISTORY

        return _success_response({
            "success": True,
            "history": history,
            "source": "dynamodb" if storage_active else "mock",
        })

    except Exception as exc:
        logger.exception("Error al obtener el historial de conversiones")
        return _error_response(500, "Internal server error", str(exc))


def create_conversion(event, context):
    """POST /history - Crea una nueva entrada en el historial"""
    try:
        # Validar que hay un body
        if not event.get("body"):
            return _error_response(400, "Request body is required")

        body = json.loads(event["body"])
        
        # Validar campos requeridos
        required_fields = ["from", "to", "amount", "result"]
        missing_fields = [field for field in required_fields if not body.get(field)]
        
        if missing_fields:
            return _error_response(400, f"Missing required fields: {', '.join(missing_fields)}")

        # Crear timestamp si no se proporciona
        if not body.get("timestamp"):
            body["timestamp"] = datetime.now(timezone.utc).isoformat()

        # Guardar la conversión
        success = store_conversion_record(body)
        
        if success:
            return _success_response({
                "success": True,
                "message": "Conversion record created successfully",
                "data": body
            })
        else:
            # Si no se pudo guardar en DynamoDB, devolver la data pero indicar que no se persistió
            return _success_response({
                "success": True,
                "message": "Conversion record created (not persisted - storage unavailable)",
                "data": body,
                "warning": "Data was not saved to persistent storage"
            })

    except json.JSONDecodeError:
        return _error_response(400, "Invalid JSON in request body")
    except ValueError as e:
        return _error_response(400, f"Invalid data: {str(e)}")
    except Exception as exc:
        logger.exception("Error creating conversion record")
        return _error_response(500, "Internal server error", str(exc))


def get_conversion_by_id_handler(event, context):
    """GET /history/{id} - Obtiene una conversión específica"""
    try:
        # Obtener el ID del path
        path_params = event.get("pathParameters") or {}
        conversion_id = path_params.get("id")
        
        if not conversion_id:
            return _error_response(400, "Conversion ID is required")

        conversion, storage_active = get_conversion_by_id(conversion_id)
        
        if not storage_active:
            # Buscar en el fallback data
            fallback_conversion = next(
                (item for item in FALLBACK_HISTORY if item["id"] == conversion_id),
                None
            )
            if fallback_conversion:
                return _success_response({
                    "success": True,
                    "conversion": fallback_conversion,
                    "source": "mock"
                })
            else:
                return _error_response(404, "Conversion not found")

        if conversion is None:
            return _error_response(404, "Conversion not found")

        return _success_response({
            "success": True,
            "conversion": conversion,
            "source": "dynamodb"
        })

    except Exception as exc:
        logger.exception("Error getting conversion by ID")
        return _error_response(500, "Internal server error", str(exc))


def update_conversion(event, context):
    """PUT /history/{id} - Actualiza una conversión existente"""
    try:
        # Obtener el ID del path
        path_params = event.get("pathParameters") or {}
        conversion_id = path_params.get("id")
        
        if not conversion_id:
            return _error_response(400, "Conversion ID is required")

        # Validar que hay un body
        if not event.get("body"):
            return _error_response(400, "Request body is required")

        updates = json.loads(event["body"])
        
        # Agregar timestamp de última actualización
        updates["last_updated"] = datetime.now(timezone.utc).isoformat()

        # Intentar actualizar
        success = update_conversion_record(conversion_id, updates)
        
        if not success:
            return _error_response(404, "Conversion not found or could not be updated")

        # Obtener la conversión actualizada
        updated_conversion, _ = get_conversion_by_id(conversion_id)
        
        return _success_response({
            "success": True,
            "message": "Conversion updated successfully",
            "conversion": updated_conversion
        })

    except json.JSONDecodeError:
        return _error_response(400, "Invalid JSON in request body")
    except Exception as exc:
        logger.exception("Error updating conversion")
        return _error_response(500, "Internal server error", str(exc))


def delete_conversion(event, context):
    """DELETE /history/{id} - Elimina una conversión"""
    try:
        # Obtener el ID del path
        path_params = event.get("pathParameters") or {}
        conversion_id = path_params.get("id")
        
        if not conversion_id:
            return _error_response(400, "Conversion ID is required")

        # Intentar eliminar
        success = delete_conversion_record(conversion_id)
        
        if not success:
            return _error_response(404, "Conversion not found or could not be deleted")

        return _success_response({
            "success": True,
            "message": "Conversion deleted successfully"
        })

    except Exception as exc:
        logger.exception("Error deleting conversion")
        return _error_response(500, "Internal server error", str(exc))
