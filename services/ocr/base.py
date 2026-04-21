import logging
from typing import Optional, Tuple, Dict, List
import cv2
import numpy as np
from PIL import Image
import io
import os
import json
from datetime import datetime
import easyocr

# Compatibilidad: Pillow 10.0.0+ removió Image.ANTIALIAS
# Agregar atributo si no existe para que EasyOCR y otras libs funcionen
if not hasattr(Image, 'ANTIALIAS'):
    Image.ANTIALIAS = Image.Resampling.LANCZOS

from config.ocr_cedula_config import OCR_CONFIG

logger = logging.getLogger(__name__)

# Inicializar reader de EasyOCR una sola vez
_reader = None

def get_ocr_reader():
    """Obtiene instancia de EasyOCR reader (lazy loading)"""
    global _reader
    if _reader is None:
        logger.info("Iniciando EasyOCR reader para español...")
        _reader = easyocr.Reader(['es'], gpu=False)
    return _reader


class BaseCedulaNacionalOCR:
    """Base para OCR de cédulas - VERSIÓN SIMPLIFICADA"""
    
    def __init__(self, tipo: str):
        self.tipo = tipo
        self.upscale = OCR_CONFIG["upscale_factor"]
        self.tratamientos_aplicados = []
    
    def _cargar_imagen(self, imagen_bytes: bytes) -> Optional[np.ndarray]:
        """Carga imagen desde bytes a OpenCV (BGR)"""
        try:
            img_pil = Image.open(io.BytesIO(imagen_bytes))
            img_cv = cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)
            logger.info(f"[{self.tipo}] Imagen cargada: {img_cv.shape}")
            self.tratamientos_aplicados.append(f"Cargada: {img_cv.shape}")
            return img_cv
        except Exception as e:
            logger.error(f"[{self.tipo}] Error cargar imagen: {e}")
            return None
    
    def _upscale(self, img: np.ndarray) -> np.ndarray:
        """Amplía imagen 3x para mejor OCR"""
        h, w = img.shape[:2]
        new_w, new_h = w * self.upscale, h * self.upscale
        img_upscaled = cv2.resize(img, (int(new_w), int(new_h)), interpolation=cv2.INTER_CUBIC)
        logger.info(f"[{self.tipo}] Upscale: {w}x{h} → {int(new_w)}x{int(new_h)}")
        self.tratamientos_aplicados.append(f"Upscale: {self.upscale}x")
        return img_upscaled
    
    def _crop_zona(self, img: np.ndarray, zona: Tuple[int, int, int, int]) -> np.ndarray:
        """Recorta zona especificada"""
        x1, y1, x2, y2 = zona
        img_cropped = img[y1:y2, x1:x2]
        logger.info(f"[{self.tipo}] Crop zona: ({x1},{y1}) → ({x2},{y2})")
        self.tratamientos_aplicados.append(f"Crop: ({x1},{y1},{x2},{y2})")
        return img_cropped
    
    def _threshold_suave(self, img: np.ndarray, valor: int = 10) -> np.ndarray:
        """Threshold suave - solo convierte a blanco y negro sin agresividad"""
        try:
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            _, binaria = cv2.threshold(gray, valor, 255, cv2.THRESH_BINARY)
            img_bin = cv2.cvtColor(binaria, cv2.COLOR_GRAY2BGR)
            logger.info(f"[{self.tipo}] Threshold suave: {valor}")
            self.tratamientos_aplicados.append(f"Threshold: {valor}")
            return img_bin
        except Exception as e:
            logger.warning(f"[{self.tipo}] Threshold falló: {e}")
            self.tratamientos_aplicados.append("Threshold: falló")
            return img
    
    def extraer_texto(self, img: np.ndarray) -> Dict:
        """Extrae texto de la imagen usando EasyOCR"""
        try:
            logger.info(f"[{self.tipo}] Iniciando extracción de texto con EasyOCR...")
            reader = get_ocr_reader()
            
            # Convertir a RGB si es BGR
            if len(img.shape) == 3 and img.shape[2] == 3:
                img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            else:
                img_rgb = img
            
            # Leer texto
            results = reader.readtext(img_rgb)
            
            # Extraer texto con confianza
            texto_bruto = []
            for detection in results:
                bbox, text, confidence = detection
                texto_bruto.append({
                    "texto": text,
                    "confianza": float(confidence),
                    "bbox": [[float(x), float(y)] for x, y in bbox]
                })
            
            # Reunir todo el texto
            texto_completo = " ".join([item["texto"] for item in texto_bruto])
            
            logger.info(f"[{self.tipo}] Texto extraído: {len(texto_bruto)} componentes encontrados")
            self.tratamientos_aplicados.append(f"OCR EasyOCR: {len(texto_bruto)} componentes")
            
            return {
                "exito": True,
                "texto_completo": texto_completo,
                "componentes": texto_bruto,
                "cantidad_componentes": len(texto_bruto)
            }
        except Exception as e:
            logger.error(f"[{self.tipo}] Error en OCR: {e}")
            return {
                "exito": False,
                "error": str(e),
                "texto_completo": "",
                "componentes": []
            }
    
    def procesar_zona_con_ocr(self, imagen_bytes: bytes, zona: Tuple[int, int, int, int]) -> Dict:
        """Procesa imagen Y extrae texto OCR"""
        self.tratamientos_aplicados = []
        
        img = self._cargar_imagen(imagen_bytes)
        if img is None:
            return {"error": "No se pudo cargar imagen"}
        
        img = self._upscale(img)
        img = self._crop_zona(img, zona)
        img = self._threshold_suave(img, valor=110)
        
        # Guardar imagen procesada en bytes
        buffer = io.BytesIO()
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        Image.fromarray(img_rgb).save(buffer, format='PNG')
        img_procesada = buffer.getvalue()
        
        # Extraer OCR
        ocr_result = self.extraer_texto(img)
        
        return {
            "exito": True,
            "imagen_procesada": img_procesada,
            "dimensiones": img.shape,
            "tratamientos_aplicados": self.tratamientos_aplicados,
            "ocr": ocr_result
        }
    
    def procesar_zona(self, imagen_bytes: bytes, zona: Tuple[int, int, int, int]) -> Dict:
        """Procesa imagen - VERSIÓN SIMPLIFICADA Y SUAVE"""
        self.tratamientos_aplicados = []
        
        img = self._cargar_imagen(imagen_bytes)
        if img is None:
            return {"error": "No se pudo cargar imagen"}
        
        img = self._upscale(img)
        img = self._crop_zona(img, zona)
        img = self._threshold_suave(img, valor=70)
        
        buffer = io.BytesIO()
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        Image.fromarray(img_rgb).save(buffer, format='PNG')
        img_procesada = buffer.getvalue()
        
        return {
            "exito": True,
            "imagen_procesada": img_procesada,
            "dimensiones": img.shape,
            "tratamientos_aplicados": self.tratamientos_aplicados
        }
    
    def _crear_carpeta_resultados(self):
        """Crea la carpeta de resultados si no existe"""
        carpeta = OCR_CONFIG["resultados_dir"]
        if not os.path.exists(carpeta):
            os.makedirs(carpeta)
            logger.info(f"[{self.tipo}] Carpeta creada: {carpeta}")
        return carpeta
    
    def guardar_resultado(self, imagen_bytes: bytes, zona_nombre: str, datos_adicionales: Dict = None) -> Dict:
        """Guarda imagen procesada y metadatos en JSON"""
        try:
            carpeta = self._crear_carpeta_resultados()
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            nombre_base = f"{self.tipo.replace(' ', '_')}_{zona_nombre}_{timestamp}"
            
            # Guardar imagen PNG
            ruta_imagen = os.path.join(carpeta, f"{nombre_base}.png")
            with open(ruta_imagen, 'wb') as f:
                f.write(imagen_bytes)
            logger.info(f"[{self.tipo}] Imagen guardada: {ruta_imagen}")
            
            # Guardar metadatos JSON
            metadatos = {
                "timestamp": timestamp,
                "tipo_cedula": self.tipo,
                "zona": zona_nombre,
                "tratamientos": self.tratamientos_aplicados,
                "ruta_imagen": ruta_imagen
            }
            if datos_adicionales:
                metadatos.update(datos_adicionales)
            
            ruta_json = os.path.join(carpeta, f"{nombre_base}.json")
            with open(ruta_json, 'w') as f:
                json.dump(metadatos, f, indent=2)
            logger.info(f"[{self.tipo}] Metadatos guardados: {ruta_json}")
            
            return {
                "exito": True,
                "ruta_imagen": ruta_imagen,
                "ruta_json": ruta_json,
                "metadatos": metadatos
            }
        
        except Exception as e:
            logger.error(f"[{self.tipo}] Error guardando resultado: {e}")
            return {"exito": False, "error": str(e)}
