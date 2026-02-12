"""
Public key registry for verifier layer.
Stores and manages issuer-certified public keys.
"""

import sqlite3
import json
from datetime import datetime
from typing import Optional, Dict
import os


class PublicKeyRegistry:
    """Registry for storing and validating issuer-certified public keys."""
    
    def __init__(self, db_path: str = "verifier/registry.db"):
        """Initialize registry database."""
        self.db_path = db_path
        self._ensure_directory()
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self._create_tables()
    
    def _ensure_directory(self):
        """Ensure database directory exists."""
        directory = os.path.dirname(self.db_path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)
    
    def _create_tables(self):
        """Create registry tables."""
        cursor = self.conn.cursor()
        
        # Certified public keys table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS certified_keys (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id TEXT NOT NULL UNIQUE,
                public_key TEXT NOT NULL,
                credential_data TEXT NOT NULL,
                signature TEXT NOT NULL,
                issuer TEXT NOT NULL,
                registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                verified BOOLEAN DEFAULT 1
            )
        ''')
        
        # Verification sessions table (for challenge tracking)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS verification_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL UNIQUE,
                student_id TEXT,
                challenge TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP NOT NULL,
                used BOOLEAN DEFAULT 0
            )
        ''')
        
        self.conn.commit()
    
    def register_public_key(self, student_id: str, public_key: str, 
                           credential_data: str, signature: str, 
                           issuer: str = "College") -> bool:
        """
        Register a certified public key.
        
        Args:
            student_id: Student ID
            public_key: Public key
            credential_data: Credential JSON
            signature: Credential signature
            issuer: Issuing authority
            
        Returns:
            True if successful, False otherwise
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT INTO certified_keys 
                (student_id, public_key, credential_data, signature, issuer)
                VALUES (?, ?, ?, ?, ?)
            ''', (student_id, public_key, credential_data, signature, issuer))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            # Update existing entry
            cursor.execute('''
                UPDATE certified_keys 
                SET public_key = ?, credential_data = ?, signature = ?, 
                    registered_at = CURRENT_TIMESTAMP
                WHERE student_id = ?
            ''', (public_key, credential_data, signature, student_id))
            self.conn.commit()
            return True
    
    def get_public_key(self, student_id: str) -> Optional[Dict]:
        """
        Get certified public key for a student.
        
        Args:
            student_id: Student ID
            
        Returns:
            Dictionary with key data or None
        """
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT * FROM certified_keys 
            WHERE student_id = ? AND verified = 1
        ''', (student_id,))
        row = cursor.fetchone()
        return dict(row) if row else None
    
    def verify_credential(self, student_id: str, signature: str) -> bool:
        """
        Verify a credential signature.
        
        Args:
            student_id: Student ID
            signature: Signature to verify
            
        Returns:
            True if valid, False otherwise
        """
        key_data = self.get_public_key(student_id)
        if not key_data:
            return False
        return key_data['signature'] == signature
    
    def store_challenge(self, session_id: str, challenge: str, 
                       student_id: Optional[str] = None, 
                       expires_in_seconds: int = 300) -> bool:
        """
        Store a challenge for a verification session.
        
        Args:
            session_id: Unique session ID
            challenge: Challenge value
            student_id: Optional student ID
            expires_in_seconds: Expiration time in seconds
            
        Returns:
            True if successful
        """
        from datetime import timedelta
        expires_at = datetime.utcnow() + timedelta(seconds=expires_in_seconds)
        
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT INTO verification_sessions 
                (session_id, student_id, challenge, expires_at)
                VALUES (?, ?, ?, ?)
            ''', (session_id, student_id, challenge, expires_at.isoformat()))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
    
    def get_challenge(self, session_id: str) -> Optional[str]:
        """
        Get challenge for a session.
        
        Args:
            session_id: Session ID
            
        Returns:
            Challenge or None
        """
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT challenge, expires_at, used FROM verification_sessions
            WHERE session_id = ?
        ''', (session_id,))
        row = cursor.fetchone()
        
        if not row:
            return None
        
        # Check if expired
        expires_at = datetime.fromisoformat(row['expires_at'])
        if datetime.utcnow() > expires_at:
            return None
        
        # Check if already used
        if row['used']:
            return None
        
        return row['challenge']
    
    def mark_challenge_used(self, session_id: str) -> bool:
        """
        Mark a challenge as used.
        
        Args:
            session_id: Session ID
            
        Returns:
            True if successful
        """
        cursor = self.conn.cursor()
        cursor.execute('''
            UPDATE verification_sessions 
            SET used = 1 
            WHERE session_id = ?
        ''', (session_id,))
        self.conn.commit()
        return cursor.rowcount > 0
    
    def close(self):
        """Close database connection."""
        self.conn.close()
