import os
from typing import Dict, Any, Optional
from cryptography.fernet import Fernet, InvalidToken
from pydantic import SecretStr
from confidant.errors import SecretsError

from confidant.config import (
    MASTER_KEY_ENV
)



class SecretField(SecretStr):
    """
    A special SecretField that can optionally resolve its value
    from another identifier key during settings loading.

    Example:
        SecretField(identifier="API_KEY")
    """

    def __init__(self, *, identifier: Optional[str] = None, **kwargs):
        super().__init__(**kwargs)
        self.identifier = identifier


def _get_master_key(custom_key: Optional[str] = None) -> bytes:
    """
    Fetch the master encryption key from argument or environment variable.
    Raises SecretsError if missing.

    Args:
        custom_key (str): Optional key override.

    Returns:
        bytes: The encryption key in bytes.
    """
    key = custom_key or os.getenv(MASTER_KEY_ENV)
    if not key:
        raise SecretsError(f"Master key not found. Set {MASTER_KEY_ENV} environment variable.")
    return key.encode()


def encrypt_secret(plain_text: str) -> str:
    """
    Encrypt a plain text secret using the master key.

    Example:
        encrypt_secret("my-secret") -> "ENC(...)"
    """
    try:
        fernet = Fernet(_get_master_key())
        encrypted = fernet.encrypt(plain_text.encode()).decode()
        return f"ENC({encrypted})"
    except Exception as e:
        raise SecretsError(f"Encryption failed: {e}")


def decrypt_secret(cipher_text: str) -> str:
    """
    Decrypt an encrypted secret using the master key.

    Example:
        decrypt_secret("ENC(...)") -> "my-secret"
    """
    try:
        if not (cipher_text.startswith("ENC(") and cipher_text.endswith(")")):
            raise SecretsError("Invalid secret format. Expected ENC(...).")

        encrypted_part = cipher_text[4:-1]
        fernet = Fernet(_get_master_key())
        decrypted = fernet.decrypt(encrypted_part.encode()).decode()
        return decrypted
    except InvalidToken:
        raise SecretsError("Invalid token. Decryption failed. Check your master key.")
    except Exception as e:
        raise SecretsError(f"Decryption failed: {e}")


def decrypt_secret_fields(raw_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Scan and decrypt all fields in raw_data that are wrapped like ENC(...).

    Returns:
        dict: Same structure with decrypted fields.
    """
    if not raw_data:
        return {}

    decrypted_data = {}
    for key, value in raw_data.items():
        if isinstance(value, str) and value.startswith("ENC(") and value.endswith(")"):
            try:
                decrypted_data[key] = decrypt_secret(value)
            except SecretsError as e:
                raise SecretsError(f"Failed decrypting field '{key}': {e}")
        else:
            decrypted_data[key] = value
    return decrypted_data


def resolve_secret_identifiers(raw_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Scan and resolve all SecretFields that have an identifier set.
    If identifier exists in raw_data, replace field with actual value.
    """
    if not raw_data:
        return {}

    resolved_data = {}
    for key, value in raw_data.items():
        if isinstance(value, SecretField) and value.identifier:
            identifier = value.identifier
            if identifier not in raw_data:
                raise SecretsError(f"Identifier '{identifier}' not found in loaded data for field '{key}'.")
            resolved_data[key] = raw_data[identifier]
        else:
            resolved_data[key] = value

    return resolved_data
