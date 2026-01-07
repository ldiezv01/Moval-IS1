import psycopg2
import os
import sys
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import random

# Ajustar path para importar src
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.moval.security.password_hasher import PasswordHasher

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
SQL_SCRIPT_PATH = os.path.join(CURRENT_DIR, "init_postgres.sql")

# DATOS DE CONEXIÓN
DB_HOST = "localhost"
DB_NAME = "moval"
DB_USER = "postgres"
DB_PASS = "1235"
DB_PORT = "5432"

def init_db():
    print(f"--- REGENERANDO BASE DE DATOS POSTGRESQL (MOVAL) ---")
    
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASS,
            port=DB_PORT
        )
        conn.autocommit = True # Para operaciones DDL si fuera necesario, pero usaremos transacciones normales
        cursor = conn.cursor()
        print(" > Conexión exitosa a PostgreSQL.")
    except Exception as e:
        print(f"ERROR DE CONEXIÓN: {e}")
        return

    # 1. Leer y ejecutar esquema SQL (DDL)
    with open(SQL_SCRIPT_PATH, "r", encoding="utf-8") as f:
        sql_script = f.read()

    try:
        cursor.execute(sql_script)
        conn.commit()
        print(" > Esquema de tablas creado.")
    except Exception as e:
        print(f"ERROR EJECUTANDO SQL: {e}")
        conn.rollback()
        return

    # 2. Preparar Hasher (Password universal: '1234')
    hasher = PasswordHasher()
    pass_hash = hasher.hash("1234")

    # 3. GENERAR USUARIOS
    usuarios = [
        # ADMIN
        ('ADMIN01', 'Admin', 'Sistema', 'admin@moval.com', pass_hash, 'ADMIN'),
        
        # MENSAJEROS (COURIER)
        ('MENS001', 'Juan', 'Pérez', 'juan@moval.com', pass_hash, 'COURIER'),
        ('MENS002', 'Laura', 'Gómez', 'laura@moval.com', pass_hash, 'COURIER'),
        ('MENS003', 'Pedro', 'Ruiz', 'pedro@moval.com', pass_hash, 'COURIER'), 
        
        # CLIENTES (CUSTOMER)
        ('CLI001', 'Ana', 'López', 'ana@moval.com', pass_hash, 'CUSTOMER'),
        ('CLI002', 'Luis', 'Martín', 'luis@moval.com', pass_hash, 'CUSTOMER'),
        ('CLI003', 'Sofía', 'Vargas', 'sofia@moval.com', pass_hash, 'CUSTOMER'),
        ('CLI004', 'Carlos', 'Sanz', 'carlos@moval.com', pass_hash, 'CUSTOMER'),
        ('CLI005', 'Elena', 'Miro', 'elena@moval.com', pass_hash, 'CUSTOMER'),
    ]
    
    # En psycopg2 usamos %s en lugar de ?
    cursor.executemany("""
        INSERT INTO Usuario (dni, nombre, apellidos, email, password_hash, rol) 
        VALUES (%s, %s, %s, %s, %s, %s)
    """, usuarios)
    print(f" > {len(usuarios)} Usuarios insertados.")

    # Recuperar IDs para relaciones
    # Como acabamos de borrar las tablas y usar SERIAL, los IDs deberían empezar en 1.
    # Admin=1
    # Couriers: Juan=2, Laura=3, Pedro=4
    # Customers: Ana=5, Luis=6, Sofia=7, Carlos=8, Elena=9
    
    # Podríamos consultarlos para estar seguros, pero con SERIAL resetado es fiable para demo.
    couriers = [2, 3, 4]
    customers = [5, 6, 7, 8, 9]

    # 4. JORNADAS
    now = datetime.now(ZoneInfo("Europe/Madrid"))
    jornadas = [
        # Juan (ID 2) NO tiene jornada activa
        (3, now - timedelta(minutes=15), 'ACTIVA')
    ]
    cursor.executemany("INSERT INTO Jornada (id_mensajero, fecha_inicio, estado) VALUES (%s, %s, %s)", jornadas)
    print(" > Jornadas activas creadas.")

    # 5. PAQUETES DE PRUEBA
    paquetes = []
    
    def random_coords():
        lat = 42.60 + random.uniform(-0.02, 0.02)
        lon = -5.56 + random.uniform(-0.03, 0.03)
        return lat, lon

    # A) Pendientes (REGISTRADO)
    for i in range(1, 11):
        lat, lon = random_coords()
        paquetes.append((
            f'PKG-N{i:03d}', 
            f'Paquete Nuevo {i}', 
            random.uniform(1.0, 10.0), 
            'Almacén Central',
            f'Calle {random.choice(["Ordoño II", "Ancha", "Padre Isla", "Burgo Nuevo"])} {random.randint(1, 100)}',
            lat, lon, 
            random.choice(customers), 
            None, 
            'REGISTRADO',
            None
        ))

    # B) Asignados (ASIGNADO)
    for i in range(11, 16):
        lat, lon = random_coords()
        paquetes.append((
            f'PKG-A{i:03d}', 
            f'Paquete Asignado {i}', 
            random.uniform(0.5, 5.0), 
            'Almacén Central',
            f'Avenida {random.choice(["Roma", "Facultad"])} {random.randint(1, 150)}',
            lat, lon,
            random.choice(customers),
            2, # Juan
            'ASIGNADO',
            None
        ))
    
    lat_l, lon_l = random_coords()
    paquetes.append((f'PKG-A099', 'Urgente Laura', 1.2, 'Almacén', 'Calle Lancia, 2', lat_l, lon_l, 5, 3, 'ASIGNADO', None))

    # C) Entregados (ENTREGADO)
    for i in range(20, 26):
        delivery_time = now - timedelta(hours=random.randint(1, 48))
        lat, lon = random_coords()
        paquetes.append((
            f'PKG-E{i:03d}', 
            f'Libros Texto {i}', 
            3.5, 
            'Librería Central',
            f'Calle {random.choice(["Mariano Andrés", "Serranos"])} {random.randint(1, 50)}',
            lat, lon,
            5, # Ana
            2, # Juan
            'ENTREGADO',
            delivery_time
        ))

    cursor.executemany("""
        INSERT INTO Paquete (codigo_seguimiento, descripcion, peso, direccion_origen, direccion_destino, latitud, longitud, id_cliente, id_mensajero, estado, fecha_entrega_real) 
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, paquetes)
    print(f" > {len(paquetes)} Paquetes generados.")

    # 6. VALORACIONES (Ratings)
    # Recuperar IDs de paquetes entregados para asociarles valoraciones
    cursor.execute("SELECT id, id_cliente FROM Paquete WHERE estado = 'ENTREGADO'")
    paquetes_entregados = cursor.fetchall()

    valoraciones = []
    comentarios = [
        "Entrega muy rápida, gracias.",
        "Todo correcto.",
        "El mensajero fue muy amable.",
        "Llegó un poco tarde pero bien.",
        "Perfecto.",
        "Sin problemas.",
        "Bien.",
        "Ok",
        "Excelente servicio, repetiré.",
        "Normal."
    ]

    for pkg_id, client_id in paquetes_entregados:
        # 80% de probabilidad de tener valoración
        if random.random() < 0.8:
            score = random.choices([3, 4, 5], weights=[10, 40, 50])[0] # Mayormente buenas notas
            comment = random.choice(comentarios)
            # A veces sin comentario
            if random.random() < 0.2:
                comment = None
            
            valoraciones.append((score, comment, pkg_id, client_id))

    if valoraciones:
        cursor.executemany("""
            INSERT INTO Valoracion (puntuacion, comentario, id_paquete, id_autor)
            VALUES (%s, %s, %s, %s)
        """, valoraciones)
        print(f" > {len(valoraciones)} Valoraciones generadas.")

    conn.commit()
    conn.close()
    print("\n--- DB POSTGRESQL LISTA PARA DEMO ---")

if __name__ == "__main__":
    init_db()
