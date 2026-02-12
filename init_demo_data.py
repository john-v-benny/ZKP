"""
Initialize demo data for the ZKP scholarship verification system.
Creates sample students in the issuer database.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from issuer.database import Database


def init_demo_data():
    """Initialize database with demo students."""
    print("Initializing demo data...")
    
    db = Database()
    
    # Demo students
    students = [
        {
            'student_id': 'STU001',
            'name': 'Alice Johnson',
            'email': 'alice.johnson@college.edu',
            'admission_year': 2024,
            'department': 'Computer Science'
        },
        {
            'student_id': 'STU002',
            'name': 'Bob Smith',
            'email': 'bob.smith@college.edu',
            'admission_year': 2023,
            'department': 'Electrical Engineering'
        },
        {
            'student_id': 'STU003',
            'name': 'Carol Davis',
            'email': 'carol.davis@college.edu',
            'admission_year': 2022,
            'department': 'Mathematics'
        },
        {
            'student_id': 'STU004',
            'name': 'David Wilson',
            'email': 'david.wilson@college.edu',
            'admission_year': 2024,
            'department': 'Physics'
        },
        {
            'student_id': 'STU005',
            'name': 'Eve Martinez',
            'email': 'eve.martinez@college.edu',
            'admission_year': 2023,
            'department': 'Computer Science'
        }
    ]
    
    # Add students
    for student in students:
        success = db.add_student(
            student['student_id'],
            student['name'],
            student['email'],
            student['admission_year'],
            student['department']
        )
        
        if success:
            print(f"✓ Added student: {student['student_id']} - {student['name']}")
        else:
            print(f"  Student {student['student_id']} already exists")
    
    db.close()
    print("\nDemo data initialization complete!")
    print("\nYou can now use these students to test the system:")
    for student in students:
        print(f"  - {student['student_id']}: {student['name']}")


if __name__ == '__main__':
    init_demo_data()
