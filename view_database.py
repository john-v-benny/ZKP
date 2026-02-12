"""
View database contents for ZKP system.
Shows what data is stored in issuer and verifier databases.
"""

import sys
import os
import json
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from issuer.database import Database as IssuerDB
from verifier.registry import PublicKeyRegistry


def view_issuer_database():
    """View issuer (college) database contents."""
    print("=" * 80)
    print("ISSUER DATABASE (College)")
    print("=" * 80)
    
    db = IssuerDB()
    
    # View students
    print("\n📚 STUDENTS TABLE:")
    print("-" * 80)
    students = db.get_all_students()
    
    if students:
        for student in students:
            print(f"\nStudent ID: {student['student_id']}")
            print(f"  Name: {student['name']}")
            print(f"  Email: {student['email']}")
            print(f"  Department: {student['department']}")
            print(f"  Admission Year: {student['admission_year']}")
            print(f"  Status: {student['status']}")
            print(f"  Created: {student['created_at']}")
    else:
        print("No students found")
    
    # View key bindings
    print("\n\n🔑 KEY BINDINGS TABLE:")
    print("-" * 80)
    cursor = db.conn.cursor()
    cursor.execute('SELECT * FROM key_bindings ORDER BY bound_at DESC')
    bindings = cursor.fetchall()
    
    if bindings:
        for binding in bindings:
            print(f"\nBinding ID: {binding['id']}")
            print(f"  Student ID: {binding['student_id']}")
            print(f"  Public Key: {binding['public_key'][:50]}...")
            print(f"  Bound At: {binding['bound_at']}")
    else:
        print("No key bindings found")
    
    # View credentials
    print("\n\n📜 CREDENTIALS TABLE:")
    print("-" * 80)
    cursor.execute('SELECT * FROM credentials ORDER BY issued_at DESC')
    credentials = cursor.fetchall()
    
    if credentials:
        for cred in credentials:
            print(f"\nCredential ID: {cred['id']}")
            print(f"  Student ID: {cred['student_id']}")
            print(f"  Public Key: {cred['public_key'][:50]}...")
            print(f"  Status: {cred['status']}")
            print(f"  Issued At: {cred['issued_at']}")
            
            # Parse credential data
            cred_data = json.loads(cred['credential_data'])
            print(f"  Credential Details:")
            print(f"    - Name: {cred_data.get('name')}")
            print(f"    - Department: {cred_data.get('department')}")
            print(f"    - Admission Year: {cred_data.get('admission_year')}")
            print(f"    - Expires: {cred_data.get('expires_at')}")
    else:
        print("No credentials issued yet")
    
    db.close()


def view_verifier_database():
    """View verifier (scholarship) database contents."""
    print("\n\n" + "=" * 80)
    print("VERIFIER DATABASE (Scholarship Backend)")
    print("=" * 80)
    
    registry = PublicKeyRegistry()
    
    # View certified keys
    print("\n🔐 CERTIFIED PUBLIC KEYS REGISTRY:")
    print("-" * 80)
    cursor = registry.conn.cursor()
    cursor.execute('SELECT * FROM certified_keys ORDER BY registered_at DESC')
    keys = cursor.fetchall()
    
    if keys:
        for key in keys:
            print(f"\nRegistry ID: {key['id']}")
            print(f"  Student ID: {key['student_id']}")
            print(f"  Public Key: {key['public_key'][:50]}...")
            print(f"  Issuer: {key['issuer']}")
            print(f"  Verified: {'Yes' if key['verified'] else 'No'}")
            print(f"  Registered At: {key['registered_at']}")
            
            # Parse credential
            cred_data = json.loads(key['credential_data'])
            print(f"  Student Info (from credential):")
            print(f"    - Name: {cred_data.get('name')}")
            print(f"    - Department: {cred_data.get('department')}")
    else:
        print("No certified keys registered yet")
    
    # View verification sessions
    print("\n\n🎯 VERIFICATION SESSIONS:")
    print("-" * 80)
    cursor.execute('SELECT * FROM verification_sessions ORDER BY created_at DESC LIMIT 10')
    sessions = cursor.fetchall()
    
    if sessions:
        for session in sessions:
            print(f"\nSession ID: {session['session_id']}")
            print(f"  Student ID: {session['student_id'] or 'N/A'}")
            print(f"  Challenge: {session['challenge'][:30]}...")
            print(f"  Created: {session['created_at']}")
            print(f"  Expires: {session['expires_at']}")
            print(f"  Used: {'Yes' if session['used'] else 'No'}")
    else:
        print("No verification sessions yet")
    
    registry.close()


def main():
    """Main function to view all databases."""
    print("\n" + "🔍 ZKP SYSTEM DATABASE VIEWER" + "\n")
    
    view_issuer_database()
    view_verifier_database()
    
    print("\n" + "=" * 80)
    print("Database view complete!")
    print("=" * 80 + "\n")


if __name__ == '__main__':
    main()
