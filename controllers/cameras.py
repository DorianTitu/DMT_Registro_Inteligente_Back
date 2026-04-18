"""Endpoints para captura de imágenes de 4 cámaras DVR"""

import logging
import base64
from fastapi import APIRouter, HTTPException

from services.captura.peatonal_usuario import CamaraPeatonalUsuario
from services.captura.peatonal_cedula import CamaraPeatonalCedula
from services.captura.vehicular_usuario import CamaraVehicularUsuario
from services.captura.vehicular_cedula import CamaraVehicularCedula

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/camaras", tags=["Cámaras"])

servicio_peatonal_usuario = CamaraPeatonalUsuario()
servicio_peatonal_cedula = CamaraPeatonalCedula()
servicio_vehicular_usuario = CamaraVehicularUsuario()
servicio_vehicular_cedula = CamaraVehicularCedula()


@router.get("/peatonal-usuario/imagen")
async def obtener_imagen_peatonal_usuario():
    """Imagen de Usuario Peatonal (Canal 1) en Base64"""
    try:
        logger.info("Imagen: Cámara Peatonal Usuario")
        
        imagen_bytes = servicio_peatonal_usuario.obtener_imagen()
        
        if imagen_bytes is None:
            raise HTTPException(
                status_code=500,
                detail="Error al capturar imagen de Usuario Peatonal"
            )
        
        imagen_base64 = base64.b64encode(imagen_bytes).decode()
        
        return {
            "exito": True,
            "canal": "Peatonal Usuario",
            "tipo": "image/jpeg",
            "imagen_base64": imagen_base64
        }
        
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error en endpoint peatonal_usuario: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/peatonal-cedula/imagen")
async def obtener_imagen_peatonal_cedula(aplicar_crop: bool = True):
    """Obtiene imagen de Cédula Peatonal (Canal 3) en Base64"""
    try:
        logger.info(f"Imagen: Cámara Peatonal Cédula (crop={aplicar_crop})")
        
        imagen_bytes = servicio_peatonal_cedula.obtener_imagen(aplicar_crop=aplicar_crop)
        
        if imagen_bytes is None:
            raise HTTPException(
                status_code=500,
                detail="Error al capturar imagen de Cédula Peatonal"
            )
        
        imagen_base64 = base64.b64encode(imagen_bytes).decode()
        
        return {
            "exito": True,
            "canal": "Peatonal Cédula",
            "tipo": "image/jpeg",
            "aplicar_crop": aplicar_crop,
            "imagen_base64": imagen_base64
        }
        
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error en endpoint peatonal_cedula: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/vehicular-usuario/imagen")
async def obtener_imagen_vehicular_usuario():
    """Obtiene imagen de Vehículos de Usuario (Canal 2) en Base64"""
    try:
        logger.info("Imagen: Cámara Vehicular Usuario")
        
        imagen_bytes = servicio_vehicular_usuario.obtener_imagen()
        
        if imagen_bytes is None:
            raise HTTPException(
                status_code=500,
                detail="Error al capturar imagen de Vehículos de Usuario"
            )
        
        imagen_base64 = base64.b64encode(imagen_bytes).decode()
        
        return {
            "exito": True,
            "canal": "Vehicular Usuario",
            "tipo": "image/jpeg",
            "imagen_base64": imagen_base64
        }
        
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error en endpoint vehicular_usuario: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/vehicular-cedula/imagen")
async def obtener_imagen_vehicular_cedula(aplicar_crop: bool = True):
    """Obtiene imagen de Cédula Vehicular (Canal 4) en Base64"""
    try:
        logger.info(f"Imagen: Cámara Vehicular Cédula (crop={aplicar_crop})")
        
        imagen_bytes = servicio_vehicular_cedula.obtener_imagen(aplicar_crop=aplicar_crop)
        
        if imagen_bytes is None:
            raise HTTPException(
                status_code=500,
                detail="Error al capturar imagen de Cédula Vehicular"
            )
        
        imagen_base64 = base64.b64encode(imagen_bytes).decode()
        
        return {
            "exito": True,
            "canal": "Vehicular Cédula",
            "tipo": "image/jpeg",
            "aplicar_crop": aplicar_crop,
            "imagen_base64": imagen_base64
        }
        
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error en endpoint vehicular_cedula: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
