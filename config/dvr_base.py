"""
Configuración centralizada del DVR Dahua
Credenciales, IP y parámetros generales
"""

# ============================================
# CONFIGURACIÓN DVR
# ============================================

DVR_CONFIG = {
    "ip": "192.168.1.148",
    "usuario": "admin",
    "contraseña": "DMT_1990",
    "puerto_rtsp": 554,
    "protocolo": "RTSP"
}

# ============================================
# CONFIGURACIÓN DE CÁMARAS
# ============================================

CANALES = {
    1: {
        "nombre": "Cámara Peatonal Usuario",
        "id": "camara_peatonal_usuario",
        "canal": 1,
        "descripcion": "Captura de foto de usuario peatonal",
        "tipo": "Analógica"
    },
    2: {
        "nombre": "Cámara Vehicular Usuario",
        "id": "camara_vehicular_usuario",
        "canal": 2,
        "descripcion": "Captura de vehículos de usuarios",
        "tipo": "Analógica"
    },
    3: {
        "nombre": "Cámara Peatonal Cédula",
        "id": "camara_peatonal_cedula",
        "canal": 3,
        "descripcion": "Captura de cédula de usuario peatonal",
        "tipo": "IP",
        "funcionalidad": "Recorte cuadrado"
    },
    4: {
        "nombre": "Cámara Vehicular Cédula",
        "id": "camara_vehicular_cedula",
        "canal": 4,
        "descripcion": "Captura de placa/documento de vehículos",
        "tipo": "IP",
        "funcionalidad": "Recorte cuadrado"
    }
}

CROP_CONFIG = {
    3: {  # Canal Peatonal Cédula
        "vertices": {
            "top_left": (210, 110),
            "bottom_right": (1190, 1000)
        }
    },
    4: {  # Canal Vehicular Cédula
        "vertices": {
            "top_left": (145, 55),
            "bottom_right": (1090, 640)
        }
    }
}

def obtener_url_rtsp(canal: int) -> str:
    """
    Genera la URL RTSP para un canal específico
    
    Args:
        canal: Número de canal (1-4)
    
    Returns:
        URL RTSP completa
    """
    return (
        f"rtsp://{DVR_CONFIG['usuario']}:{DVR_CONFIG['contraseña']}"
        f"@{DVR_CONFIG['ip']}:{DVR_CONFIG['puerto_rtsp']}"
        f"/cam/realmonitor?channel={canal}&subtype=0"
    )

FFMPEG_CONFIG = {
    "rtsp_transport": "tcp",
    "timeout": 15,
    "vframes": 1,
    "quality": 4,  # -q:v 5 (1-31, menor es mejor)
    "format": "jpg"
}
