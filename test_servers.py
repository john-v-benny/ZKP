"""
Test if both servers are responding correctly.
"""

import requests
import json

print("Testing ZKP System Servers...\n")

# Test Issuer Server
print("1. Testing Issuer Server (http://localhost:5001)")
try:
    response = requests.get('http://localhost:5001/health')
    if response.status_code == 200:
        print("   ✓ Issuer server is running!")
        print(f"   Response: {response.json()}")
    else:
        print(f"   ✗ Unexpected status code: {response.status_code}")
except Exception as e:
    print(f"   ✗ Error: {e}")

print()

# Test Verifier Server
print("2. Testing Verifier Server (http://localhost:5002)")
try:
    response = requests.get('http://localhost:5002/health')
    if response.status_code == 200:
        print("   ✓ Verifier server is running!")
        print(f"   Response: {response.json()}")
    else:
        print(f"   ✗ Unexpected status code: {response.status_code}")
except Exception as e:
    print(f"   ✗ Error: {e}")

print()

# Test student verification
print("3. Testing Student Identity Verification")
try:
    response = requests.post(
        'http://localhost:5001/verify-identity',
        json={
            'student_id': 'STU001',
            'name': 'Alice Johnson'
        }
    )
    if response.status_code == 200:
        data = response.json()
        if data.get('verified'):
            print("   ✓ Student verification works!")
            print(f"   Student: {data['student']['name']}")
        else:
            print("   ✗ Verification failed")
    else:
        print(f"   ✗ Status code: {response.status_code}")
except Exception as e:
    print(f"   ✗ Error: {e}")

print("\n" + "="*50)
print("Server test complete!")
print("="*50)
