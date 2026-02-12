"""
Cryptographic utilities for ZKP system.
Provides safe prime generation, random number generation, and modular arithmetic.
"""

import secrets
import hashlib
from typing import Tuple


class CryptoUtils:
    """Utility class for cryptographic operations."""
    
    # Using a safe 2048-bit prime (Sophie Germain prime)
    # p = 2q + 1 where both p and q are prime
    # This is a well-known safe prime for cryptographic use
    P = int(
        "FFFFFFFFFFFFFFFFC90FDAA22168C234C4C6628B80DC1CD1"
        "29024E088A67CC74020BBEA63B139B22514A08798E3404DD"
        "EF9519B3CD3A431B302B0A6DF25F14374FE1356D6D51C245"
        "E485B576625E7EC6F44C42E9A637ED6B0BFF5CB6F406B7ED"
        "EE386BFB5A899FA5AE9F24117C4B1FE649286651ECE45B3D"
        "C2007CB8A163BF0598DA48361C55D39A69163FA8FD24CF5F"
        "83655D23DCA3AD961C62F356208552BB9ED529077096966D"
        "670C354E4ABC9804F1746C08CA18217C32905E462E36CE3B"
        "E39E772C180E86039B2783A2EC07A28FB5C55DF06F4C52C9"
        "DE2BCBF6955817183995497CEA956AE515D2261898FA0510"
        "15728E5A8AACAA68FFFFFFFFFFFFFFFF", 16
    )
    
    # Generator g = 2
    G = 2
    
    # Order q = (p-1)/2
    Q = (P - 1) // 2
    
    @staticmethod
    def generate_random(bits: int = 256) -> int:
        """
        Generate a cryptographically secure random number.
        
        Args:
            bits: Number of bits for the random number
            
        Returns:
            Random integer
        """
        return secrets.randbits(bits)
    
    @staticmethod
    def generate_random_in_range(max_value: int) -> int:
        """
        Generate a random number in range [1, max_value-1].
        
        Args:
            max_value: Maximum value (exclusive)
            
        Returns:
            Random integer in valid range
        """
        return secrets.randbelow(max_value - 1) + 1
    
    @staticmethod
    def mod_exp(base: int, exponent: int, modulus: int) -> int:
        """
        Modular exponentiation: (base^exponent) mod modulus.
        Uses Python's built-in pow for efficiency.
        
        Args:
            base: Base value
            exponent: Exponent value
            modulus: Modulus value
            
        Returns:
            Result of modular exponentiation
        """
        return pow(base, exponent, modulus)
    
    @staticmethod
    def hash_to_int(*values) -> int:
        """
        Hash multiple values to an integer using SHA-256.
        
        Args:
            *values: Values to hash (will be converted to strings)
            
        Returns:
            Integer hash value
        """
        hasher = hashlib.sha256()
        for value in values:
            hasher.update(str(value).encode('utf-8'))
        return int.from_bytes(hasher.digest(), byteorder='big')
    
    @staticmethod
    def int_to_bytes(value: int) -> bytes:
        """Convert integer to bytes."""
        byte_length = (value.bit_length() + 7) // 8
        return value.to_bytes(byte_length, byteorder='big')
    
    @staticmethod
    def bytes_to_int(data: bytes) -> int:
        """Convert bytes to integer."""
        return int.from_bytes(data, byteorder='big')
    
    @classmethod
    def get_parameters(cls) -> Tuple[int, int, int]:
        """
        Get the cryptographic parameters (p, g, q).
        
        Returns:
            Tuple of (prime p, generator g, order q)
        """
        return cls.P, cls.G, cls.Q
