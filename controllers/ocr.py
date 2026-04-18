import logging
import base64
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from services.ocr.cedula_nacional_nueva import CedulaNacionalNuevaOCR
from services.ocr.cedula_nacional_antigua import CedulaNacionalAntiguaOCR

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ocr", tags=["OCR"])

servicio_nueva = CedulaNacionalNuevaOCR()
servicio_antigua = CedulaNacionalAntiguaOCR()


# Modelos de entrada
class ImagenBase64(BaseModel):
    """Modelo para recibir imagen en Base64"""
    imagen_base64: str


@router.post("/cedula-nueva/numero")
async def procesar_cedula_nueva_numero(datos: ImagenBase64):
    """Procesa número de cédula - Cédula Nueva (recibe Base64, retorna solo 10 dígitos)"""
    try:
        logger.info("OCR: Cédula Nueva - Número")
        
        # Decodificar Base64 a bytes
        imagen_bytes = base64.b64decode(datos.imagen_base64)
        resultado = servicio_nueva.procesar_numero_cedula(imagen_bytes)
        
        if "error" in resultado:
            raise HTTPException(status_code=400, detail=resultado["error"])
        
        numero_parseado = resultado.get("numero_cedula_parseado", {})
        
        return {
            "tipo": "Cédula Nueva",
            "zona": "Número de Cédula",
            "numero_cedula": numero_parseado.get("numero", ""),
            "confianza": numero_parseado.get("confianza", 0)
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error OCR cédula nueva número: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/cedula-nueva/nombres-apellidos")
async def procesar_cedula_nueva_nombres_apellidos(datos: ImagenBase64):
    """Procesa nombres y apellidos - Cédula Nueva (recibe Base64, retorna solo apellidos y nombres)"""
    try:
        logger.info("OCR: Cédula Nueva - Nombres y Apellidos")
        
        # Decodificar Base64 a bytes
        imagen_bytes = base64.b64decode(datos.imagen_base64)
        resultado = servicio_nueva.procesar_nombres_apellidos(imagen_bytes)
        
        if "error" in resultado:
            raise HTTPException(status_code=400, detail=resultado["error"])
        
        parsed_data = resultado.get("nombres_apellidos_parseados", {})
        
        return {
            "tipo": "Cédula Nueva",
            "zona": "Nombres y Apellidos",
            "apellidos": parsed_data.get("apellidos", ""),
            "confianza_apellidos": parsed_data.get("confianza_apellidos", 0),
            "nombres": parsed_data.get("nombres", ""),
            "confianza_nombres": parsed_data.get("confianza_nombres", 0)
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error OCR cédula nueva nombres-apellidos: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/cedula-nueva/completa")
async def procesar_cedula_nueva_completa(datos: ImagenBase64):
    """Barrido COMPLETO de cédula nueva - extrae TODAS las zonas con OCR (recibe Base64)"""
    try:
        logger.info("OCR: Cédula Nueva - BARRIDO COMPLETO")
        
        # Decodificar Base64 a bytes
        imagen_bytes = base64.b64decode(datos.imagen_base64)
        resultado = servicio_nueva.procesar_cedula_completa(imagen_bytes)
        
        return resultado
    except Exception as e:
        logger.error(f"Error OCR cédula nueva completa: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/cedula-antigua/numero")
async def procesar_cedula_antigua_numero(datos: ImagenBase64):
    """Procesa número de cédula - Cédula Antigua (recibe Base64)"""
    try:
        logger.info("OCR: Cédula Antigua - Número")
        
        # Decodificar Base64 a bytes
        imagen_bytes = base64.b64decode(datos.imagen_base64)
        resultado = servicio_antigua.procesar_numero_cedula(imagen_bytes)
        
        if "error" in resultado:
            raise HTTPException(status_code=400, detail=resultado["error"])
        
        numero_parseado = resultado.get("numero_cedula_parseado", {})
        
        return {
            "tipo": "Cédula Antigua",
            "zona": "Número de Cédula",
            "numero_cedula": numero_parseado.get("numero", ""),
            "confianza": numero_parseado.get("confianza", 0)
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error OCR cédula antigua número: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/cedula-antigua/nombres-apellidos")
async def procesar_cedula_antigua_nombres_apellidos(datos: ImagenBase64):
    """Procesa nombres y apellidos - Cédula Antigua (recibe Base64)"""
    try:
        logger.info("OCR: Cédula Antigua - Nombres y Apellidos")
        
        # Decodificar Base64 a bytes
        imagen_bytes = base64.b64decode(datos.imagen_base64)
        resultado = servicio_antigua.procesar_nombres_apellidos(imagen_bytes)
        
        if "error" in resultado:
            raise HTTPException(status_code=400, detail=resultado["error"])
        
        parsed_data = resultado.get("nombres_apellidos_parseados", {})
        
        return {
            "tipo": "Cédula Antigua",
            "zona": "Nombres y Apellidos",
            "apellidos": parsed_data.get("apellidos", ""),
            "confianza_apellidos": parsed_data.get("confianza_apellidos", 0),
            "nombres": parsed_data.get("nombres", ""),
            "confianza_nombres": parsed_data.get("confianza_nombres", 0)
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error OCR cédula antigua nombres-apellidos: {e}")
        raise HTTPException(status_code=500, detail=str(e))
