-- db/init.sql

-- Limpieza inicial
DROP TABLE IF EXISTS Paquete;
DROP TABLE IF EXISTS Usuario;

-- 1. Tabla de Usuarios (Sirve para Admin, Cliente y Mensajero)
CREATE TABLE Usuario (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    dni TEXT UNIQUE NOT NULL,
    nombre TEXT NOT NULL,
    apellidos TEXT NOT NULL,
    email TEXT,
    password TEXT NOT NULL,
    telefono TEXT,
    rol TEXT NOT NULL, -- Valores: 'ADMIN', 'CLIENTE', 'MENSAJERO'
    activo BOOLEAN DEFAULT 1
);

-- 2. Tabla de Paquetes
CREATE TABLE Paquete (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    codigo_seguimiento TEXT UNIQUE NOT NULL,
    descripcion TEXT,
    peso REAL,
    direccion_origen TEXT NOT NULL,
    direccion_destino TEXT NOT NULL,
    estado TEXT DEFAULT 'REGISTRADO', -- 'REGISTRADO', 'ASIGNADO', 'EN_REPARTO', 'ENTREGADO'
    fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    -- Relaciones
    id_cliente INTEGER NOT NULL,      -- Quién envía/pide el paquete
    id_mensajero INTEGER,             -- Quién lo reparte (puede ser NULL al principio)
    
    FOREIGN KEY (id_cliente) REFERENCES Usuario(id),
    FOREIGN KEY (id_mensajero) REFERENCES Usuario(id)
);

-- Insertar datos de prueba (Seed Data)
-- Password '1234' para todos
INSERT INTO Usuario (dni, nombre, apellidos, password, rol) VALUES 
('admin', 'Administrador', 'Jefe', '1234', 'ADMIN'),
('1111A', 'Juan', 'Mensajero', '1234', 'MENSAJERO'),
('2222B', 'Ana', 'Cliente', '1234', 'CLIENTE');

INSERT INTO Paquete (codigo_seguimiento, descripcion, peso, direccion_origen, direccion_destino, id_cliente, estado) VALUES
('PKG-001', 'Caja Libros', 5.5, 'Calle A, 1', 'Calle B, 2', 3, 'REGISTRADO'),
('PKG-002', 'Monitor', 2.0, 'Oficina Central', 'Casa Ana', 3, 'REGISTRADO');