import hashlib
import hmac
import re
import secrets

import bcrypt

from app.models.model import Model


class User(Model):
    @staticmethod
    def find(userId):
        return User.fetch(
            "SELECT id, first_name, last_name, location, description, occupation FROM users WHERE id=%s",
            (userId,), one=True,
        )

    @staticmethod
    def byEmail(email):
        return User.fetch("SELECT * FROM users WHERE email=%s", (email,), one=True)

    @staticmethod
    def count():
        return User.fetch("SELECT COUNT(*) AS total FROM users", one=True)["total"]

    @staticmethod
    def hashPassword(password):
        salt = secrets.token_hex(16)
        passwordBytes = password.encode("utf-8")
        saltBytes = salt.encode("ascii")
        passwordHash = hashlib.pbkdf2_hmac("sha256", passwordBytes, saltBytes, 600000).hex()
        return f"pbkdf2${salt}${passwordHash}"

    @staticmethod
    def checkPassword(password, passwordHash):
        try:
            if passwordHash.startswith("pbkdf2$"):
                algorithm, salt, storedHash = passwordHash.split("$")
                passwordBytes = password.encode("utf-8")
                saltBytes = salt.encode("ascii")
                calculatedHash = hashlib.pbkdf2_hmac("sha256", passwordBytes, saltBytes, 600000).hex()
                return hmac.compare_digest(calculatedHash, storedHash)
            return bcrypt.checkpw(password.encode("utf-8"), passwordHash.encode("ascii"))
        except (ValueError, UnicodeError):
            return False

    @staticmethod
    def validate(data):
        errors = {}
        for field in ("first_name", "last_name"):
            value = data.get(field, "").strip()
            if not value or not value.isalpha() or len(value) > 50:
                errors[field] = "Use letters only, up to 50 characters."
        email = data.get("email", "").strip()
        if len(email) > 100 or not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", email):
            errors["email"] = "Enter a valid email address, up to 100 characters."
        password = data.get("password", "")
        if not password.strip():
            errors["password"] = "Enter a password."
        if password != data.get("confirm_password", ""):
            errors["confirm_password"] = "The passwords do not match."
        for field in ("location", "occupation"):
            if len(data.get(field, "").strip()) > 100:
                errors[field] = "Use no more than 100 characters."
        if len(data.get("description", "")) > 2000:
            errors["description"] = "Use no more than 2,000 characters."
        return errors

    @staticmethod
    def create(data):
        passwordHash = User.hashPassword(data["password"])
        return User.execute(
            "INSERT INTO users (first_name,last_name,email,password,location,description,occupation) "
            "VALUES (%s,%s,%s,%s,%s,%s,%s)",
            (
                data["first_name"].strip(), data["last_name"].strip(),
                data["email"].strip().lower(), passwordHash,
                data.get("location", "").strip() or None,
                data.get("description", "").strip() or None,
                data.get("occupation", "").strip() or None,
            ),
        )

