from config.ocr_cedula_config import CEDULA_NUEVA
from services.ocr.base import BaseCedulaNacionalOCR


class CedulaNacionalNuevaOCR(BaseCedulaNacionalOCR):
    """OCR para cédulas nuevas de Ecuador"""
    
    def __init__(self):
        super().__init__("Cédula Nueva")
    
    def _parsear_nombres_apellidos(self, componentes_ocr):
        """
        Parsea componentes OCR para extraer APELLIDOS y NOMBRES
        Regla: Todo ANTES de 'NOMBRES' (sin etiquetas) = apellidos
               SOLO el primer componente DESPUÉS de 'NOMBRES' = nombres
        """
        if not componentes_ocr:
            return {"apellidos": "", "nombres": "", "confianza_apellidos": 0, "confianza_nombres": 0}
        
        # Buscar índice de la palabra "NOMBRES"
        indice_nombres = None
        for idx, comp in enumerate(componentes_ocr):
            if comp.get("texto", "").upper().strip() == "NOMBRES":
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
        
        # Palavras a ignorar (etiquetas y ruido)
        palabras_ignorar = ["APELLIDOS", "CONC", "NACIONALIDAD", "1CJiJ | n", ""]
        
        # Recolectar apellidos (antes de NOMBRES, sin etiquetas)
        apellidos_componentes = []
        for comp in componentes_ocr[:indice_nombres]:
            texto = comp.get("texto", "").upper().strip()
            # Ignorar etiquetas y ruido
            if texto and texto not in palabras_ignorar and comp.get("confianza", 0) > 0.3:
                apellidos_componentes.append(comp)
        
        # Recolectar SOLO EL PRIMER NOMBRE (después de NOMBRES)
        nombres_componentes = []
        for comp in componentes_ocr[indice_nombres + 1:]:  # +1 para saltar "NOMBRES"
            texto = comp.get("texto", "").upper().strip()
            # Tomar SOLO el primer componente válido después de NOMBRES
            if texto and texto not in palabras_ignorar and comp.get("confianza", 0) > 0.3:
                nombres_componentes.append(comp)
                break  # SOLO uno, el primero
        
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
        """Procesa zona del número de cédula CON OCR - retorna solo 10 dígitos"""
        resultado = self.procesar_zona_con_ocr(imagen_bytes, CEDULA_NUEVA["zona_numero"])
        
        if resultado.get("exito"):
            # Extraer el texto OCR completo
            texto_ocr = resultado.get("ocr", {}).get("texto_completo", "")
            confianza_ocr = self._calcular_confianza_promedio(resultado.get("ocr", {}).get("componentes", []))
            
            # Parsear número de cédula (extrae solo 10 dígitos, ignora NUI)
            numero_parseado = self._extraer_numero_cedula(texto_ocr, confianza_ocr)
            
            # Agregar al resultado
            resultado["numero_cedula_parseado"] = numero_parseado
            
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
        """Procesa zona de nombres y apellidos CON OCR Y PARSING"""
        resultado = self.procesar_zona_con_ocr(imagen_bytes, CEDULA_NUEVA["zona_nombres_apellidos"])
        
        if resultado.get("exito"):
            # Extraer componentes OCR
            componentes = resultado.get("ocr", {}).get("componentes", [])
            
            # Parsear nombres y apellidos
            parsed = self._parsear_nombres_apellidos(componentes)
            
            # Agregar datos parseados al resultado
            resultado["nombres_apellidos_parseados"] = parsed
            
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
