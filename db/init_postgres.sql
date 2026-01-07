-- db/init_postgres.sql

-- Limpieza inicial (CASCADE permite borrar tablas aunque tengan relaciones)
DROP TABLE IF EXISTS Valoracion CASCADE;
DROP TABLE IF EXISTS Incidencia CASCADE;
DROP TABLE IF EXISTS Jornada CASCADE;
DROP TABLE IF EXISTS Paquete CASCADE;
DROP TABLE IF EXISTS Usuario CASCADE;

-- 1. Tabla de Usuarios
CREATE TABLE Usuario (
    id SERIAL PRIMARY KEY,
    dni TEXT UNIQUE NOT NULL,
    nombre TEXT NOT NULL,
    apellidos TEXT NOT NULL,
    email TEXT UNIQUE,
    password_hash TEXT NOT NULL,
    telefono TEXT,
    rol TEXT NOT NULL, -- 'ADMIN', 'CUSTOMER', 'COURIER'
    activo BOOLEAN DEFAULT TRUE,
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Tabla de Paquetes
CREATE TABLE Paquete (
    id SERIAL PRIMARY KEY,
    codigo_seguimiento TEXT UNIQUE NOT NULL,
    descripcion TEXT,
    peso REAL,
    direccion_origen TEXT NOT NULL,
    direccion_destino TEXT NOT NULL,
    latitud REAL,
    longitud REAL,
    estado TEXT DEFAULT 'REGISTRADO',
    ultima_incidencia TEXT,
    fecha_incidencia TIMESTAMP,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_estimada_entrega TIMESTAMP,
    fecha_entrega_real TIMESTAMP,
    notificado_cliente INTEGER DEFAULT 0,
    
    id_cliente INTEGER NOT NULL,
    id_mensajero INTEGER,
    
    FOREIGN KEY (id_cliente) REFERENCES Usuario(id),
    FOREIGN KEY (id_mensajero) REFERENCES Usuario(id)
);

-- 3. Tabla de Jornadas
CREATE TABLE Jornada (
    id SERIAL PRIMARY KEY,
    id_mensajero INTEGER NOT NULL,
    fecha_inicio TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_fin TIMESTAMP,
    kilometros_recorridos REAL DEFAULT 0,
    estado TEXT DEFAULT 'ACTIVA',
    
    FOREIGN KEY (id_mensajero) REFERENCES Usuario(id)
);

-- 4. Tabla de Incidencias
CREATE TABLE Incidencia (
    id SERIAL PRIMARY KEY,
    titulo TEXT NOT NULL,
    descripcion TEXT,
    fecha_reporte TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    tipo TEXT,
    
    id_usuario INTEGER NOT NULL,
    id_paquete INTEGER,
    
    FOREIGN KEY (id_usuario) REFERENCES Usuario(id),
    FOREIGN KEY (id_paquete) REFERENCES Paquete(id)
);

-- 5. Tabla de Valoraciones
CREATE TABLE Valoracion (
    id SERIAL PRIMARY KEY,
    puntuacion INTEGER CHECK(puntuacion >= 1 AND puntuacion <= 5),
    comentario TEXT,
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    id_paquete INTEGER NOT NULL,
    id_autor INTEGER NOT NULL,
    
    FOREIGN KEY (id_paquete) REFERENCES Paquete(id),
    FOREIGN KEY (id_autor) REFERENCES Usuario(id)
);
