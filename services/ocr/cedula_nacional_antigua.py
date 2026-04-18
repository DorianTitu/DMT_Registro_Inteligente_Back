from config.ocr_cedula_config import CEDULA_ANTIGUA
from services.ocr.base import BaseCedulaNacionalOCR


class CedulaNacionalAntiguaOCR(BaseCedulaNacionalOCR):
    """OCR para cédulas antiguas de Ecuador"""
    
    def __init__(self):
        super().__init__("Cédula Antigua")
    
    def procesar_numero_cedula(self, imagen_bytes: bytes):
        """Procesa zona del número de cédula"""
        resultado = self.procesar_zona(imagen_bytes, CEDULA_ANTIGUA["zona_numero"])
        
        if resultado.get("exito"):
            guardado = self.guardar_resultado(
                resultado["imagen_procesada"],
                "numero_cedula",
                {"dimensiones": str(resultado["dimensiones"])}
            )
            resultado["guardado"] = guardado
        
        return resultado
    
    def procesar_nombres_apellidos(self, imagen_bytes: bytes):
        """Procesa zona de nombres y apellidos"""
        resultado = self.procesar_zona(imagen_bytes, CEDULA_ANTIGUA["zona_nombres_apellidos"])
        
        if resultado.get("exito"):
            guardado = self.guardar_resultado(
                resultado["imagen_procesada"],
                "nombres_apellidos",
                {"dimensiones": str(resultado["dimensiones"])}
            )
            resultado["guardado"] = guardado
        
        return resultado
