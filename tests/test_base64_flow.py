"""
Script de prueba para validar el flujo Base64 end-to-end
Prueba: Captura → Base64 → OCR
"""
import requests
import base64
import json
from pathlib import Path

BASE_URL = "http://localhost:8000"

def test_camera_capture():
    """Prueba captura de cámara y verifica que retorna Base64"""
    print("\n" + "="*60)
    print("TEST 1: Captura de Cámara (Peatonal Cédula)")
    print("="*60)
    
    try:
        response = requests.get(
            f"{BASE_URL}/camaras/peatonal-cedula/imagen",
            params={"aplicar_crop": False},
            timeout=10
        )
        response.raise_for_status()
        
        data = response.json()
        print(f"✓ Respuesta recibida")
        print(f"  - Canal: {data.get('canal')}")
        print(f"  - Tipo: {data.get('tipo')}")
        print(f"  - Tamaño Base64: {len(data.get('imagen_base64', ''))} caracteres")
        
        if "imagen_base64" in data and len(data["imagen_base64"]) > 0:
            print(f"✓ Base64 válido recibido")
            return data["imagen_base64"]
        else:
            print(f"✗ No se recibió Base64")
            return None
            
    except Exception as e:
        print(f"✗ Error en captura: {e}")
        return None


def test_ocr_numero(imagen_base64):
    """Prueba OCR con imagen Base64 - Número de cédula"""
    print("\n" + "="*60)
    print("TEST 2: OCR - Número de Cédula (Base64 input)")
    print("="*60)
    
    try:
        payload = {
            "imagen_base64": imagen_base64
        }
        
        response = requests.post(
            f"{BASE_URL}/ocr/cedula-nueva/numero",
            json=payload,
            timeout=20
        )
        response.raise_for_status()
        
        data = response.json()
        print(f"✓ Respuesta OCR recibida")
        print(f"  - Tipo: {data.get('tipo')}")
        print(f"  - Zona: {data.get('zona')}")
        print(f"  - Número: {data.get('numero_cedula')}")
        print(f"  - Confianza: {data.get('confianza'):.2%}")
        
        return data
        
    except requests.exceptions.RequestException as e:
        print(f"✗ Error en OCR: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"  Respuesta: {e.response.text}")
        return None


def test_ocr_nombres_apellidos(imagen_base64):
    """Prueba OCR con imagen Base64 - Nombres y Apellidos"""
    print("\n" + "="*60)
    print("TEST 3: OCR - Nombres y Apellidos (Base64 input)")
    print("="*60)
    
    try:
        payload = {
            "imagen_base64": imagen_base64
        }
        
        response = requests.post(
            f"{BASE_URL}/ocr/cedula-nueva/nombres-apellidos",
            json=payload,
            timeout=20
        )
        response.raise_for_status()
        
        data = response.json()
        print(f"✓ Respuesta OCR recibida")
        print(f"  - Tipo: {data.get('tipo')}")
        print(f"  - Zona: {data.get('zona')}")
        print(f"  - Apellidos: {data.get('apellidos')}")
        print(f"  - Confianza Apellidos: {data.get('confianza_apellidos'):.2%}")
        print(f"  - Nombres: {data.get('nombres')}")
        print(f"  - Confianza Nombres: {data.get('confianza_nombres'):.2%}")
        
        return data
        
    except requests.exceptions.RequestException as e:
        print(f"✗ Error en OCR: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"  Respuesta: {e.response.text}")
        return None


def test_with_file(archivo_imagen):
    """Prueba OCR con archivo local (convierte a Base64 primero)"""
    print("\n" + "="*60)
    print(f"TEST 4: OCR con archivo local - {archivo_imagen.name}")
    print("="*60)
    
    try:
        # Leer imagen y convertir a Base64
        with open(archivo_imagen, "rb") as f:
            imagen_bytes = f.read()
            imagen_base64 = base64.b64encode(imagen_bytes).decode()
        
        print(f"✓ Archivo cargado: {archivo_imagen.name}")
        print(f"  - Tamaño: {len(imagen_bytes)} bytes")
        print(f"  - Base64: {len(imagen_base64)} caracteres")
        
        # Enviar a OCR
        payload = {"imagen_base64": imagen_base64}
        
        response = requests.post(
            f"{BASE_URL}/ocr/cedula-nueva/numero",
            json=payload,
            timeout=20
        )
        response.raise_for_status()
        
        data = response.json()
        print(f"\n✓ OCR procesado exitosamente")
        print(f"  - Número: {data.get('numero_cedula')}")
        print(f"  - Confianza: {data.get('confianza'):.2%}")
        
        return data
        
    except FileNotFoundError:
        print(f"✗ Archivo no encontrado: {archivo_imagen}")
        return None
    except Exception as e:
        print(f"✗ Error: {e}")
        return None


def main():
    """Ejecuta todas las pruebas"""
    print("\n" + "="*60)
    print("PRUEBA DE FLUJO BASE64 END-TO-END")
    print("="*60)
    
    # Test 1: Captura en vivo
    imagen_base64 = test_camera_capture()
    
    if imagen_base64:
        # Test 2 & 3: OCR con Base64 de captura
        test_ocr_numero(imagen_base64)
        test_ocr_nombres_apellidos(imagen_base64)
    
    # Test 4: Prueba con archivo local
    snapshot_dir = Path(__file__).parent.parent / "snapshots_cedula"
    if snapshot_dir.exists():
        imagenes = list(snapshot_dir.glob("*.jpg")) + list(snapshot_dir.glob("*.png"))
        if imagenes:
            print(f"\n✓ Se encontraron {len(imagenes)} imágenes locales")
            # Usar la primera imagen disponible
            test_with_file(imagenes[0])
        else:
            print(f"\n⚠ No hay imágenes en {snapshot_dir}")
    
    print("\n" + "="*60)
    print("PRUEBAS COMPLETADAS")
    print("="*60)


if __name__ == "__main__":
    main()
