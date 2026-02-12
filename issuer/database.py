"""
Database management for issuer (college) layer.
Stores student records, credentials, and key bindings.
"""

import sqlite3
import json
from datetime import datetime
from typing import Optional, Dict, List
import os


class Database:
    """Database manager for college student records and credentials."""
    
    def __init__(self, db_path: str = "issuer/college.db"):
        """Initialize database connection."""
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
        """Create database tables if they don't exist."""
        cursor = self.conn.cursor()
        
        # Students table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS students (
                student_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT NOT NULL,
                admission_year INTEGER NOT NULL,
                department TEXT NOT NULL,
                status TEXT DEFAULT 'active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Key bindings table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS key_bindings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id TEXT NOT NULL,
                public_key TEXT NOT NULL,
                bound_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (student_id) REFERENCES students(student_id),
                UNIQUE(student_id, public_key)
            )
        ''')
        
        # Credentials table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS credentials (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id TEXT NOT NULL,
                public_key TEXT NOT NULL,
                credential_data TEXT NOT NULL,
                signature TEXT NOT NULL,
                issued_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP,
                status TEXT DEFAULT 'active',
                FOREIGN KEY (student_id) REFERENCES students(student_id)
            )
        ''')
        
        self.conn.commit()
    
    def add_student(self, student_id: str, name: str, email: str, 
                   admission_year: int, department: str) -> bool:
        """
        Add a new student to the database.
        
        Args:
            student_id: Unique student ID
            name: Student name
            email: Student email
            admission_year: Year of admission
            department: Department name
            
        Returns:
            True if successful, False otherwise
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT INTO students (student_id, name, email, admission_year, department)
                VALUES (?, ?, ?, ?, ?)
            ''', (student_id, name, email, admission_year, department))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
    
    def get_student(self, student_id: str) -> Optional[Dict]:
        """
        Get student information.
        
        Args:
            student_id: Student ID
            
        Returns:
            Dictionary with student data or None
        """
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM students WHERE student_id = ?', (student_id,))
        row = cursor.fetchone()
        return dict(row) if row else None
    
    def verify_student_identity(self, student_id: str, name: str) -> bool:
        """
        Verify student identity.
        
        Args:
            student_id: Student ID
            name: Student name
            
        Returns:
            True if identity matches, False otherwise
        """
        student = self.get_student(student_id)
        if not student:
            return False
        return student['name'].lower() == name.lower() and student['status'] == 'active'
    
    def bind_public_key(self, student_id: str, public_key: str) -> bool:
        """
        Bind a public key to a student ID.
        
        Args:
            student_id: Student ID
            public_key: Public key to bind
            
        Returns:
            True if successful, False otherwise
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT INTO key_bindings (student_id, public_key)
                VALUES (?, ?)
            ''', (student_id, public_key))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
    
    def get_public_key(self, student_id: str) -> Optional[str]:
        """
        Get the public key bound to a student.
        
        Args:
            student_id: Student ID
            
        Returns:
            Public key or None
        """
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT public_key FROM key_bindings 
            WHERE student_id = ? 
            ORDER BY bound_at DESC 
            LIMIT 1
        ''', (student_id,))
        row = cursor.fetchone()
        return row['public_key'] if row else None
    
    def store_credential(self, student_id: str, public_key: str, 
                        credential_data: str, signature: str) -> int:
        """
        Store an issued credential.
        
        Args:
            student_id: Student ID
            public_key: Public key
            credential_data: Credential data (JSON)
            signature: Digital signature
            
        Returns:
            Credential ID
        """
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO credentials (student_id, public_key, credential_data, signature)
            VALUES (?, ?, ?, ?)
        ''', (student_id, public_key, credential_data, signature))
        self.conn.commit()
        return cursor.lastrowid
    
    def get_credential(self, student_id: str) -> Optional[Dict]:
        """
        Get the most recent active credential for a student.
        
        Args:
            student_id: Student ID
            
        Returns:
            Dictionary with credential data or None
        """
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT * FROM credentials 
            WHERE student_id = ? AND status = 'active'
            ORDER BY issued_at DESC 
            LIMIT 1
        ''', (student_id,))
        row = cursor.fetchone()
        return dict(row) if row else None
    
    def get_all_students(self) -> List[Dict]:
        """Get all students."""
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM students ORDER BY student_id')
        return [dict(row) for row in cursor.fetchall()]
    
    def close(self):
        """Close database connection."""
        self.conn.close()
