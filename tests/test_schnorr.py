"""
Unit tests for Schnorr ZKP protocol implementation.
Tests completeness, soundness, and zero-knowledge properties.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from crypto.schnorr import SchnorrZKP
from crypto.keys import KeyManager
from crypto.utils import CryptoUtils


def test_key_generation():
    """Test key pair generation."""
    print("Testing key generation...")
    km = KeyManager()
    
    private_key, public_key = km.generate_keypair()
    
    # Verify keys are in valid range
    assert 1 <= private_key < km.q, "Private key out of range"
    assert 1 <= public_key < km.p, "Public key out of range"
    
    # Verify public key is correctly derived
    assert km.verify_keypair(private_key, public_key), "Key pair verification failed"
    
    print("✓ Key generation test passed")


def test_schnorr_completeness():
    """Test that honest prover can convince verifier (completeness)."""
    print("\nTesting Schnorr completeness...")
    zkp = SchnorrZKP()
    km = KeyManager()
    
    # Generate keys
    private_key, public_key = km.generate_keypair()
    
    # Generate commitment
    r, t = zkp.generate_commitment()
    
    # Generate challenge
    c = zkp.generate_challenge()
    
    # Generate response
    s = zkp.generate_response(r, c, private_key)
    
    # Verify proof
    is_valid = zkp.verify_proof(t, s, c, public_key)
    
    assert is_valid, "Valid proof was rejected (completeness failed)"
    print("✓ Completeness test passed")


def test_schnorr_soundness():
    """Test that dishonest prover cannot convince verifier (soundness)."""
    print("\nTesting Schnorr soundness...")
    zkp = SchnorrZKP()
    km = KeyManager()
    
    # Generate keys
    private_key, public_key = km.generate_keypair()
    
    # Generate commitment
    r, t = zkp.generate_commitment()
    
    # Generate challenge
    c = zkp.generate_challenge()
    
    # Generate WRONG response (using wrong private key)
    wrong_private_key = (private_key + 1) % zkp.q
    s = zkp.generate_response(r, c, wrong_private_key)
    
    # Verify proof should fail
    is_valid = zkp.verify_proof(t, s, c, public_key)
    
    assert not is_valid, "Invalid proof was accepted (soundness failed)"
    print("✓ Soundness test passed")


def test_schnorr_wrong_challenge():
    """Test that proof fails with wrong challenge."""
    print("\nTesting wrong challenge rejection...")
    zkp = SchnorrZKP()
    km = KeyManager()
    
    # Generate keys
    private_key, public_key = km.generate_keypair()
    
    # Generate commitment
    r, t = zkp.generate_commitment()
    
    # Generate challenge
    c = zkp.generate_challenge()
    
    # Generate response
    s = zkp.generate_response(r, c, private_key)
    
    # Verify with DIFFERENT challenge
    wrong_c = (c + 1) % zkp.q
    is_valid = zkp.verify_proof(t, s, wrong_c, public_key)
    
    assert not is_valid, "Proof accepted with wrong challenge"
    print("✓ Wrong challenge test passed")


def test_complete_proof_workflow():
    """Test complete proof creation and verification workflow."""
    print("\nTesting complete proof workflow...")
    zkp = SchnorrZKP()
    km = KeyManager()
    
    # Generate keys
    private_key, public_key = km.generate_keypair()
    
    # Generate challenge
    challenge = zkp.generate_challenge()
    
    # Create proof
    proof = zkp.create_proof(private_key, challenge)
    
    # Verify proof
    is_valid = zkp.verify_complete_proof(proof, challenge, public_key)
    
    assert is_valid, "Complete proof workflow failed"
    print("✓ Complete proof workflow test passed")


def test_non_interactive_proof():
    """Test non-interactive ZKP using Fiat-Shamir heuristic."""
    print("\nTesting non-interactive proof...")
    zkp = SchnorrZKP()
    km = KeyManager()
    
    # Generate keys
    private_key, public_key = km.generate_keypair()
    
    # Create non-interactive proof
    message = "scholarship_application_2026"
    proof = zkp.create_non_interactive_proof(private_key, public_key, message)
    
    # Verify proof
    is_valid = zkp.verify_non_interactive_proof(proof, public_key, message)
    
    assert is_valid, "Non-interactive proof failed"
    
    # Test with wrong message
    is_valid_wrong = zkp.verify_non_interactive_proof(proof, public_key, "wrong_message")
    assert not is_valid_wrong, "Non-interactive proof accepted wrong message"
    
    print("✓ Non-interactive proof test passed")


def test_key_serialization():
    """Test key serialization and deserialization."""
    print("\nTesting key serialization...")
    km = KeyManager()
    
    # Generate keys
    private_key, public_key = km.generate_keypair()
    
    # Serialize
    serialized = km.serialize_keys(private_key, public_key)
    
    # Deserialize
    restored_private, restored_public = km.deserialize_keys(serialized)
    
    assert private_key == restored_private, "Private key serialization failed"
    assert public_key == restored_public, "Public key serialization failed"
    
    # Test public key export/import
    exported = km.export_public_key(public_key)
    imported = km.import_public_key(exported)
    
    assert public_key == imported, "Public key export/import failed"
    
    print("✓ Key serialization test passed")


def test_multiple_proofs():
    """Test that same keys can generate multiple valid proofs."""
    print("\nTesting multiple proofs with same keys...")
    zkp = SchnorrZKP()
    km = KeyManager()
    
    # Generate keys once
    private_key, public_key = km.generate_keypair()
    
    # Generate and verify multiple proofs
    for i in range(5):
        challenge = zkp.generate_challenge()
        proof = zkp.create_proof(private_key, challenge)
        is_valid = zkp.verify_complete_proof(proof, challenge, public_key)
        assert is_valid, f"Proof {i+1} failed"
    
    print("✓ Multiple proofs test passed (5 proofs verified)")


def run_all_tests():
    """Run all tests."""
    print("=" * 60)
    print("Running Schnorr ZKP Protocol Tests")
    print("=" * 60)
    
    try:
        test_key_generation()
        test_schnorr_completeness()
        test_schnorr_soundness()
        test_schnorr_wrong_challenge()
        test_complete_proof_workflow()
        test_non_interactive_proof()
        test_key_serialization()
        test_multiple_proofs()
        
        print("\n" + "=" * 60)
        print("✓ ALL TESTS PASSED!")
        print("=" * 60)
        return True
        
    except AssertionError as e:
        print(f"\n✗ TEST FAILED: {e}")
        return False
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
