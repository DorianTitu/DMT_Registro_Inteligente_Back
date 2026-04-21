"""
Configuración de OCR para cédulas
Define zonas de recorte para número y nombres/apellidos
Organizado por tipo_camara (peatonal/vehicular) y tipo de cédula (nueva/antigua)
"""

from pathlib import Path

# =============================================
# ZONAS DE RECORTE POR CÁMARA Y TIPO DE CÉDULA
# =============================================
OCR_ZONAS = {
    "peatonal": {
        "nueva": {
            "zona_numero": (100, 1400, 1100, 1800),              # Número de cédula
            "zona_nombres_apellidos": (1000, 250, 1850, 900)     # Nombres y apellidos
        },
        "antigua": {
            "zona_numero": (2000, 350, 3000, 800),               # Número de cédula
            "zona_nombres_apellidos": (1000, 400, 1850, 1000)    # Nombres y apellidos
        }
    },
    "vehicular": {
        "nueva": {
            # TODO: Ajustar estas zonas para cámara vehicular
            "zona_numero": (100, 1400, 1100, 1800),              # Número de cédula
            "zona_nombres_apellidos": (800, 250, 1800, 900)     # Nombres y apellidos
        },
        "antigua": {
            # TODO: Ajustar estas zonas para cámara vehicular
            "zona_numero": (1700, 350, 3000, 800),               # Número de cédula
            "zona_nombres_apellidos": (1000, 400, 1850, 1000)    # Nombres y apellidos
        }
    }
}

# =============================================
# PARÁMETROS DE PROCESAMIENTO (Optimizado para texto limpio)
# =============================================
OCR_CONFIG = {
    "upscale_factor": 3,                                         # Amplificación 3x
    "clahe_clip_limit": 5.0,                                    # Contraste FUERTE para separar texto
    "clahe_tile_size": 4,                                       # Tile pequeño para más detalle
    "morph_kernel_size": 2,                                     # Kernel pequeño
    "resultados_dir": str(Path(__file__).parent.parent / "ocr_resultados"),  # Carpeta de guardado (compatible Windows/Linux/Mac)
    "auto_rotate": False                                        # Desactivado
}
