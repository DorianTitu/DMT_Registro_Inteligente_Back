"""
Configuración de OCR para cédulas
Define zonas de recorte para número y nombres/apellidos
"""

# =============================================
# CÉDULA NUEVA - ZONAS DE RECORTE
# =============================================
CEDULA_NUEVA = {
    "zona_numero": (100, 1400, 1000, 1800),              # Inferior Izquierda: número de cédula
    "zona_nombres_apellidos": (800, 250, 1800, 900)   # Central-Superior: nombres y apellidos
}

# =============================================
# CÉDULA ANTIGUA - ZONAS DE RECORTE
# =============================================
CEDULA_ANTIGUA = {
    "zona_numero": (0, 2000, 0, 2000),              # Inferior Izquierda
    "zona_nombres_apellidos": (0, 2000, 0, 2000)   # Central-Superior
}

# =============================================
# PARÁMETROS DE PROCESAMIENTO (Optimizado para texto limpio)
# =============================================
OCR_CONFIG = {
    "upscale_factor": 3,                    # Amplificación 3x
    "clahe_clip_limit": 5.0,               # Contraste FUERTE para separa texto
    "clahe_tile_size": 4,                  # Tile pequeño para más detalle
    "morph_kernel_size": 2,                # Kernel pequeño
    "resultados_dir": "./ocr_resultados",  # Carpeta de guardado
    "auto_rotate": False                   # Desactivado
}
