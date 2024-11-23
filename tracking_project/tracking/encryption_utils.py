# encryption_utils.py
from cryptography.fernet import Fernet
from django.conf import settings

# Create a Fernet instance using the key from settings
fernet = Fernet(settings.SECRET_ENCRYPTION_KEY)

def encrypt(data):
    """Encrypts the provided data"""
    return fernet.encrypt(data.encode()).decode()

def decrypt(encrypted_data):
    """Decrypts the provided encrypted data"""
    return fernet.decrypt(encrypted_data.encode()).decode()

def encrypt_id(data):
    """Encrypts the provided data (alternative function)"""
    return encrypt(data)
