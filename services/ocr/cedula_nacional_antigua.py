from config.ocr_cedula_config import CEDULA_ANTIGUA
from services.ocr.base import BaseCedulaNacionalOCR
import re


class CedulaNacionalAntiguaOCR(BaseCedulaNacionalOCR):
    """OCR para cédulas antiguas de Ecuador - Lógica propia"""
    
    def __init__(self):
        super().__init__("Cédula Antigua")
    
    def _extraer_numero_cedula_antigua(self, componentes_ocr):
        """
        Extrae número de cédula antigua
        Busca el componente que tenga el patrón "No.", "Vo." o similar
        Retorna solo los 10 dígitos (ignora guión)
        """
        if not componentes_ocr:
            return {"numero": "", "confianza": 0}
        
        # Buscar componente que contenga solo números y posible guión
        for comp in componentes_ocr:
            texto = comp.get("texto", "").strip()
            confianza = comp.get("confianza", 0)
            
            # Buscar patrones como "172193122-6" o solo dígitos
            if re.search(r'\d', texto):
                # Extraer SOLO los dígitos (ignorar guión)
                numero = re.sub(r'[^0-9]', '', texto).strip()
                
                # Si tiene 10+ dígitos, retornar
                if len(numero) >= 10:
                    return {
                        "numero": numero[:10],  # Solo primeros 10 dígitos
                        "confianza": confianza
                    }
        
        return {"numero": "", "confianza": 0}
    
    def _parsear_nombres_apellidos_antigua(self, componentes_ocr):
        """
        Parsea nombres y apellidos de cédula antigua
        Busca etiqueta "APELLIDOS Y NOMBRES"
        Siguiente componente = apellidos
        Componente después = nombres
        """
        if not componentes_ocr:
            return {"apellidos": "", "nombres": "", "confianza_apellidos": 0, "confianza_nombres": 0}
        
        # Buscar índice de la etiqueta "APELLIDOS Y NOMBRES"
        indice_etiqueta = None
        for idx, comp in enumerate(componentes_ocr):
            texto = comp.get("texto", "").upper().strip()
            if "APELLIDOS Y NOMBRES" in texto or "APELLIDOS" in texto:
                indice_etiqueta = idx
                break
        
        # Si no encuentra etiqueta, retornar vacío
        if indice_etiqueta is None:
            return {"apellidos": "", "nombres": "", "confianza_apellidos": 0, "confianza_nombres": 0}
        
        # El siguiente componente es APELLIDOS
        apellidos_componente = None
        apellidos_confianza = 0
        if indice_etiqueta + 1 < len(componentes_ocr):
            apellidos_componente = componentes_ocr[indice_etiqueta + 1]
            apellidos_confianza = apellidos_componente.get("confianza", 0)
        
        # El componente después es NOMBRES
        nombres_componente = None
        nombres_confianza = 0
        if indice_etiqueta + 2 < len(componentes_ocr):
            nombres_componente = componentes_ocr[indice_etiqueta + 2]
            nombres_confianza = nombres_componente.get("confianza", 0)
        
        apellidos = apellidos_componente.get("texto", "").strip() if apellidos_componente else ""
        nombres = nombres_componente.get("texto", "").strip() if nombres_componente else ""
        
        return {
            "apellidos": apellidos,
            "nombres": nombres,
            "confianza_apellidos": apellidos_confianza,
            "confianza_nombres": nombres_confianza
        }
    
    def procesar_numero_cedula(self, imagen_bytes: bytes):
        """
        Procesa zona del número de cédula de cédula antigua
        Extrae número en formato original (ej: 172193122-6)
        Guarda recorte procesado (imagen + OCR bruto en JSON)
        """
        resultado = self.procesar_zona_con_ocr(imagen_bytes, CEDULA_ANTIGUA["zona_numero"])
        
        if resultado.get("exito"):
            # Extraer número de cédula
            componentes = resultado.get("ocr", {}).get("componentes", [])
            numero_parseado = self._extraer_numero_cedula_antigua(componentes)
            
            # Agregar al resultado
            resultado["numero_cedula_parseado"] = numero_parseado
            
            # Guardar recorte con OCR y número extraído
            guardado = self.guardar_resultado(
                resultado["imagen_procesada"],
                "numero_cedula",
                {
                    "dimensiones": str(resultado["dimensiones"]),
                    "ocr_bruto": resultado.get("ocr", {}),
                    "numero_cedula_parseado": numero_parseado,
                    "tratamientos": resultado.get("tratamientos_aplicados")
                }
            )
            resultado["guardado"] = guardado
        
        return resultado
    
    def procesar_nombres_apellidos(self, imagen_bytes: bytes):
        """
        Procesa zona de nombres y apellidos de cédula antigua
        Estructura: Etiqueta → Apellidos → Nombres
        Guarda recorte procesado (imagen + OCR bruto + parsing en JSON)
        """
        resultado = self.procesar_zona_con_ocr(imagen_bytes, CEDULA_ANTIGUA["zona_nombres_apellidos"])
        
        if resultado.get("exito"):
            # Extraer componentes OCR
            componentes = resultado.get("ocr", {}).get("componentes", [])
            
            # Parsear nombres y apellidos (lógica antigua)
            parsed = self._parsear_nombres_apellidos_antigua(componentes)
            
            # Agregar datos parseados al resultado
            resultado["nombres_apellidos_parseados"] = parsed
            
            # Guardar recorte con OCR y datos parseados
            guardado = self.guardar_resultado(
                resultado["imagen_procesada"],
                "nombres_apellidos",
                {
                    "dimensiones": str(resultado["dimensiones"]),
                    "ocr_bruto": resultado.get("ocr", {}),
                    "nombres_apellidos_parseados": parsed,
                    "tratamientos": resultado.get("tratamientos_aplicados")
                }
            )
            resultado["guardado"] = guardado
        
        return resultado
