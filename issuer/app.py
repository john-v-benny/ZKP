"""
Flask application for issuer (college) layer.
Provides APIs for student identity verification and credential issuance.
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from issuer.database import Database
from issuer.credentials import CredentialManager


def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__)
    CORS(app)  # Enable CORS for all routes
    
    # Initialize database and credential manager
    db = Database()
    cred_manager = CredentialManager()
    
    @app.route('/health', methods=['GET'])
    def health():
        """Health check endpoint."""
        return jsonify({'status': 'healthy', 'service': 'issuer'}), 200
    
    @app.route('/verify-identity', methods=['POST'])
    def verify_identity():
        """
        Verify student identity.
        
        Request body:
            {
                "student_id": "STU001",
                "name": "John Doe"
            }
        """
        data = request.get_json()
        student_id = data.get('student_id')
        name = data.get('name')
        
        if not student_id or not name:
            return jsonify({'error': 'Missing student_id or name'}), 400
        
        # Verify identity
        is_valid = db.verify_student_identity(student_id, name)
        
        if is_valid:
            student = db.get_student(student_id)
            return jsonify({
                'verified': True,
                'student': student
            }), 200
        else:
            return jsonify({'verified': False}), 401
    
    @app.route('/bind-key', methods=['POST'])
    def bind_key():
        """
        Bind a public key to a student ID.
        
        Request body:
            {
                "student_id": "STU001",
                "name": "John Doe",
                "public_key": "12345..."
            }
        """
        data = request.get_json()
        student_id = data.get('student_id')
        name = data.get('name')
        public_key = data.get('public_key')
        
        if not all([student_id, name, public_key]):
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Verify identity first
        if not db.verify_student_identity(student_id, name):
            return jsonify({'error': 'Identity verification failed'}), 401
        
        # Bind public key
        success = db.bind_public_key(student_id, public_key)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Public key bound successfully'
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': 'Key binding failed (may already exist)'
            }), 409
    
    @app.route('/issue-credential', methods=['POST'])
    def issue_credential():
        """
        Issue a signed credential to a student.
        
        Request body:
            {
                "student_id": "STU001",
                "public_key": "12345..."
            }
        """
        data = request.get_json()
        student_id = data.get('student_id')
        public_key = data.get('public_key')
        
        if not student_id or not public_key:
            return jsonify({'error': 'Missing student_id or public_key'}), 400
        
        # Get student data
        student = db.get_student(student_id)
        if not student:
            return jsonify({'error': 'Student not found'}), 404
        
        # Verify public key is bound
        bound_key = db.get_public_key(student_id)
        if bound_key != public_key:
            return jsonify({'error': 'Public key not bound to this student'}), 401
        
        # Issue credential
        issued = cred_manager.issue_credential(student_id, public_key, student)
        
        # Store credential
        credential_json = json.dumps(issued['credential'])
        db.store_credential(
            student_id,
            public_key,
            credential_json,
            issued['signature']
        )
        
        return jsonify({
            'success': True,
            'credential': issued['credential'],
            'signature': issued['signature']
        }), 200
    
    @app.route('/credential/<student_id>', methods=['GET'])
    def get_credential(student_id):
        """
        Get the credential for a student.
        
        Path parameter:
            student_id: Student ID
        """
        credential = db.get_credential(student_id)
        
        if credential:
            return jsonify({
                'success': True,
                'credential': json.loads(credential['credential_data']),
                'signature': credential['signature'],
                'issued_at': credential['issued_at']
            }), 200
        else:
            return jsonify({'error': 'Credential not found'}), 404
    
    @app.route('/students', methods=['GET'])
    def list_students():
        """List all students."""
        students = db.get_all_students()
        return jsonify({'students': students}), 200
    
    @app.route('/add-student', methods=['POST'])
    def add_student():
        """
        Add a new student (for testing/demo purposes).
        
        Request body:
            {
                "student_id": "STU001",
                "name": "John Doe",
                "email": "john@example.com",
                "admission_year": 2024,
                "department": "Computer Science"
            }
        """
        data = request.get_json()
        
        required_fields = ['student_id', 'name', 'email', 'admission_year', 'department']
        if not all(field in data for field in required_fields):
            return jsonify({'error': 'Missing required fields'}), 400
        
        success = db.add_student(
            data['student_id'],
            data['name'],
            data['email'],
            data['admission_year'],
            data['department']
        )
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Student added successfully'
            }), 201
        else:
            return jsonify({
                'success': False,
                'message': 'Student already exists'
            }), 409
    
    return app


if __name__ == '__main__':
    app = create_app()
    print("Starting Issuer (College) Server on http://localhost:5001")
    app.run(host='0.0.0.0', port=5001, debug=True)
