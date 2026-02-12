"""
ZKP verification engine for verifier layer.
Handles challenge generation and proof verification.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from crypto.schnorr import SchnorrZKP
from typing import Dict, Optional
import uuid


class ZKPVerifier:
    """ZKP verification engine for scholarship backend."""
    
    def __init__(self):
        """Initialize ZKP verifier."""
        self.zkp = SchnorrZKP()
    
    def generate_challenge_session(self) -> Dict[str, str]:
        """
        Generate a new challenge session.
        
        Returns:
            Dictionary with session_id and challenge
        """
        session_id = str(uuid.uuid4())
        challenge = self.zkp.generate_challenge()
        
        return {
            'session_id': session_id,
            'challenge': str(challenge)
        }
    
    def verify_proof(self, commitment: str, response: str, 
                    challenge: str, public_key: str) -> bool:
        """
        Verify a ZKP proof.
        
        Args:
            commitment: Commitment value t
            response: Response value s
            challenge: Challenge value c
            public_key: Public key y
            
        Returns:
            True if proof is valid, False otherwise
        """
        try:
            # Convert strings to integers
            t = int(commitment)
            s = int(response)
            c = int(challenge)
            y = int(public_key)
            
            # Verify proof
            return self.zkp.verify_proof(t, s, c, y)
            
        except (ValueError, TypeError):
            return False
    
    def verify_complete_proof(self, proof: Dict, challenge: str, 
                             public_key: str) -> bool:
        """
        Verify a complete proof dictionary.
        
        Args:
            proof: Dictionary with commitment and response
                   Can be {commitment, response} or {t, s, c}
            challenge: Challenge value
            public_key: Public key
            
        Returns:
            True if valid, False otherwise
        """
        # Support both formats: {commitment, response} and {t, s, c}
        commitment = proof.get('commitment') or proof.get('t')
        response = proof.get('response') or proof.get('s')
        
        if not commitment or not response:
            return False
        
        return self.verify_proof(
            str(commitment),
            str(response),
            challenge,
            public_key
        )
    
    def verify_non_interactive_proof(self, proof: Dict, public_key: str, 
                                    message: str = "") -> bool:
        """
        Verify a non-interactive proof.
        
        Args:
            proof: Proof dictionary with commitment, response, challenge
            public_key: Public key
            message: Optional message
            
        Returns:
            True if valid, False otherwise
        """
        try:
            # Convert to integers
            proof_int = {
                'commitment': int(proof['commitment']),
                'response': int(proof['response']),
                'challenge': int(proof['challenge'])
            }
            y = int(public_key)
            
            return self.zkp.verify_non_interactive_proof(proof_int, y, message)
            
        except (ValueError, TypeError, KeyError):
            return False
