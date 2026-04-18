"""
API DVR Dahua 2.0 - Arquitectura de Servicios y Controladores
"""

from fastapi import FastAPI
from fastapi.responses import JSONResponse
import logging
from datetime import datetime

from controllers.cameras import router as cameras_router
from controllers.ocr import router as ocr_router

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="API DVR Dahua - Sistema de Cámaras",
    description="API para captura de imágenes de 4 cámaras DVR",
    version="2.0.0"
)

app.include_router(cameras_router)
app.include_router(ocr_router)



# ============================================
# ENDPOINTS RAÍZ
# ============================================

@app.get("/")
async def root():
    """
    Información general de la API
    """
    return {
        "nombre": "API DVR Dahua 2.0",
        "versión": "2.0.0",
        "descripción": "Sistema de cámaras con arquitectura de servicios",
        "estado": "Activo",
        "camaras": {
            "1": {
                "nombre": "Cámara Peatonal Usuario",
                "endpoint": "GET /camaras/peatonal-usuario/imagen",
                "descripcion": "Captura de foto de usuario peatonal",
                "recorte": False
            },
            "2": {
                "nombre": "Cámara Vehicular Usuario",
                "endpoint": "GET /camaras/vehicular-usuario/imagen",
                "descripcion": "Captura de vehículos de usuarios",
                "recorte": False
            },
            "3": {
                "nombre": "Cámara Peatonal Cédula",
                "endpoint": "GET /camaras/peatonal-cedula/imagen",
                "descripcion": "Captura de cédula de usuario peatonal",
                "recorte": True,
                "parametro": "aplicar_crop"
            },
            "4": {
                "nombre": "Cámara Vehicular Cédula",
                "endpoint": "GET /camaras/vehicular-cedula/imagen",
                "descripcion": "Captura de placa/documento de vehículos",
                "recorte": True,
                "parametro": "aplicar_crop"
            }
        },
        "documentacion": "/docs",
        "timestamp": datetime.now().isoformat()
    }


@app.get("/health")
async def health():
    """Health check"""
    return {"estado": "ok"}


@app.exception_handler(Exception)
async def exception_handler(request, exc):
    logger.error(f"Error: {str(exc)}")
    return JSONResponse(status_code=500, content={"detail": str(exc)})


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
