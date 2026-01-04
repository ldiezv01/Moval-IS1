import sqlite3
import os
import sys

# Ajustar path para importar desde src
# db/init_db.py -> dirname = db -> .. = root
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.moval.security.password_hasher import PasswordHasher

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(CURRENT_DIR, "moval.db")
SQL_SCRIPT_PATH = os.path.join(CURRENT_DIR, "init.sql")

def init_db():
    # 1. Borrar DB anterior si existe para empezar limpio
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        print(f"Base de datos anterior '{DB_PATH}' eliminada.")

    # 2. Leer el script SQL
    with open(SQL_SCRIPT_PATH, "r", encoding="utf-8") as f:
        sql_script = f.read()

    # 3. Separar DDL de DML
    # El script SQL original contiene inserts con contraseñas en texto plano.
    # Se extrae solo la parte de definición de esquema (DDL) para ejecutarla.
    # Los datos se insertarán posteriormente mediante Python usando hashing seguro.
    
    split_marker = "-- Insertar datos de prueba"
    if split_marker in sql_script:
        ddl_script = sql_script.split(split_marker)[0]
    else:
        ddl_script = sql_script

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print("Creando esquema de base de datos...")
    cursor.executescript(ddl_script)

    # 4. Inserción de usuarios (Seed Data)
    # Generación de hashes seguros para contraseñas de prueba.
    print("Insertando datos semilla (Usuarios)...")
    hasher = PasswordHasher()
    password_comun = "1234"
    hash_password = hasher.hash(password_comun)

    users = [
        ('admin', 'Administrador', 'Jefe', 'admin@moval.com', hash_password, 'ADMIN'),
        ('1111A', 'Juan', 'Mensajero', 'juan@moval.com', hash_password, 'COURIER'),
        ('2222B', 'Ana', 'Cliente', 'ana@moval.com', hash_password, 'CUSTOMER')
    ]

    cursor.executemany("""
        INSERT INTO Usuario (dni, nombre, apellidos, email, password_hash, rol) 
        VALUES (?, ?, ?, ?, ?, ?)
    """, users)

    # 5. Inserción de datos operacionales de prueba (Paquetes, Jornadas)
    print("Insertando datos semilla (Operaciones)...")
    
    # Referencias estáticas basadas en orden de inserción: Admin=1, Juan=2, Ana=3
    
    packages = [
        ('PKG-001', 'Caja Libros', 5.5, 'Calle A, 1', 'Calle B, 2', 3, 'REGISTRADO'),
        ('PKG-002', 'Monitor', 2.0, 'Oficina Central', 'Casa Ana', 3, 'REGISTRADO')
    ]
    cursor.executemany("""
        INSERT INTO Paquete (codigo_seguimiento, descripcion, peso, direccion_origen, direccion_destino, id_cliente, estado, fecha_estimada_entrega) 
        VALUES (?, ?, ?, ?, ?, ?, ?, datetime('now', '+1 day'))
    """, packages)

    # Inicialización de jornada activa para pruebas de courier
    cursor.execute("""
        INSERT INTO Jornada (id_mensajero, fecha_inicio, estado) 
        VALUES (2, datetime('now', '-2 hours'), 'ACTIVA')
    """)

    conn.commit()
    conn.close()
    print(f"Base de datos '{DB_PATH}' inicializada correctamente con usuarios (Pass: {password_comun}).")

if __name__ == "__main__":
    init_db()
