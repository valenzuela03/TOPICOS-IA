import sqlite3
import os
import cv2
from paddleocr import PaddleOCR
import numpy as np
import re
from ultralytics import YOLO

# --- Configuración de Rutas ---
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
DB_FILE_NAME = "matriculas.db"
DB_FILE = os.path.join(PROJECT_ROOT, "db", DB_FILE_NAME)
# IMAGE_PATH ya no es necesario para la cámara
MODEL_PATH = os.path.join(PROJECT_ROOT, 'models', 'best.pt')
            

# --- Módulo de Visión Artificial (Modificado para Cámara) ---

def detectar_y_leer_placa(frame, model, ocr) -> str | None:
    """
    Usa el modelo YOLOv8 y PaddleOCR sobre un frame de video.
    """
    # Validar que el frame existe
    if frame is None:
        return None

    blacklist = ["grupo", "premie", "premier", "mx", "com", "agency", "automotriz"]
    plate_pattern = r'^[A-Z0-9]{5,8}$' 

    # Detección sobre el frame (verbose=False para no saturar consola)
    results = model(frame, verbose=False)

    for result in results:
        if result.boxes is None or len(result.boxes) == 0:
            continue

        index_plates = (result.boxes.cls == 0).nonzero(as_tuple=True)[0]

        for idx in index_plates:
            conf = result.boxes.conf[idx].item()
            
            if conf > 0.5:
                xyxy = result.boxes.xyxy[idx].squeeze().tolist()
                x1, y1 = int(xyxy[0]), int(xyxy[1])
                x2, y2 = int(xyxy[2]), int(xyxy[3])

                # Dibujar recuadro de detección
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

                # Recortar
                y1_c, y2_c = max(0, y1-15), min(frame.shape[0], y2+15)
                x1_c, x2_c = max(0, x1-15), min(frame.shape[1], x2+15)
                
                plate_image = frame[y1_c:y2_c, x1_c:x2_c]

                # PaddleOCR predict
                try:
                    result_ocr = ocr.predict(cv2.cvtColor(plate_image, cv2.COLOR_BGR2RGB))
                except Exception:
                    continue
                
                if result_ocr is None or result_ocr[0] is None:
                    continue

                texts = result_ocr[0]["rec_texts"]

                for text in texts:
                    cleaned_text = re.sub(r'[^A-Za-z0-9]', '', text).upper()

                    if len(cleaned_text) == 0: continue
                    if any(b in cleaned_text.lower() for b in blacklist): continue
                    if not re.match(plate_pattern, cleaned_text): continue

                    print("Placa detectada:", cleaned_text)
                    return cleaned_text
    return None

# --- Módulo de Vinculación de Base de Datos ---

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
    if not os.path.exists(DB_FILE):
        print("ERROR: Base de Datos no encontrada.")
        return

    # 1. Cargar modelos UNA VEZ antes del bucle
    print("--- Cargando modelos... ---")
    if not os.path.exists(MODEL_PATH):
        print(f"ERROR: Modelo no encontrado en {MODEL_PATH}")
        return
        
    model = YOLO(MODEL_PATH)
    # Usamos la config original
    ocr = PaddleOCR(use_angle_cls=True, lang='en')

    # 2. Configuración de Cámara
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("No se pudo abrir la cámara.")
        return
    
    cap.set(3, 640)
    cap.set(4, 480)

    print("\n--- Sistema iniciado. Presiona 'q' para salir ---")

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        # Procesar frame
        placa_detectada = detectar_y_leer_placa(frame, model, ocr)

        if placa_detectada:
            datos_vehiculo = buscar_datos_vehiculo(placa_detectada)
            
            if datos_vehiculo:
                # Mostrar datos en pantalla
                texto = f"{datos_vehiculo['placa']} - {datos_vehiculo['propietario_nombre']}"
                cv2.putText(frame, texto, (20, 450), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                
                # Imprimir en consola una sola vez (opcional, para no saturar)
                print(f"Encontrado: {texto}")
            else:
                cv2.putText(frame, f"{placa_detectada} - No Registrado", (20, 450), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

        cv2.imshow('Sistema SDAM', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()