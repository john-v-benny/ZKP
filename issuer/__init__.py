"""
Issuer layer module for college backend.
Handles student identity verification and credential issuance.
"""

from .app import create_app
from .database import Database
from .credentials import CredentialManager

__all__ = ['create_app', 'Database', 'CredentialManager']
