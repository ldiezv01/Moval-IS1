-- db/init.sql

-- Limpieza inicial (Orden inverso para respetar Foreign Keys)
DROP TABLE IF EXISTS Valoracion;
DROP TABLE IF EXISTS Incidencia;
DROP TABLE IF EXISTS Jornada;
DROP TABLE IF EXISTS Paquete;
DROP TABLE IF EXISTS Usuario;

-- 1. Tabla de Usuarios (Sirve para Admin, Cliente y Mensajero)
CREATE TABLE Usuario (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    dni TEXT UNIQUE NOT NULL,
    nombre TEXT NOT NULL,
    apellidos TEXT NOT NULL,
    email TEXT UNIQUE,
    password TEXT NOT NULL,
    telefono TEXT,
    rol TEXT NOT NULL, -- Valores: 'ADMIN', 'CLIENTE', 'MENSAJERO'
    activo BOOLEAN DEFAULT 1,
    fecha_registro DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 2. Tabla de Paquetes
CREATE TABLE Paquete (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    codigo_seguimiento TEXT UNIQUE NOT NULL,
    descripcion TEXT,
    peso REAL,
    direccion_origen TEXT NOT NULL,
    direccion_destino TEXT NOT NULL,
    estado TEXT DEFAULT 'REGISTRADO', -- 'REGISTRADO', 'ASIGNADO', 'EN_REPARTO', 'ENTREGADO', 'DEVUELTO', 'INCIDENCIA'
    fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
    fecha_estimada_entrega DATETIME,
    fecha_entrega_real DATETIME,
    
    -- Relaciones
    id_cliente INTEGER NOT NULL,      -- Quién envía/pide el paquete
    id_mensajero INTEGER,             -- Quién lo reparte (puede ser NULL al principio)
    
    FOREIGN KEY (id_cliente) REFERENCES Usuario(id),
    FOREIGN KEY (id_mensajero) REFERENCES Usuario(id)
);

-- 3. Tabla de Jornadas (Workdays)
-- Registra cuando un mensajero empieza y termina su turno
CREATE TABLE Jornada (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    id_mensajero INTEGER NOT NULL,
    fecha_inicio DATETIME DEFAULT CURRENT_TIMESTAMP,
    fecha_fin DATETIME,
    kilometros_recorridos REAL DEFAULT 0,
    estado TEXT DEFAULT 'ACTIVA', -- 'ACTIVA', 'FINALIZADA'
    
    FOREIGN KEY (id_mensajero) REFERENCES Usuario(id)
);

-- 4. Tabla de Incidencias
-- Problemas reportados durante el reparto o con un paquete
CREATE TABLE Incidencia (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    titulo TEXT NOT NULL,
    descripcion TEXT,
    fecha_reporte DATETIME DEFAULT CURRENT_TIMESTAMP,
    tipo TEXT, -- 'PAQUETE_DAÑADO', 'AUSENCIA', 'VEHICULO', 'OTRO'
    
    -- Relaciones
    id_usuario INTEGER NOT NULL, -- Quien reporta la incidencia
    id_paquete INTEGER,          -- Opcional: si la incidencia es sobre un paquete específico
    
    FOREIGN KEY (id_usuario) REFERENCES Usuario(id),
    FOREIGN KEY (id_paquete) REFERENCES Paquete(id)
);

-- 5. Tabla de Valoraciones
-- Feedback del servicio
CREATE TABLE Valoracion (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    puntuacion INTEGER CHECK(puntuacion >= 1 AND puntuacion <= 5),
    comentario TEXT,
    fecha DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    -- Relaciones
    id_paquete INTEGER NOT NULL,
    id_autor INTEGER NOT NULL, -- Quién escribe la valoración (normalmente el cliente)
    
    FOREIGN KEY (id_paquete) REFERENCES Paquete(id),
    FOREIGN KEY (id_autor) REFERENCES Usuario(id)
);

-- Insertar datos de prueba (Seed Data)
-- Password '1234' para todos
INSERT INTO Usuario (dni, nombre, apellidos, email, password, rol) VALUES 
('admin', 'Administrador', 'Jefe', 'admin@moval.com', '1234', 'ADMIN'),
('1111A', 'Juan', 'Mensajero', 'juan@moval.com', '1234', 'MENSAJERO'),
('2222B', 'Ana', 'Cliente', 'ana@moval.com', '1234', 'CLIENTE');

INSERT INTO Paquete (codigo_seguimiento, descripcion, peso, direccion_origen, direccion_destino, id_cliente, estado, fecha_estimada_entrega) VALUES
('PKG-001', 'Caja Libros', 5.5, 'Calle A, 1', 'Calle B, 2', 3, 'REGISTRADO', DATETIME('now', '+1 day')),
('PKG-002', 'Monitor', 2.0, 'Oficina Central', 'Casa Ana', 3, 'REGISTRADO', DATETIME('now', '+2 days'));

-- Ejemplo de una jornada activa para Juan
INSERT INTO Jornada (id_mensajero, fecha_inicio, estado) VALUES
(2, DATETIME('now', '-2 hours'), 'ACTIVA');
