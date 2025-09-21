import bcrypt

class PasswordService:
    @staticmethod
    def hash_password(plain_password: str) -> str:
        """
        Hash a plain text password using bcrypt.
        Returns the hashed password as a string for storage in DB.
        """
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(plain_password.encode("utf-8"), salt)
        return hashed.decode("utf-8")

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """
        Verify a plain text password against a hashed password.
        Returns True if match, False otherwise.
        """
        return bcrypt.checkpw(
            plain_password.encode("utf-8"), hashed_password.encode("utf-8")
        )

