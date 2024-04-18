# utils/digital_signature.py
from Crypto.Hash import SHA256
from Crypto.Signature import pkcs1_15
from Crypto.PublicKey import RSA
import base64

class DigitalSignature:
    def __init__(self, private_key, public_key):
        self.private_key = RSA.import_key(private_key)
        self.public_key = RSA.import_key(public_key)

    def generate_signature(self, message: bytes) -> str:
        hash_obj = SHA256.new(message)
        signature = pkcs1_15.new(self.private_key).sign(hash_obj)
        return base64.b64encode(signature).decode('utf-8')

    def verify_signature(self, message: bytes, signature: str) -> bool:
        try:
            hash_obj = SHA256.new(message)
            pkcs1_15.new(self.public_key).verify(hash_obj, base64.b64decode(signature.encode('utf-8')))
            return True
        except (ValueError, TypeError):
            return False