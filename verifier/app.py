"""
Flask application for verifier (scholarship backend) layer.
Provides APIs for ZKP verification and eligibility checking.
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from verifier.registry import PublicKeyRegistry
from verifier.verification import ZKPVerifier
from verifier.eligibility import EligibilityEngine
from issuer.credentials import CredentialManager


def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__)
    CORS(app)  # Enable CORS for all routes
    
    # Initialize components
    registry = PublicKeyRegistry()
    zkp_verifier = ZKPVerifier()
    eligibility_engine = EligibilityEngine()
    cred_manager = CredentialManager()  # For validating credentials
    
    @app.route('/health', methods=['GET'])
    def health():
        """Health check endpoint."""
        return jsonify({'status': 'healthy', 'service': 'verifier'}), 200
    
    @app.route('/register-credential', methods=['POST'])
    def register_credential():
        """
        Register a student's credential in the public key registry.
        
        Request body:
            {
                "student_id": "STU001",
                "credential": {...},
                "signature": "abc123..."
            }
        """
        data = request.get_json()
        student_id = data.get('student_id')
        credential = data.get('credential')
        signature = data.get('signature')
        
        if not all([student_id, credential, signature]):
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Validate credential signature
        credential_json = json.dumps(credential)
        is_valid = cred_manager.validate_credential(credential_json, signature)
        
        if not is_valid:
            return jsonify({'error': 'Invalid credential or signature'}), 401
        
        # Extract public key
        public_key = credential.get('public_key')
        if not public_key:
            return jsonify({'error': 'No public key in credential'}), 400
        
        # Register in registry
        success = registry.register_public_key(
            student_id,
            public_key,
            credential_json,
            signature
        )
        
        return jsonify({
            'success': success,
            'message': 'Credential registered successfully' if success else 'Registration failed'
        }), 200 if success else 500
    
    @app.route('/request-challenge', methods=['POST'])
    def request_challenge():
        """
        Request a challenge for ZKP verification.
        
        Request body:
            {
                "student_id": "STU001"
            }
        """
        data = request.get_json()
        student_id = data.get('student_id')
        
        if not student_id:
            return jsonify({'error': 'Missing student_id'}), 400
        
        # Check if student has registered credential
        key_data = registry.get_public_key(student_id)
        if not key_data:
            return jsonify({'error': 'Student not registered'}), 404
        
        # Generate challenge session
        session = zkp_verifier.generate_challenge_session()
        
        # Store challenge in registry
        registry.store_challenge(
            session['session_id'],
            session['challenge'],
            student_id
        )
        
        return jsonify({
            'session_id': session['session_id'],
            'challenge': session['challenge']
        }), 200
    
    @app.route('/verify-proof', methods=['POST'])
    def verify_proof():
        """
        Verify a ZKP proof.
        
        Request body:
            {
                "session_id": "uuid",
                "student_id": "STU001",
                "proof": {
                    "commitment": "123...",
                    "response": "456..."
                }
            }
        """
        data = request.get_json()
        session_id = data.get('session_id')
        student_id = data.get('student_id')
        proof = data.get('proof')
        
        if not all([session_id, student_id, proof]):
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Get challenge from session
        challenge = registry.get_challenge(session_id)
        if not challenge:
            return jsonify({'error': 'Invalid or expired session'}), 401
        
        # Get public key
        key_data = registry.get_public_key(student_id)
        if not key_data:
            return jsonify({'error': 'Student not registered'}), 404
        
        public_key = key_data['public_key']
        
        # Verify proof
        is_valid = zkp_verifier.verify_complete_proof(proof, challenge, public_key)
        
        # Mark challenge as used
        if is_valid:
            registry.mark_challenge_used(session_id)
        
        return jsonify({
            'verified': is_valid,
            'message': 'Proof verified successfully' if is_valid else 'Proof verification failed'
        }), 200
    
    @app.route('/check-eligibility', methods=['POST'])
    def check_eligibility():
        """
        Check scholarship eligibility (complete workflow).
        
        Request body:
            {
                "session_id": "uuid",
                "student_id": "STU001",
                "proof": {
                    "commitment": "123...",
                    "response": "456..."
                }
            }
        """
        data = request.get_json()
        session_id = data.get('session_id')
        student_id = data.get('student_id')
        proof = data.get('proof')
        
        if not all([session_id, student_id, proof]):
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Get challenge
        challenge = registry.get_challenge(session_id)
        if not challenge:
            return jsonify({'error': 'Invalid or expired session'}), 401
        
        # Get credential
        key_data = registry.get_public_key(student_id)
        if not key_data:
            return jsonify({'error': 'Student not registered'}), 404
        
        public_key = key_data['public_key']
        credential = json.loads(key_data['credential_data'])
        
        # Verify proof
        proof_verified = zkp_verifier.verify_complete_proof(proof, challenge, public_key)
        
        # Mark challenge as used
        if proof_verified:
            registry.mark_challenge_used(session_id)
        
        # Check eligibility
        decision = eligibility_engine.check_eligibility(
            student_id,
            credential,
            proof_verified
        )
        
        return jsonify(decision), 200
    
    @app.route('/registry/<student_id>', methods=['GET'])
    def get_registry_entry(student_id):
        """
        Get registry entry for a student.
        
        Path parameter:
            student_id: Student ID
        """
        key_data = registry.get_public_key(student_id)
        
        if key_data:
            return jsonify({
                'student_id': key_data['student_id'],
                'public_key': key_data['public_key'],
                'credential': json.loads(key_data['credential_data']),
                'registered_at': key_data['registered_at']
            }), 200
        else:
            return jsonify({'error': 'Student not found in registry'}), 404
    
    @app.route('/decisions', methods=['GET'])
    def get_decisions():
        """Get all eligibility decisions."""
        student_id = request.args.get('student_id')
        decisions = eligibility_engine.get_decision_history(student_id)
        return jsonify({'decisions': decisions}), 200
    
    return app


if __name__ == '__main__':
    app = create_app()
    print("Starting Verifier (Scholarship Backend) Server on http://localhost:5002")
    app.run(host='0.0.0.0', port=5002, debug=True)
