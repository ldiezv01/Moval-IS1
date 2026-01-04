import sqlite3
import os
import sys
from datetime import datetime, timedelta
import random

# Ajustar path para importar src
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.moval.security.password_hasher import PasswordHasher

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(CURRENT_DIR, "moval.db")
SQL_SCRIPT_PATH = os.path.join(CURRENT_DIR, "init.sql")

def init_db():
    print(f"--- REGENERANDO BASE DE DATOS DE DEMOSTRACIÓN ---")
    
    # 1. Borrar DB anterior
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        print(" > Base de datos anterior eliminada.")

    # 2. Leer esquema SQL (Solo DDL)
    with open(SQL_SCRIPT_PATH, "r", encoding="utf-8") as f:
        sql_script = f.read()

    # Cortamos antes de los inserts de prueba originales para meter los nuestros
    split_marker = "-- Insertar datos de prueba"
    if split_marker in sql_script:
        ddl_script = sql_script.split(split_marker)[0]
    else:
        ddl_script = sql_script

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.executescript(ddl_script)
    print(" > Esquema de tablas creado.")

    # 3. Preparar Hasher (Password universal: '1234')
    hasher = PasswordHasher()
    pass_hash = hasher.hash("1234")

    # 4. GENERAR USUARIOS
    # (dni, nombre, apellidos, email, password_hash, rol)
    usuarios = [
        # ADMIN
        ('ADMIN01', 'Admin', 'Sistema', 'admin@moval.com', pass_hash, 'ADMIN'),
        
        # MENSAJEROS (COURIER)
        ('MENS001', 'Juan', 'Pérez', 'juan@moval.com', pass_hash, 'COURIER'),
        ('MENS002', 'Laura', 'Gómez', 'laura@moval.com', pass_hash, 'COURIER'),
        ('MENS003', 'Pedro', 'Ruiz', 'pedro@moval.com', pass_hash, 'COURIER'), # Este no trabajará hoy
        
        # CLIENTES (CUSTOMER)
        ('CLI001', 'Ana', 'López', 'ana@moval.com', pass_hash, 'CUSTOMER'),
        ('CLI002', 'Luis', 'Martín', 'luis@moval.com', pass_hash, 'CUSTOMER'),
        ('CLI003', 'Sofía', 'Vargas', 'sofia@moval.com', pass_hash, 'CUSTOMER'),
        ('CLI004', 'Carlos', 'Sanz', 'carlos@moval.com', pass_hash, 'CUSTOMER'),
        ('CLI005', 'Elena', 'Miro', 'elena@moval.com', pass_hash, 'CUSTOMER'),
    ]
    
    cursor.executemany("""
        INSERT INTO Usuario (dni, nombre, apellidos, email, password_hash, rol) 
        VALUES (?, ?, ?, ?, ?, ?)
    """, usuarios)
    print(f" > {len(usuarios)} Usuarios insertados (Pass: 1234).")

    # Recuperar IDs para relaciones
    # Admin=1
    # Couriers: Juan=2, Laura=3, Pedro=4
    # Customers: Ana=5, Luis=6, Sofia=7, Carlos=8, Elena=9
    couriers = [2, 3, 4]
    customers = [5, 6, 7, 8, 9]

    # 5. JORNADAS (Juan y Laura trabajan hoy)
    # Juan lleva 2 horas, Laura acaba de entrar. Pedro no trabaja.
    now = datetime.now()
    jornadas = [
        (2, now - timedelta(hours=2), 'ACTIVA'),
        (3, now - timedelta(minutes=15), 'ACTIVA')
    ]
    cursor.executemany("INSERT INTO Jornada (id_mensajero, fecha_inicio, estado) VALUES (?, ?, ?)", jornadas)
    print(" > Jornadas activas creadas para Juan y Laura.")

    # 6. PAQUETES DE PRUEBA
    paquetes = []
    
    # Helper para coordenadas en León (aprox 42.60, -5.56)
    def random_coords():
        # Variación pequeña para que caigan en la ciudad
        lat = 42.60 + random.uniform(-0.02, 0.02)
        lon = -5.56 + random.uniform(-0.03, 0.03)
        return lat, lon

    # A) Pendientes (REGISTRADO) - Para que el Admin asigne
    for i in range(1, 11):
        lat, lon = random_coords()
        paquetes.append((
            f'PKG-N{i:03d}', 
            f'Paquete Nuevo {i}', 
            random.uniform(1.0, 10.0), 
            'Almacén Central',
            f'Calle {random.choice(["Ordoño II", "Ancha", "Padre Isla", "Burgo Nuevo", "República Argentina", "Gran Vía de San Marcos"])}, {random.randint(1, 100)}',
            lat, lon, # Coordenadas
            random.choice(customers), # Cliente aleatorio
            None, # Sin mensajero
            'REGISTRADO',
            None
        ))

    # B) Asignados (ASIGNADO) - Para que Juan/Laura entreguen
    for i in range(11, 16):
        lat, lon = random_coords()
        paquetes.append((
            f'PKG-A{i:03d}', 
            f'Paquete Asignado {i}', 
            random.uniform(0.5, 5.0), 
            'Almacén Central',
            f'Avenida {random.choice(["Roma", "Facultad de Veterinaria", "Independencia", "Reyes Leoneses"])}, {random.randint(1, 150)}',
            lat, lon,
            random.choice(customers),
            2, # Asignado a Juan (ID 2)
            'ASIGNADO',
            None
        ))
    # Uno para Laura
    lat_l, lon_l = random_coords()
    paquetes.append((f'PKG-A099', 'Urgente Laura', 1.2, 'Almacén', 'Calle Lancia, 2', lat_l, lon_l, 5, 3, 'ASIGNADO', None))

    # C) Entregados (ENTREGADO) - Para que los clientes valoren
    for i in range(20, 26):
        delivery_time = now - timedelta(hours=random.randint(1, 48))
        lat, lon = random_coords()
        paquetes.append((
            f'PKG-E{i:03d}', 
            f'Libros Texto {i}', 
            3.5, 
            'Librería Central',
            f'Calle {random.choice(["Mariano Andrés", "Serranos", "Damasco"])}, {random.randint(1, 50)}',
            lat, lon,
            5, # Todos para ANA (ID 5) para probar fácil su panel
            2, # Entregado por Juan
            'ENTREGADO',
            delivery_time
        ))

    cursor.executemany("""
        INSERT INTO Paquete (codigo_seguimiento, descripcion, peso, direccion_origen, direccion_destino, latitud, longitud, id_cliente, id_mensajero, estado, fecha_entrega_real) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, paquetes)
    print(f" > {len(paquetes)} Paquetes generados (Pendientes, Asignados y Entregados).")

    conn.commit()
    conn.close()
    print("\n--- DB LISTA PARA DEMO ---")
    print("Credenciales Utiles:")
    print(" [ADMIN]    admin@moval.com  / 1234")
    print(" [COURIER]  juan@moval.com   / 1234  (Tiene paquetes asignados)")
    print(" [CUSTOMER] ana@moval.com    / 1234  (Tiene paquetes entregados para valorar)")

if __name__ == "__main__":
    init_db()