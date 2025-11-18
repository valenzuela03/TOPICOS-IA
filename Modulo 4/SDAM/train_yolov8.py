from ultralytics import YOLO
import os

# --- Configuración de Rutas ---
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(PROJECT_ROOT, 'data', 'placas_config.yaml')
# La ruta de salida se usa dentro de la función train_model
# MODEL_OUTPUT_DIR = os.path.join(PROJECT_ROOT, 'models', 'placas_yolov8n') 

def train_model():
    """
    Carga un modelo YOLOv8 pre-entrenado y lo entrena con el dataset de placas.
    """
    print("--- 🚀 INICIANDO ENTRENAMIENTO YOLOv8 ---")
    
    if not os.path.exists(CONFIG_PATH):
        print(f"🛑 ERROR: Archivo de configuración no encontrado en: {CONFIG_PATH}")
        print("Asegúrate de haber creado 'data/placas_config.yaml'.")
        return

    try:
        # Cargar un modelo YOLOv8 Nano pre-entrenado
        # Este es el modelo más pequeño y rápido, ideal para empezar.
        model = YOLO('yolov8n.pt')
        print("✅ Modelo YOLOv8n pre-entrenado cargado.")
        
        # Iniciar el entrenamiento
        # data: Ruta al archivo .yaml de configuración del dataset
        # epochs: Número de veces que el modelo verá el dataset completo. 50 es un buen inicio.
        # imgsz: Tamaño de la imagen de entrada (640x640 es estándar).
        # project: Carpeta donde se guardarán los resultados del entrenamiento.
        # name: Subcarpeta específica para esta corrida de entrenamiento.
        
        results = model.train(
            data=CONFIG_PATH, 
            epochs=50, 
            imgsz=640,
            project=os.path.join(PROJECT_ROOT, 'models'),
            name='placas_yolov8n'
        )
        
        print("\n--- ✅ ENTRENAMIENTO FINALIZADO CON ÉXITO ---")
        print(f"Los resultados (pesos del modelo, métricas) se guardaron en: {os.path.join(PROJECT_ROOT, 'models', 'placas_yolov8n', 'weights', 'best.pt')}")

    except Exception as e:
        print(f"❌ Ocurrió un error durante el entrenamiento: {e}")
        print("Asegúrate de que la estructura de tus datos sea correcta y las dependencias estén instaladas.")

if __name__ == "__main__":
    train_model()