
import os
import json
import base64

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding


def generate_keys():
    if os.path.exists("private_key.pem") and os.path.exists("public_key.pem"):
        return

    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048
    )

    with open("private_key.pem", "wb") as f:
        f.write(private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        ))

    with open("public_key.pem", "wb") as f:
        f.write(private_key.public_key().public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ))


def load_peer_public_key(source):
    if isinstance(source, str) and os.path.isfile(source):
        with open(source, "rb") as f:
            source = f.read()

    return serialization.load_pem_public_key(source)


def encrypt_message(message, peer_public_key):
    key = Fernet.generate_key()
    encrypted_message = Fernet(key).encrypt(message.encode("utf-8"))

    encrypted_key = peer_public_key.encrypt(
        key,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

    payload = {
        "key": base64.b64encode(encrypted_key).decode("ascii"),
        "message": encrypted_message.decode("ascii")
    }

    return json.dumps(payload).encode("utf-8")


def decrypt_message(encrypted_data, private_key):
    if isinstance(encrypted_data, bytes):
        encrypted_data = encrypted_data.decode("utf-8")

    payload = json.loads(encrypted_data)

    encrypted_key = base64.b64decode(payload["key"])
    key = private_key.decrypt(
        encrypted_key,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

    return Fernet(key).decrypt(
        payload["message"].encode("ascii")
    ).decode("utf-8")
