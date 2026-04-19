"""
Controlador de Ingresos Peatonales - Endpoints CREATE, READ, UPDATE
"""

import logging
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional

from services.ingresos_peatonales.gestor_ingresos import GestorIngresosPeatonales

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ingresos-peatonal", tags=["Ingresos Peatonales"])
gestor = GestorIngresosPeatonales()


# ============================================
# MODELOS PYDANTIC
# ============================================

class CrearIngresoRequest(BaseModel):
    """Modelo para crear un nuevo ingreso peatonal"""
    numero_cedula: str = Field(..., description="10 dígitos de cédula")
    nombres: str = Field(..., description="Nombres completos")
    apellidos: str = Field(..., description="Apellidos")
    hora_entrada: str = Field(..., description="Hora de entrada HH:MM:SS")
    departamento: str = Field(..., description="Departamento/área de destino")
    motivo: str = Field(..., description="Motivo del ingreso")
    imagen_usuario_base64: str = Field(..., description="Imagen del usuario en Base64")
    imagen_cedula_base64: str = Field(..., description="Imagen de la cédula en Base64")


class ActualizarIngresoRequest(BaseModel):
    """Modelo para actualizar un ingreso peatonal"""
    numero_cedula: Optional[str] = Field(None, description="10 dígitos de cédula")
    nombres: Optional[str] = Field(None, description="Nombres completos")
    apellidos: Optional[str] = Field(None, description="Apellidos")
    departamento: Optional[str] = Field(None, description="Departamento/área")
    motivo: Optional[str] = Field(None, description="Motivo del ingreso")


# ============================================
# ENDPOINTS
# ============================================

@router.post("/create")
async def crear_ingreso_peatonal(datos: CrearIngresoRequest):
    """
    Crea un nuevo registro de ingreso peatonal
    
    - Genera ticket automático: TICKET-[MES]-[DÍA]-[NÚMERO]
    - Guarda imágenes (usuario.jpeg, cedula.jpeg)
    - Crea carpeta del día si no existe
    - Actualiza Excel mensual
    
    Retorna: ticket generado y fecha de registro
    """
    try:
        logger.info(f"Créando ingreso para cédula: {datos.numero_cedula}")

        resultado = gestor.crear_ingreso(
            numero_cedula=datos.numero_cedula,
            nombres=datos.nombres,
            apellidos=datos.apellidos,
            hora_entrada=datos.hora_entrada,
            departamento=datos.departamento,
            motivo=datos.motivo,
            imagen_usuario_base64=datos.imagen_usuario_base64,
            imagen_cedula_base64=datos.imagen_cedula_base64,
        )

        if "error" in resultado:
            raise HTTPException(status_code=400, detail=resultado["error"])

        return {
            "exito": True,
            "mensaje": "Ingreso peatonal registrado exitosamente",
            "ticket": resultado["ticket"],
            "fecha_registro": resultado["fecha_registro"],
            "hora_entrada": resultado["hora_entrada"],
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error en crear_ingreso_peatonal: {e}")
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")


@router.get("/{ticket}")
async def leer_ingreso_peatonal(ticket: str):
    """
    Lee un registro de ingreso peatonal por ticket
    
    Retorna:
    - Todos los datos del registro
    - TICKET, NOMBRE, APELLIDO, CÉDULA, DEPARTAMENTO, MOTIVO
    - INGRESO, SALIDA/ESTADO, FECHA_REGISTRO
    - Imágenes en Base64 (usuario.jpeg, cedula.jpeg)
    """
    try:
        logger.info(f"Leyendo ingreso con ticket: {ticket}")

        resultado = gestor.leer_ingreso(ticket)

        if "error" in resultado:
            raise HTTPException(status_code=404, detail=resultado["error"])

        return {
            "exito": True,
            "datos": resultado,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error en leer_ingreso_peatonal: {e}")
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")


@router.put("/{ticket}")
async def actualizar_ingreso_peatonal(ticket: str, datos: ActualizarIngresoRequest):
    """
    Actualiza un registro de ingreso peatonal
    
    Campos editables:
    - numero_cedula
    - nombres
    - apellidos
    - departamento
    - motivo
    
    Campos NO editables (inmutables):
    - TICKET
    - FECHA_REGISTRO (fecha de creación)
    
    Las imágenes NO se pueden editar
    """
    try:
        logger.info(f"Actualizando ingreso con ticket: {ticket}")

        # Convertir el modelo a diccionario, excluyendo campos None
        datos_dict = datos.dict(exclude_none=True)

        if not datos_dict:
            raise HTTPException(status_code=400, detail="No hay campos para actualizar")

        resultado = gestor.actualizar_ingreso(ticket, datos_dict)

        if "error" in resultado:
            raise HTTPException(status_code=404, detail=resultado["error"])

        return {
            "exito": True,
            "mensaje": resultado["mensaje"],
            "ticket": resultado["ticket"],
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error en actualizar_ingreso_peatonal: {e}")
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")
