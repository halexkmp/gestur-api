from passlib.context import CryptContext


class PasswordHashCreate:
    def get_password_hash(self, password):
        return CryptContext(schemes=["bcrypt"], deprecated="auto").hash(password)