from config.ocr_cedula_config import OCR_ZONAS
from services.ocr.base import BaseCedulaNacionalOCR
import re


# ====================================================
# VARIACIONES DE ETIQUETAS NOMBRES (Falsos negativos OCR)
# ====================================================
VARIACIONES_NOMBRES = [
    "NOMBRES",      # Correcto
    "MOMBRES",      # M por N (muy común en OCR)
    "NOMARES",      # Confusión de B con A
    "NOMBFES",      # F por R
    "NQMBRES",      # Q en lugar de U
]


class CedulaNacionalAntiguaOCR(BaseCedulaNacionalOCR):
    """OCR para cédulas antiguas de Ecuador - Lógica propia"""
    
    def __init__(self, tipo_camara: str = "peatonal"):
        """
        tipo_camara: "peatonal" o "vehicular"
        """
        super().__init__("Cédula Antigua")
        self.tipo_camara = tipo_camara
        self.zonas = OCR_ZONAS[tipo_camara]["antigua"]
    
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
        Regla: Busca "NOMBRES" 
               Lo que está ARRIBA (últimas 2 palabras) = APELLIDOS
               Lo que está ABAJO (primer componente) = NOMBRES
        """
        if not componentes_ocr:
            return {"apellidos": "", "nombres": "", "confianza_apellidos": 0, "confianza_nombres": 0}
        
        # Buscar índice de "NOMBRES" (buscando variaciones)
        indice_nombres = None
        for idx, comp in enumerate(componentes_ocr):
            texto = comp.get("texto", "").upper().strip()
            if texto in VARIACIONES_NOMBRES:
                indice_nombres = idx
                break
        
        # Si no encuentra "NOMBRES", retornar vacío
        if indice_nombres is None:
            return {"apellidos": "", "nombres": "", "confianza_apellidos": 0, "confianza_nombres": 0}
        
        # Tomar los 2 componentes DIRECTAMENTE ANTES de "NOMBRES" = APELLIDOS
        apellidos_componentes = []
        if indice_nombres >= 2:
            apellidos_componentes = componentes_ocr[indice_nombres - 2:indice_nombres]
        elif indice_nombres == 1:
            apellidos_componentes = componentes_ocr[indice_nombres - 1:indice_nombres]
        
        # Tomar el primer componente DIRECTAMENTE DESPUÉS de "NOMBRES" = NOMBRES
        nombres_componentes = []
        if indice_nombres + 1 < len(componentes_ocr):
            nombres_componentes = [componentes_ocr[indice_nombres + 1]]
        
        apellidos = " ".join([c.get("texto", "").strip() for c in apellidos_componentes])
        nombres = " ".join([c.get("texto", "").strip() for c in nombres_componentes])
        
        confianza_apellidos = sum([c.get("confianza", 0) for c in apellidos_componentes]) / len(apellidos_componentes) if apellidos_componentes else 0
        confianza_nombres = sum([c.get("confianza", 0) for c in nombres_componentes]) / len(nombres_componentes) if nombres_componentes else 0
        
        return {
            "apellidos": apellidos.strip(),
            "nombres": nombres.strip(),
            "confianza_apellidos": confianza_apellidos,
            "confianza_nombres": confianza_nombres
        }
    
    def procesar_numero_cedula(self, imagen_bytes: bytes):
        """
        Procesa zona del número de cédula de cédula antigua
        Extrae número en formato original (ej: 172193122-6)
        Guarda recorte procesado (imagen + OCR bruto en JSON)
        """
        resultado = self.procesar_zona_con_ocr(imagen_bytes, self.zonas["zona_numero"])
        
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
        resultado = self.procesar_zona_con_ocr(imagen_bytes, self.zonas["zona_nombres_apellidos"])
        
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
