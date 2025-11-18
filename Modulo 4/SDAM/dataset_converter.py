import xml.etree.ElementTree as ET
import os
import random
import shutil

# --- Configuración de Rutas ---
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
DATASET_PATH = os.path.join(PROJECT_ROOT, 'data', 'dataset')
VOC_ANNOTATIONS_PATH = os.path.join(DATASET_PATH, 'annotations')
IMAGES_PATH = os.path.join(DATASET_PATH, 'images')

# Rutas de Salida (Formato YOLO)
YOLO_OUTPUT_PATH = DATASET_PATH
TRAIN_RATIO = 0.8  # 80% para entrenamiento, 20% para validación
CLASS_ID = 0 

def convert_coordinates(size, box):
    """Convierte las coordenadas del formato Pascal VOC al formato YOLO normalizado."""
    dw = 1.0 / size[0]
    dh = 1.0 / size[1]
    
    xmin, ymin, xmax, ymax = box
    
    # Cálculos para YOLO
    x_center = (xmin + xmax) / 2.0
    y_center = (ymin + ymax) / 2.0
    w = xmax - xmin
    h = ymax - ymin
    
    # Normalización
    x_center = x_center * dw
    y_center = y_center * dh
    w = w * dw
    h = h * dh
    
    return (x_center, y_center, w, h)

def process_xml(xml_file, output_path):
    """Procesa un archivo XML y crea el archivo de texto YOLO correspondiente."""
    try:
        tree = ET.parse(xml_file)
        root = tree.getroot()
        
        size = root.find('size')
        if size is None: return False

        w = int(size.find('width').text)
        h = int(size.find('height').text)
        
        if w == 0 or h == 0: return False

        yolo_lines = []

        for obj in root.iter('object'):
            bbox = obj.find('bndbox')
            if bbox is None: continue
                
            xmin = int(float(bbox.find('xmin').text))
            ymin = int(float(bbox.find('ymin').text))
            xmax = int(float(bbox.find('xmax').text))
            ymax = int(float(bbox.find('ymax').text))
            
            normalized_box = convert_coordinates((w, h), (xmin, ymin, xmax, ymax))
            
            # Formato final: [class_id x_center y_center width height]
            line = f"{CLASS_ID} {normalized_box[0]:.6f} {normalized_box[1]:.6f} {normalized_box[2]:.6f} {normalized_box[3]:.6f}\n"
            yolo_lines.append(line)
            
        if yolo_lines:
            base_name = os.path.basename(xml_file).replace('.xml', '.txt')
            output_file = os.path.join(output_path, base_name)
            with open(output_file, 'w') as f:
                f.writelines(yolo_lines)
            return True
        return False

    except Exception as e:
        print(f"❌ Error al procesar el archivo {xml_file}: {e}")
        return False


def create_yolo_structure():
    """Crea la estructura de carpetas YOLOv8 (train/images, train/labels, val/images, val/labels)."""
    print("Iniciando conversión y división de dataset...")

    # Rutas de salida
    train_images = os.path.join(YOLO_OUTPUT_PATH, 'train', 'images')
    train_labels = os.path.join(YOLO_OUTPUT_PATH, 'train', 'labels')
    val_images = os.path.join(YOLO_OUTPUT_PATH, 'val', 'images')
    val_labels = os.path.join(YOLO_OUTPUT_PATH, 'val', 'labels')

    # Limpiar y crear la estructura de carpetas
    for d in [train_images, train_labels, val_images, val_labels]:
        if os.path.exists(d):
            shutil.rmtree(d)
        os.makedirs(d)
        
    xml_files = [f for f in os.listdir(VOC_ANNOTATIONS_PATH) if f.endswith('.xml')]
    if not xml_files:
        print(f"🛑 Error: No se encontraron archivos XML en {VOC_ANNOTATIONS_PATH}")
        return

    # Dividir los archivos
    random.shuffle(xml_files)
    split_index = int(len(xml_files) * TRAIN_RATIO)
    train_files = xml_files[:split_index]
    val_files = xml_files[split_index:]

    print(f"Total de archivos: {len(xml_files)}")
    print(f"Archivos de Entrenamiento: {len(train_files)}")
    print(f"Archivos de Validación: {len(val_files)}")
    print("-" * 30)

    # --- Procesamiento y Movimiento de Archivos de Entrenamiento ---
    print("Procesando datos de ENTRENAMIENTO...")
    for xml_file in train_files:
        xml_path = os.path.join(VOC_ANNOTATIONS_PATH, xml_file)
        base_name = xml_file.replace('.xml', '')
        
        if process_xml(xml_path, train_labels):
            # Mover la imagen correspondiente (.png o .jpg)
            for ext in ['.png', '.jpg']:
                image_name = base_name + ext
                image_src = os.path.join(IMAGES_PATH, image_name)
                image_dst = os.path.join(train_images, image_name)
                if os.path.exists(image_src):
                    shutil.copy(image_src, image_dst)
                    break
            else:
                print(f"⚠️ Imagen {base_name}.png/.jpg no encontrada. Omitiendo.")

    # --- Procesamiento y Movimiento de Archivos de Validación ---
    print("Procesando datos de VALIDACIÓN...")
    for xml_file in val_files:
        xml_path = os.path.join(VOC_ANNOTATIONS_PATH, xml_file)
        base_name = xml_file.replace('.xml', '')

        if process_xml(xml_path, val_labels):
            # Mover la imagen correspondiente (.png o .jpg)
            for ext in ['.png', '.jpg']:
                image_name = base_name + ext
                image_src = os.path.join(IMAGES_PATH, image_name)
                image_dst = os.path.join(val_images, image_name)
                if os.path.exists(image_src):
                    shutil.copy(image_src, image_dst)
                    break
            else:
                print(f"⚠️ Imagen {base_name}.png/.jpg no encontrada. Omitiendo.")

    print("-" * 30)
    print("✅ Conversión y división completada.")
    print("   El dataset está listo para entrenar en la carpeta 'data/dataset'.")

if __name__ == "__main__":
    
    if not os.path.exists(VOC_ANNOTATIONS_PATH) or not os.path.exists(IMAGES_PATH):
        print("🛑 ERROR: No se encontró la estructura de entrada del dataset.")
        print(f"   Asegúrate de tener las carpetas: data/dataset/annotations y data/dataset/images")
    else:
        create_yolo_structure()