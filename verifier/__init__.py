"""
Verifier layer module for scholarship backend.
Handles ZKP verification and eligibility decisions.
"""

from .app import create_app
from .registry import PublicKeyRegistry
from .verification import ZKPVerifier
from .eligibility import EligibilityEngine

__all__ = ['create_app', 'PublicKeyRegistry', 'ZKPVerifier', 'EligibilityEngine']
