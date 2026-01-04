import sys
import os

# Configuración de PYTHONPATH local para el script de prueba
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from moval.persistence.repositories import UserRepo, SessionRepo
from moval.security.password_hasher import PasswordHasher
from moval.usecases.login import Login

def smoke_test():
    print("--- Iniciando Smoke Test ---")
    
    # 1. Inicialización de componentes
    user_repo = UserRepo("moval.db")
    # SessionRepo mockeado según implementación en repositories.py
    from src.moval.persistence.repositories import SessionRepo
    session_repo = SessionRepo()
    hasher = PasswordHasher()
    
    login_usecase = Login(user_repo, session_repo, hasher)
    
    # 2. Intento de login con usuario semilla
    test_email = "juan@moval.com"
    test_pass = "1234"
    
    print(f"Probando login para: {test_email}...")
    
    try:
        result = login_usecase.execute(test_email, test_pass)
        print("LOGIN EXITOSO")
        print(f"Resultado: {result}")
    except Exception as e:
        print(f"ERROR EN LOGIN: {str(e)}")

    # 3. Verificación de datos del usuario en BD
    user = user_repo.get_by_email(test_email)
    if user:
        print(f"Datos recuperados de BD: ID={user['id']}, Rol={user['role']}, Activo={user['is_active']}")
    else:
        print("ERROR: Usuario no encontrado en la base de datos.")

if __name__ == "__main__":
    smoke_test()
