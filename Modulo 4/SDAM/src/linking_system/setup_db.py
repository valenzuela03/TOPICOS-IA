import sqlite3
import os
import uuid

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))

DB_FILE_NAME = "matriculas.db"
DB_FILE = os.path.join(PROJECT_ROOT, "db", DB_FILE_NAME)

def get_db_path():
    return DB_FILE

def setup_database(db_path):
    """Crea las tablas de la base de datos y añade datos de prueba."""
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        print(f"Conexión a la base de datos '{db_path}' establecida.")
    except sqlite3.Error as e:
        print(f"Error al conectar a SQLite: {e}")
        return

    sql_create_owners_table = """
    CREATE TABLE IF NOT EXISTS Propietarios (
        owner_id TEXT PRIMARY KEY,
        nombre TEXT NOT NULL,
        datos_contacto TEXT,
        direccion TEXT
    );
    """

    sql_create_vehicles_table = """
    CREATE TABLE IF NOT EXISTS Vehiculos (
        placa_numero TEXT PRIMARY KEY,
        marca TEXT NOT NULL,
        modelo TEXT,
        anio INTEGER,
        owner_id TEXT NOT NULL,
        FOREIGN KEY (owner_id) REFERENCES Propietarios (owner_id)
            ON DELETE CASCADE ON UPDATE CASCADE
    );
    """

    try:
        cursor.execute(sql_create_owners_table)
        cursor.execute(sql_create_vehicles_table)
        conn.commit()
        print("Tablas 'Propietarios' y 'Vehiculos' creadas con éxito.")
    except sqlite3.Error as e:
        print(f"Error al crear tablas: {e}")
        conn.close()
        return
    
    owner_id_cesar = str(uuid.uuid4())
    owner_id_elena = str(uuid.uuid4())
    
    owners_data = [
        (owner_id_cesar, 'César Augusto Hernández', 'Tel: +52 667 123 4567', 'Av. Tecnológico #123'),
        (owner_id_elena, 'Elena Patricia Soto', 'Tel: +52 667 987 6543', 'Calle Central #456'),
    ]

    vehicles_data = [
        # Placas sin guiones para la DB
        ('ABC123', 'Nissan', 'Versa', 2020, owner_id_cesar), 
        ('XYZ789', 'Ford', 'Focus', 2018, owner_id_elena),
        ('PQR456', 'Toyota', 'Corolla', 2022, owner_id_cesar),
    ]

    try:
        cursor.execute("DELETE FROM Vehiculos")
        cursor.execute("DELETE FROM Propietarios")
        
        cursor.executemany("INSERT INTO Propietarios VALUES (?, ?, ?, ?)", owners_data)
        cursor.executemany("INSERT INTO Vehiculos VALUES (?, ?, ?, ?, ?)", vehicles_data)
        
        conn.commit()
        print("Datos de prueba insertados con éxito.")
    except sqlite3.Error as e:
        print(f"Error al insertar datos de prueba: {e}")
        conn.close()
        return

    conn.close()

if __name__ == "__main__":

    db_dir = os.path.join(PROJECT_ROOT, 'db')
    os.makedirs(db_dir, exist_ok=True)
    
    db_path = get_db_path()
    setup_database(db_path)
    print("\nLa base de datos SQLite está lista y poblada")