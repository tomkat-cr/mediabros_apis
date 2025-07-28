
"""
Password Encryption module
"""
from werkzeug.security import generate_password_hash, check_password_hash


def verify_password(plain_password, hashed_password):
    """
    Verifies a password by comparing the encrypted form of
    the form_auth_password with the db_user_password.
    :param hashed_password: The encrypted password stored in the database.
    :param plain_password: The password entered by the user.
    :return: True if the passwords match, False otherwise.
    """
    return check_password_hash(
        hashed_password,
        plain_password
    )


def get_password_hash(password):
    """
    Encrypts a password using the 'scrypt' method.
    :param password: The password to encrypt.
    :return: The encrypted password.
    """
    return generate_password_hash(
        password,
        method='scrypt',
    )


"""
PREVIOUSLY:
DeprecationWarning: 'crypt' is deprecated and slated for removal in Python 3.13

from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)
"""
