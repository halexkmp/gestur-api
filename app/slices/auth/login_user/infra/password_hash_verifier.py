from passlib.context import CryptContext
class PasswordVerifyHash:
    def verify_hash_password(self, password, password_hash):
        return CryptContext(schemes=["bcrypt"], deprecated="auto").verify(password, password_hash)