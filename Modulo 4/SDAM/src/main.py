import sqlite3
import os
import cv2
from paddleocr import PaddleOCR
import numpy as np
import re
from ultralytics import YOLO

# --- Configuración de Rutas ---
# __file__ está en src/. Retrocede (..) para llegar a SDAM/
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
DB_FILE_NAME = "matriculas.db"
DB_FILE = os.path.join(PROJECT_ROOT, "db", DB_FILE_NAME)
IMAGE_PATH = os.path.join(PROJECT_ROOT, 'data', 'raw', 'Cars2.png')
MODEL_PATH = os.path.join(PROJECT_ROOT, 'models', 'best.pt')
            

# --- Módulo de Visión Artificial (Paso 2: Integración YOLO) ---

def detectar_y_leer_placa(image_path: str) -> str | None:
    """
    Usa el modelo YOLOv8 para detectar la placa y paddleocr para leer los caracteres.
    """
    print(f"--- 🧠 Procesando Imagen: {image_path} ---")

    if not os.path.exists(MODEL_PATH):
        print(f"ERROR: Modelo entrenado no encontrado en: {MODEL_PATH}")
        return "ABC123" 

    if not os.path.exists(image_path):
        print(f"Imagen no encontrada en: {image_path}")
        return "ABC123"

    # --- CORRECCIÓN PRINCIPAL: Cargar la imagen en memoria ---
    img_original = cv2.imread(image_path)
    if img_original is None:
        print("Error: No se pudo leer el archivo de imagen con OpenCV.")
        return None
    # ---------------------------------------------------------

    # Iniciar el modelo
    model = YOLO(MODEL_PATH)
    ocr = PaddleOCR(use_angle_cls=True, lang='en')

    blacklist = ["grupo", "premie", "premier", "mx", "com", "agency", "automotriz"]
    plate_pattern = r'^[A-Z0-9]{5,8}$' # Mover el patrón aquí para eficiencia

    results = model(image_path)

    for result in results:
        # Verificar si hay detecciones
        if result.boxes is None or len(result.boxes) == 0:
            continue

        index_plates = (result.boxes.cls == 0).nonzero(as_tuple=True)[0]

        for idx in index_plates:
            conf = result.boxes.conf[idx].item()
            print("confianza:", conf)
            
            if conf > 0.5:
                xyxy = result.boxes.xyxy[idx].squeeze().tolist()
                x1, y1 = int(xyxy[0]), int(xyxy[1])
                x2, y2 = int(xyxy[2]), int(xyxy[3])

                # --- CORRECCIÓN: Recortar sobre la variable de imagen (img_original), no el path ---
                # Aseguramos que las coordenadas no sean negativas para evitar errores
                y1_c, y2_c = max(0, y1-15), min(img_original.shape[0], y2+15)
                x1_c, x2_c = max(0, x1-15), min(img_original.shape[1], x2+15)
                
                plate_image = img_original[y1_c:y2_c, x1_c:x2_c]
                # ----------------------------------------------------------------------------------

                # PaddleOCR estándar devuelve una lista de listas, ajustado aquí:
                result_ocr = ocr.predict(cv2.cvtColor(plate_image, cv2.COLOR_BGR2RGB))
                
                # Validación extra por si OCR no detecta nada en el recorte
                if result_ocr is None or result_ocr[0] is None:
                    continue

                texts = result_ocr[0]["rec_texts"]
                plate_pattern = r'^[A-Z0-9]{5,8}$'


                for text in texts:
                    cleaned_text = re.sub(r'[^A-Za-z0-9]', '', text).upper()

                    # Ignorar textos vacíos
                    if len(cleaned_text) == 0:
                        continue

                    # Ignorar palabras en lista negra
                    if any(b in cleaned_text.lower() for b in blacklist):
                        continue

                    # Filtrar por patrón de placa
                    if not re.match(plate_pattern, cleaned_text):
                        continue

                    # Si pasa todos los filtros, esto sí es una placa real
                    print("Detected Plate Text:", cleaned_text)
                    return cleaned_text
    return None

# --- Módulo de Vinculación de Base de Datos (Paso 3) ---

def buscar_datos_vehiculo(placa_numero: str):
    """
    Consulta la base de datos para obtener los datos del vehículo y propietario.
    """
    conn = None
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        placa_sin_guiones = placa_numero
        
        query = """
        SELECT
            V.placa_numero, V.marca, V.modelo, V.anio,
            P.nombre, P.datos_contacto, P.direccion
        FROM Vehiculos V
        JOIN Propietarios P ON V.owner_id = P.owner_id
        WHERE V.placa_numero = ?;
        """
        
        cursor.execute(query, (placa_sin_guiones,))
        resultado = cursor.fetchone()
        
        if resultado:
            return {
                'placa': resultado[0],
                'marca': resultado[1],
                'modelo': resultado[2],
                'anio': resultado[3],
                'propietario_nombre': resultado[4],
                'propietario_contacto': resultado[5],
                'propietario_direccion': resultado[6]
            }
        else:
            return None
            
    except sqlite3.Error as e:
        print(f"Error de Base de Datos: {e}")
        return None
    finally:
        if conn:
            conn.close()

# --- Función Principal ---

def main():
    """Ejecuta el flujo completo del sistema SDAM."""
    
    if not os.path.exists(DB_FILE):
        print("------------------------------------------------------------------")
        print("ERROR: Base de Datos no encontrada.")
        print("   Por favor, ejecute el script de configuración primero:")
        print("   python src/linking_system/setup_db.py")
        print("------------------------------------------------------------------")
        return

    placa_detectada_limpia = detectar_y_leer_placa(IMAGE_PATH)
    
    if not placa_detectada_limpia:
        print("\n No se pudo determinar la matrícula. Finalizando.")
        return

    print(f"\n--- 🔎 Buscando Matrícula '{placa_detectada_limpia}' en DB ---")
    datos_vehiculo = buscar_datos_vehiculo(placa_detectada_limpia)

    if datos_vehiculo:
        print("\n RESULTADO ENCONTRADO:")
        print("----------------------------------")
        print(f"Matrícula: {datos_vehiculo['placa']}")
        print(f"Marca/Modelo: {datos_vehiculo['marca']} {datos_vehiculo['modelo']} ({datos_vehiculo['anio']})")
        print("----------------------------------")
        print(f"Propietario: {datos_vehiculo['propietario_nombre']}")
        print(f"Contacto: {datos_vehiculo['propietario_contacto']}")
        print(f"Dirección: {datos_vehiculo['propietario_direccion']}")
        print("----------------------------------")
    else:
        print(f"\n Matrícula '{placa_detectada_limpia}' no encontrada en la base de datos.")


if __name__ == "__main__":
    main()