"""
Credential management for issuer layer.
Handles credential creation, signing, and validation.
"""

import json
import hashlib
import hmac
from datetime import datetime, timedelta
from typing import Dict, Optional


class CredentialManager:
    """Manages credential issuance and validation."""
    
    def __init__(self, secret_key: str = "college_secret_key_2026"):
        """
        Initialize credential manager.
        
        Args:
            secret_key: Secret key for signing credentials
        """
        self.secret_key = secret_key.encode('utf-8')
    
    def create_credential(self, student_id: str, public_key: str, 
                         student_data: Dict) -> Dict:
        """
        Create a credential for a student.
        
        Args:
            student_id: Student ID
            public_key: Student's public key
            student_data: Additional student data
            
        Returns:
            Credential dictionary
        """
        credential = {
            'student_id': student_id,
            'public_key': public_key,
            'name': student_data.get('name'),
            'email': student_data.get('email'),
            'department': student_data.get('department'),
            'admission_year': student_data.get('admission_year'),
            'issued_at': datetime.utcnow().isoformat(),
            'expires_at': (datetime.utcnow() + timedelta(days=365)).isoformat(),
            'issuer': 'College Verification System',
            'version': '1.0'
        }
        return credential
    
    def sign_credential(self, credential: Dict) -> str:
        """
        Sign a credential using HMAC-SHA256.
        
        Args:
            credential: Credential dictionary
            
        Returns:
            Signature (hex string)
        """
        # Create canonical representation
        credential_str = json.dumps(credential, sort_keys=True)
        
        # Generate HMAC signature
        signature = hmac.new(
            self.secret_key,
            credential_str.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        return signature
    
    def verify_signature(self, credential: Dict, signature: str) -> bool:
        """
        Verify a credential signature.
        
        Args:
            credential: Credential dictionary
            signature: Signature to verify
            
        Returns:
            True if signature is valid, False otherwise
        """
        expected_signature = self.sign_credential(credential)
        return hmac.compare_digest(expected_signature, signature)
    
    def issue_credential(self, student_id: str, public_key: str, 
                        student_data: Dict) -> Dict:
        """
        Issue a complete signed credential.
        
        Args:
            student_id: Student ID
            public_key: Student's public key
            student_data: Student data
            
        Returns:
            Dictionary with credential and signature
        """
        credential = self.create_credential(student_id, public_key, student_data)
        signature = self.sign_credential(credential)
        
        return {
            'credential': credential,
            'signature': signature
        }
    
    def validate_credential(self, credential_data: str, signature: str) -> bool:
        """
        Validate a credential and its signature.
        
        Args:
            credential_data: JSON string of credential
            signature: Signature to verify
            
        Returns:
            True if valid, False otherwise
        """
        try:
            credential = json.loads(credential_data)
            
            # Verify signature
            if not self.verify_signature(credential, signature):
                return False
            
            # Check expiration
            expires_at = datetime.fromisoformat(credential['expires_at'])
            if datetime.utcnow() > expires_at:
                return False
            
            return True
            
        except (json.JSONDecodeError, KeyError, ValueError):
            return False
    
    def extract_public_key(self, credential_data: str) -> Optional[str]:
        """
        Extract public key from credential.
        
        Args:
            credential_data: JSON string of credential
            
        Returns:
            Public key or None
        """
        try:
            credential = json.loads(credential_data)
            return credential.get('public_key')
        except json.JSONDecodeError:
            return None
