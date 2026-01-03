from moval.usecases.errors import ValidationError, PermissionError
from moval.domain.enums import Role

class Login:
    def __init__(self, user_repo, session_repo, password_hasher):
        self.user_repo = user_repo
        self.session_repo = session_repo
        self.password_hasher = password_hasher

    def execute(self, email: str, password: str):
        # Validate email and password
        if not email or not password:
            raise ValidationError("Email and password are required")

        user = self._authenticate_user(email, password)
        if not user:
            raise ValidationError("Invalid credentials")

        if user.get("is_blocked"):
            raise PermissionError("User is blocked")

        token = self.session_repo.create_session(user["id"])

        return {
            "user_id": user["id"],
            "role": user["role"],
            "token": token
        }

    def _authenticate_user(self, email, password):
        user = self.user_repo.get_by_email(email)
        if not user:
            return None

        if not self.password_hasher.verify(password, user["password_hash"]):
            return None

        return user 
    
