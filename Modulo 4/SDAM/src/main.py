import sqlite3
import os
import cv2
import pytesseract
import numpy as np
from ultralytics import YOLO

# --- Configuración de Rutas ---
# __file__ está en src/. Retrocede (..) para llegar a SDAM/
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
DB_FILE_NAME = "matriculas.db"
DB_FILE = os.path.join(PROJECT_ROOT, "db", DB_FILE_NAME)
IMAGE_PATH = os.path.join(PROJECT_ROOT, 'data', 'raw', 'Cars2.png')
MODEL_PATH = os.path.join(PROJECT_ROOT, 'models', 'placas_yolov8n', 'weights', 'best.pt')


# --- Módulo de Visión Artificial (Paso 2: Integración YOLO) ---

def detectar_y_leer_placa(image_path: str) -> str | None:
    """
    Usa el modelo YOLOv8 para detectar la placa y Tesseract para leer los caracteres.
    """
    print(f"--- 🧠 Procesando Imagen: {image_path} ---")

    if not os.path.exists(MODEL_PATH):
        print(f"🛑 ERROR: Modelo entrenado no encontrado en: {MODEL_PATH}")
        print("   Asegúrate de ejecutar 'python train_yolov8.py' primero.")
        return "ABC123" # Fallback para demostrar la DB

    if not os.path.exists(image_path):
        print(f"⚠️ Imagen no encontrada en: {image_path}")
        return "ABC123"

    try:
        # 1. Cargar el modelo entrenado
        model = YOLO(MODEL_PATH)
        print("✅ Modelo YOLOv8n cargado exitosamente.")
        
        # 2. Cargar la imagen
        img = cv2.imread(image_path)
        if img is None:
            raise FileNotFoundError(f"No se pudo cargar la imagen: {image_path}. Asegúrese del formato.")

        # 3. Detección con YOLOv8
        # device='cpu' se usa aquí para compatibilidad general. Si quieres usar MPS/GPU, usa device='mps'
        results = model(img, verbose=False, device='cpu') 
        
        detecciones = results[0].boxes.xyxy
        
        if len(detecciones) == 0:
            print("⚠️ YOLOv8 no detectó ninguna placa en la imagen.")
            return "ABC123" # Fallback

        # Tomar la primera detección (placa con mayor confianza)
        # Las coordenadas están en formato [x1, y1, x2, y2]
        x1, y1, x2, y2 = map(int, detecciones[0])
        
        # 4. Recortar la matrícula con las coordenadas detectadas
        cropped_img = img[y1:y2, x1:x2]
        print(f"✅ Placa detectada y recortada en coordenadas: ({x1}, {y1}) a ({x2}, {y2})")

        # 5. Preprocesamiento para OCR (Solo en el recorte)
        gray = cv2.cvtColor(cropped_img, cv2.COLOR_BGR2GRAY) 
        
        # Aplicar contraste adaptativo (CLAHE)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        contrasted = clahe.apply(gray)
        
        # Binarización
        _, thresh = cv2.threshold(contrasted, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # 6. Reconocimiento de Caracteres (OCR)
        custom_config = r'--oem 3 --psm 8 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
        placa_raw = pytesseract.image_to_string(thresh, config=custom_config)
        
        # 7. Limpieza de la matrícula
        placa_limpia = ''.join(filter(str.isalnum, placa_raw)).upper()
        
        
        if not placa_limpia or len(placa_limpia) < 6:
             print("⚠️ El OCR (Tesseract) falló al leer los caracteres del recorte de la placa.")
             return "ABC123" # Fallback si no se puede leer la placa real
        
        print(f"✅ OCR exitoso. Matrícula detectada (Limpia): '{placa_limpia}'")
        
        return placa_limpia 
        
    except pytesseract.TesseractNotFoundError:
        print("❌ ERROR: Tesseract OCR no está instalado o no se encuentra en el PATH.")
        return "ABC123"
    except Exception as e:
        print(f"❌ Error durante el proceso de Visión Artificial: {e}")
        return "ABC123"
        

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
        print(f"❌ Error de Base de Datos: {e}")
        return None
    finally:
        if conn:
            conn.close()

# --- Función Principal ---

def main():
    """Ejecuta el flujo completo del sistema SDAM."""
    
    if not os.path.exists(DB_FILE):
        print("------------------------------------------------------------------")
        print("🛑 ERROR: Base de Datos no encontrada.")
        print("   Por favor, ejecute el script de configuración primero:")
        print("   python src/linking_system/setup_db.py")
        print("------------------------------------------------------------------")
        return

    placa_detectada_limpia = detectar_y_leer_placa(IMAGE_PATH)
    
    if not placa_detectada_limpia:
        print("\n❌ No se pudo determinar la matrícula. Finalizando.")
        return

    print(f"\n--- 🔎 Buscando Matrícula '{placa_detectada_limpia}' en DB ---")
    datos_vehiculo = buscar_datos_vehiculo(placa_detectada_limpia)

    if datos_vehiculo:
        print("\n✅ RESULTADO ENCONTRADO:")
        print("----------------------------------")
        print(f"Matrícula: {datos_vehiculo['placa']}")
        print(f"Marca/Modelo: {datos_vehiculo['marca']} {datos_vehiculo['modelo']} ({datos_vehiculo['anio']})")
        print("----------------------------------")
        print(f"Propietario: {datos_vehiculo['propietario_nombre']}")
        print(f"Contacto: {datos_vehiculo['propietario_contacto']}")
        print(f"Dirección: {datos_vehiculo['propietario_direccion']}")
        print("----------------------------------")
    else:
        print(f"\n❌ Matrícula '{placa_detectada_limpia}' no encontrada en la base de datos.")


if __name__ == "__main__":
    main()