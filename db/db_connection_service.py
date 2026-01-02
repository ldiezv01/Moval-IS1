import sqlite3
from contextlib import contextmanager
import os

# La base de datos estará en la carpeta 'db' al nivel de 'src'
DB_PATH = os.path.join(os.path.dirname(__file__), '../../db/db.sqlite')

@contextmanager
def db_connection_service():
    connection = None
    try:
        # Crea la carpeta db si no existe
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
        
        connection = sqlite3.connect(DB_PATH)
        connection.row_factory = sqlite3.Row # Importante para acceder por nombre de columna
        yield DBConnection(connection)

    except sqlite3.Error as e:
        print(f"Error connecting to database: {e}")
        raise e

    finally:
        if connection:
            connection.close()

class DBConnection:
    def __init__(self, connection: sqlite3.Connection):
        self.connection = connection

    def query(self, query: str, args: tuple = ()) -> list[sqlite3.Row]:
        cursor = self.connection.cursor()
        cursor.execute(query, args)
        response = cursor.fetchall()
        self.connection.commit()
        return response

    def execute(self, query: str, args: tuple = ()) -> int:
        cursor = self.connection.cursor()
        cursor.execute(query, args)
        self.connection.commit()
        return cursor.lastrowid