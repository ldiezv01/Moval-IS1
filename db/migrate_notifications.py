import sqlite3
import os

db_path = os.path.join('db', 'moval.db')
if not os.path.exists(db_path):
    print("DB not found")
    exit(0)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    print("Adding 'notificado_cliente' to Paquete...")
    # 0 = No visto (Unseen), 1 = Visto (Seen)
    cursor.execute("ALTER TABLE Paquete ADD COLUMN notificado_cliente INTEGER DEFAULT 0")
    print("Success.")
except Exception as e:
    print(f"Info: {e}")

conn.commit()
conn.close()
