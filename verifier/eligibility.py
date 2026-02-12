"""
Eligibility decision engine for scholarship verification.
Determines scholarship grant/deny based on verification results.
"""

import json
from datetime import datetime
from typing import Dict, Optional


class EligibilityEngine:
    """Engine for making scholarship eligibility decisions."""
    
    def __init__(self):
        """Initialize eligibility engine."""
        self.decisions = []
    
    def check_eligibility(self, student_id: str, credential: Dict, 
                         proof_verified: bool) -> Dict:
        """
        Check scholarship eligibility.
        
        Args:
            student_id: Student ID
            credential: Student credential
            proof_verified: Whether ZKP proof was verified
            
        Returns:
            Dictionary with eligibility decision
        """
        # Basic eligibility criteria
        eligible = True
        reasons = []
        
        # Must have valid proof
        if not proof_verified:
            eligible = False
            reasons.append("ZKP proof verification failed")
            return self._create_decision(student_id, eligible, reasons)
        
        # Check credential validity
        try:
            # Check if credential has required fields
            required_fields = ['student_id', 'name', 'department', 'admission_year']
            for field in required_fields:
                if field not in credential:
                    eligible = False
                    reasons.append(f"Missing required field: {field}")
            
            # Check admission year (example: must be within last 5 years)
            if eligible and 'admission_year' in credential:
                current_year = datetime.now().year
                admission_year = credential['admission_year']
                
                if current_year - admission_year > 5:
                    eligible = False
                    reasons.append("Admission year too old (>5 years)")
            
            # Check if credential is expired
            if 'expires_at' in credential:
                expires_at = datetime.fromisoformat(credential['expires_at'])
                if datetime.utcnow() > expires_at:
                    eligible = False
                    reasons.append("Credential expired")
            
            # If all checks pass
            if eligible:
                reasons.append("All eligibility criteria met")
                reasons.append("ZKP proof verified successfully")
            
        except Exception as e:
            eligible = False
            reasons.append(f"Error checking eligibility: {str(e)}")
        
        return self._create_decision(student_id, eligible, reasons)
    
    def _create_decision(self, student_id: str, eligible: bool, 
                        reasons: list) -> Dict:
        """
        Create an eligibility decision.
        
        Args:
            student_id: Student ID
            eligible: Whether eligible
            reasons: List of reasons
            
        Returns:
            Decision dictionary
        """
        decision = {
            'student_id': student_id,
            'eligible': eligible,
            'decision': 'GRANT' if eligible else 'DENY',
            'reasons': reasons,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        # Store decision
        self.decisions.append(decision)
        
        return decision
    
    def get_decision_history(self, student_id: Optional[str] = None) -> list:
        """
        Get decision history.
        
        Args:
            student_id: Optional student ID to filter by
            
        Returns:
            List of decisions
        """
        if student_id:
            return [d for d in self.decisions if d['student_id'] == student_id]
        return self.decisions
    
    def apply_custom_criteria(self, credential: Dict, 
                             criteria: Dict) -> tuple[bool, list]:
        """
        Apply custom eligibility criteria.
        
        Args:
            credential: Student credential
            criteria: Custom criteria dictionary
            
        Returns:
            Tuple of (eligible, reasons)
        """
        eligible = True
        reasons = []
        
        # Example custom criteria
        if 'min_admission_year' in criteria:
            min_year = criteria['min_admission_year']
            if credential.get('admission_year', 0) < min_year:
                eligible = False
                reasons.append(f"Admission year before {min_year}")
        
        if 'required_department' in criteria:
            required_dept = criteria['required_department']
            if credential.get('department') != required_dept:
                eligible = False
                reasons.append(f"Not in required department: {required_dept}")
        
        return eligible, reasons
