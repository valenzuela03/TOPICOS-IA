import sqlite3
import os
import uuid

# --- Configuración de Rutas ---
# __file__ está en la raíz del proyecto (SDAM/).
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
DB_FILE_NAME = "matriculas.db"
DB_FILE = os.path.join(PROJECT_ROOT, "db", DB_FILE_NAME)

def add_data():
    """
    Agrega una nueva matrícula y propietario a la base de datos de prueba.
    """
    
    # Datos a insertar
    new_placa = 'VJK525C'  # Matrícula REAL del vehículo
    
    # Generar un ID único para el nuevo propietario
    new_owner_id = str(uuid.uuid4())
    
    # Datos del nuevo propietario
    owner_name = 'Carlos Beltran'
    owner_contact = 'Tel: +52 667 485 2854'
    owner_address = 'Blvd Santa anita'
    
    # Datos del nuevo vehículo (El auto de la imagen)
    vehicle_marca = 'ford'
    vehicle_modelo = 'fiesta'
    vehicle_anio = 2005

    conn = None
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        print(f"Conexión a la base de datos '{DB_FILE_NAME}' establecida.")
        
        # 1. Insertar nuevo propietario
        owner_data = (new_owner_id, owner_name, owner_contact, owner_address)
        cursor.execute("INSERT INTO Propietarios VALUES (?, ?, ?, ?)", owner_data)
        print(f"Propietario '{owner_name}' agregado.")
        
        # 2. Insertar nuevo vehículo
        vehicle_data = (new_placa, vehicle_marca, vehicle_modelo, vehicle_anio, new_owner_id)
        cursor.execute("INSERT INTO Vehiculos VALUES (?, ?, ?, ?, ?)", vehicle_data)
        print(f"Vehículo con placa '{new_placa}' agregado y vinculado a '{owner_name}'.")

        conn.commit()
        
    except sqlite3.IntegrityError:
        print(f"a placa '{new_placa}' ya existe en la base de datos.")
    except sqlite3.Error as e:
        print(f"Error de Base de Datos al insertar: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    if os.path.exists(DB_FILE):
        add_data()
        print("\n¡Base de datos actualizada con la placa real!")
    else:
        print("ERROR: Base de datos 'matriculas.db' no encontrada.")
        print("Ejecuta 'python src/linking_system/setup_db.py' primero.")