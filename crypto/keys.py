"""
Key management for ZKP system.
Handles private/public key generation, storage, and serialization.
"""

import json
import base64
from typing import Tuple, Dict
from .utils import CryptoUtils


class KeyManager:
    """Manages cryptographic keys for students."""
    
    def __init__(self):
        self.p, self.g, self.q = CryptoUtils.get_parameters()
    
    def generate_keypair(self) -> Tuple[int, int]:
        """
        Generate a private/public key pair.
        
        Private key: x (random in range [1, q-1])
        Public key: y = g^x mod p
        
        Returns:
            Tuple of (private_key, public_key)
        """
        # Generate private key x in range [1, q-1]
        private_key = CryptoUtils.generate_random_in_range(self.q)
        
        # Compute public key y = g^x mod p
        public_key = CryptoUtils.mod_exp(self.g, private_key, self.p)
        
        return private_key, public_key
    
    def derive_public_key(self, private_key: int) -> int:
        """
        Derive public key from private key.
        
        Args:
            private_key: Private key x
            
        Returns:
            Public key y = g^x mod p
        """
        return CryptoUtils.mod_exp(self.g, private_key, self.p)
    
    def verify_keypair(self, private_key: int, public_key: int) -> bool:
        """
        Verify that a public key matches a private key.
        
        Args:
            private_key: Private key x
            public_key: Public key y
            
        Returns:
            True if y = g^x mod p, False otherwise
        """
        expected_public = self.derive_public_key(private_key)
        return expected_public == public_key
    
    @staticmethod
    def serialize_keys(private_key: int, public_key: int) -> str:
        """
        Serialize keys to JSON string.
        
        Args:
            private_key: Private key
            public_key: Public key
            
        Returns:
            JSON string containing both keys
        """
        key_data = {
            'private_key': str(private_key),
            'public_key': str(public_key)
        }
        return json.dumps(key_data)
    
    @staticmethod
    def deserialize_keys(json_str: str) -> Tuple[int, int]:
        """
        Deserialize keys from JSON string.
        
        Args:
            json_str: JSON string containing keys
            
        Returns:
            Tuple of (private_key, public_key)
        """
        key_data = json.loads(json_str)
        return int(key_data['private_key']), int(key_data['public_key'])
    
    @staticmethod
    def serialize_public_key(public_key: int) -> str:
        """
        Serialize public key to base64 string.
        
        Args:
            public_key: Public key
            
        Returns:
            Base64 encoded public key
        """
        key_bytes = CryptoUtils.int_to_bytes(public_key)
        return base64.b64encode(key_bytes).decode('utf-8')
    
    @staticmethod
    def deserialize_public_key(encoded_key: str) -> int:
        """
        Deserialize public key from base64 string.
        
        Args:
            encoded_key: Base64 encoded public key
            
        Returns:
            Public key as integer
        """
        key_bytes = base64.b64decode(encoded_key.encode('utf-8'))
        return CryptoUtils.bytes_to_int(key_bytes)
    
    def export_public_key(self, public_key: int) -> Dict[str, str]:
        """
        Export public key in a standard format.
        
        Args:
            public_key: Public key to export
            
        Returns:
            Dictionary with public key and parameters
        """
        return {
            'public_key': str(public_key),
            'p': str(self.p),
            'g': str(self.g),
            'q': str(self.q)
        }
    
    @staticmethod
    def import_public_key(key_data: Dict[str, str]) -> int:
        """
        Import public key from standard format.
        
        Args:
            key_data: Dictionary with public key data
            
        Returns:
            Public key as integer
        """
        return int(key_data['public_key'])
