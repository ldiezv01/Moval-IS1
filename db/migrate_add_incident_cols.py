import sqlite3
import os

db_path = os.path.join('db', 'moval.db')

if not os.path.exists(db_path):
    print(f"Database not found at {db_path}")
    exit(0)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    print("Attempting to add 'ultima_incidencia' column...")
    cursor.execute("ALTER TABLE Paquete ADD COLUMN ultima_incidencia TEXT")
    print("Success.")
except sqlite3.OperationalError as e:
    print(f"Skipped: {e}")

try:
    print("Attempting to add 'fecha_incidencia' column...")
    cursor.execute("ALTER TABLE Paquete ADD COLUMN fecha_incidencia DATETIME")
    print("Success.")
except sqlite3.OperationalError as e:
    print(f"Skipped: {e}")

conn.commit()
conn.close()
print("Migration complete.")
