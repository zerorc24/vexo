import os
import base64

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from decouple import config


# Load AES-256 key from .env
SECRET_KEY = bytes.fromhex(
    config("AES_SECRET_KEY")
)


def encrypt_message(message):
    """
    Encrypt plain text message
    """

    aesgcm = AESGCM(SECRET_KEY)

    # Random nonce for every message
    nonce = os.urandom(12)

    encrypted_data = aesgcm.encrypt(
        nonce,
        message.encode(),
        None
    )

    # Store nonce + encrypted text together
    encrypted_message = base64.b64encode(
        nonce + encrypted_data
    ).decode()

    return encrypted_message


def decrypt_message(encrypted_message):
    """
    Decrypt encrypted message
    """

    aesgcm = AESGCM(SECRET_KEY)

    # Convert back from base64
    data = base64.b64decode(
        encrypted_message.encode()
    )

    # First 12 bytes = nonce
    nonce = data[:12]

    # Remaining bytes = ciphertext
    ciphertext = data[12:]

    decrypted_data = aesgcm.decrypt(
        nonce,
        ciphertext,
        None
    )

    return decrypted_data.decode()