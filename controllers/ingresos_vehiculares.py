"""
Controlador de Ingresos Vehiculares - Endpoints CREATE, READ, UPDATE
Estructuralmente idéntico a peatonales pero con 3 imágenes: usuario, cedula, placa
"""

import logging
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional

from services.ingresos_vehiculares.gestor_ingresos import GestorIngresosVehiculares

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ingresos-vehicular", tags=["Ingresos Vehiculares"])
gestor = GestorIngresosVehiculares()


# ============================================
# MODELOS PYDANTIC
# ============================================

class CrearIngresoVehicularRequest(BaseModel):
    """Modelo para crear un nuevo ingreso vehicular"""
    numero_cedula: str = Field(..., description="10 dígitos de cédula")
    nombres: str = Field(..., description="Nombres completos")
    apellidos: str = Field(..., description="Apellidos")
    placa: str = Field(..., description="Placa del vehículo")
    hora_entrada: str = Field(..., description="Hora de entrada HH:MM:SS")
    departamento: str = Field(..., description="Departamento/área de destino")
    motivo: str = Field(..., description="Motivo del ingreso")
    imagen_usuario_base64: str = Field(..., description="Imagen del usuario en Base64")
    imagen_cedula_base64: str = Field(..., description="Imagen de la cédula en Base64")
    imagen_placa_base64: str = Field(..., description="Imagen de la placa en Base64")


class ActualizarIngresoVehicularRequest(BaseModel):
    """Modelo para actualizar un ingreso vehicular"""
    numero_cedula: Optional[str] = Field(None, description="10 dígitos de cédula")
    nombres: Optional[str] = Field(None, description="Nombres completos")
    apellidos: Optional[str] = Field(None, description="Apellidos")
    placa: Optional[str] = Field(None, description="Placa del vehículo")
    departamento: Optional[str] = Field(None, description="Departamento/área")
    motivo: Optional[str] = Field(None, description="Motivo del ingreso")


# ============================================
# ENDPOINTS
# ============================================

@router.post("/create")
async def crear_ingreso_vehicular(datos: CrearIngresoVehicularRequest):
    """
    Crea un nuevo registro de ingreso vehicular
    
    - Genera ticket automático: TICKET-[MES]-[DÍA]-[NÚMERO]
    - Guarda 3 imágenes (usuario.jpeg, cedula.jpeg, placa.jpeg)
    - Crea carpeta del día si no existe
    - Actualiza Excel mensual con placa
    
    Retorna: ticket generado y fecha de registro
    """
    try:
        logger.info(f"Creando ingreso vehicular para cédula: {datos.numero_cedula}, placa: {datos.placa}")

        resultado = gestor.crear_ingreso(
            numero_cedula=datos.numero_cedula,
            nombres=datos.nombres,
            apellidos=datos.apellidos,
            placa=datos.placa,
            hora_entrada=datos.hora_entrada,
            departamento=datos.departamento,
            motivo=datos.motivo,
            imagen_usuario_base64=datos.imagen_usuario_base64,
            imagen_cedula_base64=datos.imagen_cedula_base64,
            imagen_placa_base64=datos.imagen_placa_base64,
        )

        if "error" in resultado:
            raise HTTPException(status_code=400, detail=resultado["error"])

        return {
            "exito": True,
            "mensaje": "Ingreso vehicular registrado exitosamente",
            "ticket": resultado["ticket"],
            "fecha_registro": resultado["fecha_registro"],
            "hora_entrada": resultado["hora_entrada"],
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error en crear_ingreso_vehicular: {e}")
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")


@router.get("/{ticket}")
async def leer_ingreso_vehicular(ticket: str):
    """
    Lee un registro de ingreso vehicular por ticket
    
    Retorna:
    - Todos los datos del registro
    - TICKET, NOMBRE, APELLIDO, CÉDULA, PLACA, DEPARTAMENTO, MOTIVO
    - INGRESO, SALIDA/ESTADO, FECHA_REGISTRO
    - 3 Imágenes en Base64 (usuario.jpeg, cedula.jpeg, placa.jpeg)
    """
    try:
        logger.info(f"Leyendo ingreso vehicular con ticket: {ticket}")

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
        logger.error(f"Error en leer_ingreso_vehicular: {e}")
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")


@router.put("/{ticket}")
async def actualizar_ingreso_vehicular(ticket: str, datos: ActualizarIngresoVehicularRequest):
    """
    Actualiza un registro de ingreso vehicular
    
    Campos editables:
    - numero_cedula
    - nombres
    - apellidos
    - placa
    - departamento
    - motivo
    
    Campos NO editables (inmutables):
    - TICKET
    - FECHA_REGISTRO (fecha de creación)
    
    Las imágenes NO se pueden editar
    """
    try:
        logger.info(f"Actualizando ingreso vehicular con ticket: {ticket}")

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
        logger.error(f"Error en actualizar_ingreso_vehicular: {e}")
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")


@router.get("/listar/dia")
async def listar_ingresos_vehiculares_por_dia(fecha: str):
    """
    Lista todos los tickets vehiculares de un día específico
    
    Parámetro query:
    - fecha: DD/MM/YYYY o YYYY-MM-DD
    
    Retorna:
    - Lista de todos los registros del día (SIN imágenes Base64)
    - Incluye: ticket, cédula, nombres, apellidos, placa, departamento, motivo, horas
    - Total de registros del día
    
    Ejemplos:
    - GET /ingresos-vehicular/listar/dia?fecha=19/04/2026
    - GET /ingresos-vehicular/listar/dia?fecha=2026-04-19
    """
    try:
        logger.info(f"Listando ingresos vehiculares para fecha: {fecha}")

        resultado = gestor.listar_ingresos_por_dia(fecha)

        if "error" in resultado:
            raise HTTPException(status_code=400, detail=resultado["error"])

        return {
            "exito": True,
            "fecha": resultado["fecha"],
            "cantidad_tickets": resultado["cantidad_tickets"],
            "tickets": resultado["tickets"],
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error en listar_ingresos_vehiculares_por_dia: {e}")
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")
