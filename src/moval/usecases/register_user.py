class RegisterUser:
    def execute(self,data):
        email = data.get("email")
        password = data.get("password")
        role = data.get("role", "CUSTOMER")  # Default role is CUSTOMER
        created_by = data.get("created_by")  # Who is creating the user

        # Validate email uniqueness
        if self._is_email_taken(email):
            raise ValueError("Duplicate email")
        
        # Validate password strength
        if not self._is_valid_password(password):
            raise ValueError("Invalid password")
        
        # Assign role based on who is creating the user
        if created_by == "ADMIN":
            if role not in ["ADMIN", "COURIER"]:
                raise ValueError("Admin can only create ADMIN or COURIER roles")
        else:
            role = "CUSTOMER"

        # Create user logic here (e.g., save to database)
        user = {"email": email, "password": password, "role": role}
        return user

    def _is_email_taken(self, email):
        # Placeholder for email uniqueness check
        return False # Assume email is not taken for this example

    def _is_valid_password(self, password):
        if len(password) < 8:
            return False
        has_upper = any(c.isupper() for c in password)
        has_lower = any(c.islower() for c in password)
        has_digit = any(c.isdigit() for c in password)
        return has_upper and has_lower and has_digit
    
        