from config.ocr_cedula_config import OCR_ZONAS
from services.ocr.base import BaseCedulaNacionalOCR


# ====================================================
# VARIACIONES DE ETIQUETAS NOMBRES (Falsos negativos OCR)
# ====================================================
VARIACIONES_NOMBRES = [
    "NOMBRES",      # Correcto
    "MOMBRES",      # M por N (muy común en OCR)
    "NOMARES",      # Confusión de B con A
    "NOMBFES",      # F por R
    "NQMBRES",
    "NOMORES",     # Q en lugar de U
]


class CedulaNacionalNuevaOCR(BaseCedulaNacionalOCR):
    """OCR para cédulas nuevas de Ecuador"""
    
    def __init__(self, tipo_camara: str = "peatonal"):
        """
        tipo_camara: "peatonal" o "vehicular"
        """
        super().__init__("Cédula Nueva")
        self.tipo_camara = tipo_camara
        self.zonas = OCR_ZONAS[tipo_camara]["nueva"]
    
    def _parsear_nombres_apellidos(self, componentes_ocr):
        """
        Parsea componentes OCR para extraer APELLIDOS y NOMBRES
        Regla: SOLO LAS ÚLTIMAS 2 PALABRAS ANTES de 'NOMBRES' = apellidos
               SOLO el primer componente DESPUÉS de 'NOMBRES' = nombres
        """
        if not componentes_ocr:
            return {"apellidos": "", "nombres": "", "confianza_apellidos": 0, "confianza_nombres": 0}
        
        # Buscar índice de la palabra "NOMBRES" (buscando variaciones comunes de OCR)
        indice_nombres = None
        for idx, comp in enumerate(componentes_ocr):
            texto_componente = comp.get("texto", "").upper().strip()
            if texto_componente in VARIACIONES_NOMBRES:
                indice_nombres = idx
                break
        
        # Si no encuentra "NOMBRES", retornar todo como nombres
        if indice_nombres is None:
            texto_completo = " ".join([c.get("texto", "") for c in componentes_ocr])
            confianza_promedio = sum([c.get("confianza", 0) for c in componentes_ocr]) / len(componentes_ocr) if componentes_ocr else 0
            return {
                "apellidos": "",
                "nombres": texto_completo,
                "confianza_apellidos": 0,
                "confianza_nombres": confianza_promedio
            }
        
        # Tomar los 2 componentes DIRECTAMENTE ANTES de "NOMBRES" = APELLIDOS
        apellidos_componentes = []
        if indice_nombres >= 2:
            # Últimos 2 componentes antes de NOMBRES
            apellidos_componentes = componentes_ocr[indice_nombres - 2:indice_nombres]
        elif indice_nombres == 1:
            # Solo 1 componente antes de NOMBRES
            apellidos_componentes = componentes_ocr[indice_nombres - 1:indice_nombres]
        
        # Tomar el primer componente DIRECTAMENTE DESPUÉS de "NOMBRES" = NOMBRES
        nombres_componentes = []
        if indice_nombres + 1 < len(componentes_ocr):
            nombres_componentes = [componentes_ocr[indice_nombres + 1]]
        
        # Extraer texto y confianza
        apellidos_texto = " ".join([c.get("texto", "") for c in apellidos_componentes])
        nombres_texto = " ".join([c.get("texto", "") for c in nombres_componentes])
        
        confianza_apellidos = sum([c.get("confianza", 0) for c in apellidos_componentes]) / len(apellidos_componentes) if apellidos_componentes else 0
        confianza_nombres = sum([c.get("confianza", 0) for c in nombres_componentes]) / len(nombres_componentes) if nombres_componentes else 0
        
        return {
            "apellidos": apellidos_texto.strip(),
            "nombres": nombres_texto.strip(),
            "confianza_apellidos": confianza_apellidos,
            "confianza_nombres": confianza_nombres
        }
    
    def _extraer_numero_cedula(self, texto_ocr, confianza_ocr):
        
        import re

        if not texto_ocr:
            return {"numero": "", "confianza": 0}
        
        # Remover espacios
        texto_limpio = texto_ocr.strip()
        
        # Remover "NUI" o "NUI." del inicio
        if texto_limpio.upper().startswith("NUI."):
            texto_limpio = texto_limpio[4:]  # Remover "NUI."
        elif texto_limpio.upper().startswith("NUI"):
            texto_limpio = texto_limpio[3:]  # Remover "NUI"
        
        # Extraer SOLO los dígitos
        digitos = re.findall(r'\d', texto_limpio)
        numero = "".join(digitos)
        
        # Tomar solo los primeros 10 dígitos
        numero = numero[:10]
        
        return {
            "numero": numero,
            "confianza": confianza_ocr
        }
    
    def procesar_numero_cedula(self, imagen_bytes: bytes):
        """Procesa zona del número de cédula CON OCR - retorna solo 10 dígitos - SÍ guarda imagen y JSON"""
        resultado = self.procesar_zona_con_ocr(imagen_bytes, self.zonas["zona_numero"])
        
        if resultado.get("exito"):
            # Extraer el texto OCR completo
            texto_ocr = resultado.get("ocr", {}).get("texto_completo", "")
            confianza_ocr = self._calcular_confianza_promedio(resultado.get("ocr", {}).get("componentes", []))
            
            # Parsear número de cédula (extrae solo 10 dígitos, ignora NUI)
            numero_parseado = self._extraer_numero_cedula(texto_ocr, confianza_ocr)
            
            # Agregar al resultado
            resultado["numero_cedula_parseado"] = numero_parseado
            
            # Guardar imagen procesada y metadatos JSON
            guardado = self.guardar_resultado(
                resultado["imagen_procesada"],
                "numero_cedula",
                {
                    "dimensiones": str(resultado["dimensiones"]),
                    "ocr": resultado.get("ocr"),
                    "numero_cedula_parseado": numero_parseado
                }
            )
            resultado["guardado"] = guardado
        
        return resultado
    
    def _calcular_confianza_promedio(self, componentes):
        """Calcula la confianza promedio de los componentes OCR"""
        if not componentes:
            return 0.0
        confianzas = [c.get("confianza", 0) for c in componentes]
        return sum(confianzas) / len(confianzas) if confianzas else 0.0
    
    def procesar_nombres_apellidos(self, imagen_bytes: bytes):
        """Procesa zona de nombres y apellidos CON OCR Y PARSING - SÍ guarda imagen y JSON"""
        resultado = self.procesar_zona_con_ocr(imagen_bytes, self.zonas["zona_nombres_apellidos"])
        
        if resultado.get("exito"):
            # Extraer componentes OCR
            componentes = resultado.get("ocr", {}).get("componentes", [])
            
            # Parsear nombres y apellidos
            parsed = self._parsear_nombres_apellidos(componentes)
            
            # Agregar datos parseados al resultado
            resultado["nombres_apellidos_parseados"] = parsed
            
            # Guardar imagen procesada y metadatos JSON
            guardado = self.guardar_resultado(
                resultado["imagen_procesada"],
                "nombres_apellidos",
                {
                    "dimensiones": str(resultado["dimensiones"]),
                    "ocr": resultado.get("ocr"),
                    "nombres_apellidos_parseados": parsed
                }
            )
            resultado["guardado"] = guardado
        
        return resultado
    
    def procesar_cedula_completa(self, imagen_bytes: bytes):
        """Barrido completo de la cédula - extrae TODAS las zonas"""
        resultados = {
            "exito": True,
            "tipo_cedula": "Cédula Nueva",
            "timestamp": __import__("datetime").datetime.now().isoformat(),
            "zonas": {}
        }
        
        # Procesar zona de número
        resultado_numero = self.procesar_numero_cedula(imagen_bytes)
        resultados["zonas"]["numero"] = resultado_numero
        
        # Procesar zona de nombres y apellidos
        resultado_nombres = self.procesar_nombres_apellidos(imagen_bytes)
        resultados["zonas"]["nombres_apellidos"] = resultado_nombres
        
        # Resumen OCR en bruto
        resultados["resumen_ocr"] = {
            "numero": {
                "texto": resultado_numero.get("ocr", {}).get("texto_completo", ""),
                "confianza_promedio": self._calcular_confianza_promedio(
                    resultado_numero.get("ocr", {}).get("componentes", [])
                ),
                "componentes_detectados": resultado_numero.get("ocr", {}).get("cantidad_componentes", 0)
            },
            "nombres": {
                "texto": resultado_nombres.get("ocr", {}).get("texto_completo", ""),
                "confianza_promedio": self._calcular_confianza_promedio(
                    resultado_nombres.get("ocr", {}).get("componentes", [])
                ),
                "componentes_detectados": resultado_nombres.get("ocr", {}).get("cantidad_componentes", 0)
            }
        }
        
        return resultados
    
    def _calcular_confianza_promedio(self, componentes):
        """Calcula la confianza promedio de los componentes OCR"""
        if not componentes:
            return 0.0
        confianzas = [c.get("confianza", 0) for c in componentes]
        return sum(confianzas) / len(confianzas) if confianzas else 0.0
