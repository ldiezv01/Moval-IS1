# Moval Logistics System

Aplicación de escritorio para la gestión logística integral, diseñada para administrar envíos, rutas de reparto y seguimiento de entregas en tiempo real.

## Requisitos Previos

- Python 3.9 o superior.
- Pip (gestor de paquetes de Python).
- **PostgreSQL** instalado y en ejecución.

## Instalación

1. **Clonar o descargar el repositorio** en su equipo local.
2. **Instalar dependencias**:
   Ejecute el siguiente comando en la raíz del proyecto para instalar las librerías necesarias:
   pip install -r requirements.txt

## Configuración de la Base de Datos (PostgreSQL)

1. Cree una base de datos vacía en PostgreSQL llamada `moval`.
2. Verifique las credenciales de conexión en `db/init_db_postgres.py` y `src/moval/persistence/repositories.py` (Host: `localhost`, Port: `5432`, User: `postgres`, Pass: `1235`).
3. **Inicialización de la Base de Datos (Demo)**:
   Ejecute el siguiente comando para crear las tablas e insertar los datos de prueba:
   python db/init_db_postgres.py

## Ejecución

Para iniciar la aplicación, ejecute el archivo principal desde la raíz del proyecto:
python src/moval/app/main.py


## Credenciales de Prueba

Puede utilizar las siguientes cuentas para probar los diferentes roles del sistema (la contraseña es `1234` para todos):

| Rol | Email | Contraseña | Descripción |
| :--- | :--- | :--- | :--- |
| **Administrador** | `admin@moval.com` | `1234` | Gestión total de usuarios y envíos. |
| **Mensajero** | `juan@moval.com` | `1234` | Gestión de rutas y entregas activas. |
| **Cliente** | `ana@moval.com` | `1234` | Seguimiento de envíos y valoraciones. |

---
Para más información sobre la arquitectura y el uso de agentes de IA, consulte [AGENTS.md](./AGENTS.md).

