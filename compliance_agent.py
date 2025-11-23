"""
Hifadhi V3: Compliance & Bias Detection Agent
Ensures fair, unbiased, and legally compliant hiring decisions
"""

from typing import Dict, List, Any
from datetime import datetime
import json


class ComplianceAgent:
    """
    Monitors hiring decisions for:
    - Bias detection (gender, age, race, etc.)
    - EEOC compliance
    - Audit trail generation
    - Decision justification
    """
    
    def __init__(self):
        self.protected_attributes = [
            "gender", "age", "race", "ethnicity", "religion",
            "disability", "marital status", "pregnancy", "national origin"
        ]
        self.audit_log = []
    
    def review_decision(
        self,
        candidate_id: str,
        candidate_name: str,
        decision: str,
        score: int,
        reasoning: str,
        decision_maker: str = "AI System"
    ) -> Dict[str, Any]:
        """
        Review a hiring decision for compliance and bias
        
        Returns:
            {
                "approved": True,
                "bias_detected": False,
                "compliance_notes": [...],
                "audit_entry_id": "AUD12345",
                "warnings": []
            }
        """
        
        timestamp = datetime.now().isoformat()
        
        # 1. Check for bias indicators in reasoning
        bias_check = self._check_for_bias(reasoning)
        
        # 2. Validate decision justification
        justification_check = self._validate_justification(reasoning, score, decision)
        
        # 3. Check for consistency (similar candidates should get similar scores)
        # In production, this would compare against historical decisions
        consistency_check = {"consistent": True, "notes": "Manual review recommended for edge cases"}
        
        # 4. Generate audit entry
        audit_entry = {
            "audit_id": f"AUD{len(self.audit_log) + 1:05d}",
            "timestamp": timestamp,
            "candidate_id": candidate_id,
            "candidate_name": candidate_name,
            "decision": decision,
            "score": score,
            "reasoning": reasoning,
            "decision_maker": decision_maker,
            "bias_check": bias_check,
            "compliance_status": "approved" if not bias_check["detected"] else "flagged",
            "reviewer": "ComplianceAgent V3"
        }
        
        self.audit_log.append(audit_entry)
        
        # 5. Determine approval
        approved = not bias_check["detected"] and justification_check["valid"]
        
        warnings = []
        if bias_check["detected"]:
            warnings.append(f"⚠️ Potential bias detected: {', '.join(bias_check['indicators'])}")
        if not justification_check["valid"]:
            warnings.append("⚠️ Decision justification insufficient")
        
        compliance_notes = self._generate_compliance_notes(
            decision, score, bias_check, justification_check
        )
        
        return {
            "approved": approved,
            "bias_detected": bias_check["detected"],
            "bias_indicators": bias_check["indicators"],
            "compliance_notes": compliance_notes,
            "audit_entry_id": audit_entry["audit_id"],
            "warnings": warnings,
            "recommendations": self._get_recommendations(approved, bias_check)
        }
    
    def _check_for_bias(self, reasoning: str) -> Dict[str, Any]:
        """Detect potential bias in decision reasoning"""
        reasoning_lower = reasoning.lower()
        
        detected_indicators = []
        
        # Check for protected attribute mentions
        for attr in self.protected_attributes:
            if attr in reasoning_lower:
                detected_indicators.append(f"Mentioned '{attr}'")
        
        # Check for age-related bias
        age_terms = ["too old", "too young", "recent grad", "senior citizen", "overqualified"]
        for term in age_terms:
            if term in reasoning_lower:
                detected_indicators.append(f"Age-related term: '{term}'")
        
        # Check for gender bias
        gender_terms = ["he ", "she ", "his ", "her ", "him ", "guys", "girls"]
        for term in gender_terms:
            if term in reasoning_lower and term not in ["his experience", "her experience"]:
                detected_indicators.append(f"Gender-specific language: '{term}'")
        
        # Check for culture fit bias (can be proxy for discrimination)
        if "culture fit" in reasoning_lower or "cultural fit" in reasoning_lower:
            detected_indicators.append("'Culture fit' mentioned - ensure objective criteria used")
        
        return {
            "detected": len(detected_indicators) > 0,
            "indicators": detected_indicators,
            "risk_level": "high" if len(detected_indicators) > 2 else "medium" if detected_indicators else "low"
        }
    
    def _validate_justification(self, reasoning: str, score: int, decision: str) -> Dict[str, bool]:
        """Ensure decision has proper justification"""
        
        # Check if reasoning is substantive (not just boilerplate)
        is_substantive = len(reasoning) > 50
        
        # Check if score aligns with decision
        score_aligned = (decision == "Pass" and score >= 70) or (decision == "Reject" and score < 70)
        
        # Check if reasoning mentions objective criteria
        objective_terms = ["skills", "experience", "education", "qualifications", "score"]
        mentions_objective = any(term in reasoning.lower() for term in objective_terms)
        
        valid = is_substantive and score_aligned and mentions_objective
        
        return {
            "valid": valid,
            "substantive": is_substantive,
            "score_aligned": score_aligned,
            "objective_criteria": mentions_objective
        }
    
    def _generate_compliance_notes(
        self,
        decision: str,
        score: int,
        bias_check: Dict,
        justification_check: Dict
    ) -> List[str]:
        """Generate compliance documentation notes"""
        notes = []
        
        notes.append(f"✅ Decision: {decision} (Score: {score})")
        notes.append(f"✅ Bias Risk Level: {bias_check['risk_level']}")
        notes.append(f"✅ Justification Valid: {justification_check['valid']}")
        
        if decision == "Reject" and score < 60:
            notes.append("✅ Rejection based on objective scoring criteria")
        
        if not bias_check["detected"]:
            notes.append("✅ No bias indicators detected in reasoning")
        
        notes.append("✅ Audit trail created for record-keeping")
        
        return notes
    
    def _get_recommendations(self, approved: bool, bias_check: Dict) -> List[str]:
        """Get recommendations for HR team"""
        recommendations = []
        
        if not approved:
            recommendations.append("🔍 Manual review recommended before finalizing decision")
            recommendations.append("📝 Revise reasoning to remove bias indicators")
        
        if bias_check["risk_level"] == "medium":
            recommendations.append("⚠️ Consider secondary review by HR manager")
        
        if bias_check["risk_level"] == "high":
            recommendations.append("🚨 Mandatory HR review required before proceeding")
        
        if approved:
            recommendations.append("✅ Decision approved - ready to proceed")
        
        return recommendations
    
    def generate_audit_report(self, start_date: str = None, end_date: str = None) -> Dict[str, Any]:
        """Generate compliance audit report"""
        
        total_decisions = len(self.audit_log)
        flagged_decisions = sum(1 for entry in self.audit_log if entry["compliance_status"] == "flagged")
        
        decisions_by_outcome = {}
        for entry in self.audit_log:
            outcome = entry["decision"]
            decisions_by_outcome[outcome] = decisions_by_outcome.get(outcome, 0) + 1
        
        return {
            "report_generated": datetime.now().isoformat(),
            "period": {"start": start_date, "end": end_date},
            "total_decisions": total_decisions,
            "flagged_decisions": flagged_decisions,
            "approval_rate": round((total_decisions - flagged_decisions) / total_decisions * 100, 1) if total_decisions > 0 else 0,
            "decisions_by_outcome": decisions_by_outcome,
            "recent_flags": [
                {
                    "candidate": entry["candidate_name"],
                    "reason": entry["bias_check"]["indicators"]
                }
                for entry in self.audit_log[-5:] if entry["compliance_status"] == "flagged"
            ]
        }


# Quick test
if __name__ == "__main__":
    compliance = ComplianceAgent()
    
    # Test case: Good decision
    result1 = compliance.review_decision(
        candidate_id="CAND00001",
        candidate_name="John Doe",
        decision="Pass",
        score=85,
        reasoning="Strong skills in Python and Django. 5 years of relevant experience. Education level matches requirements."
    )
    
    print("Good Decision Review:")
    print(json.dumps(result1, indent=2))
    
    print("\n" + "="*50 + "\n")
    
    # Test case: Biased decision
    result2 = compliance.review_decision(
        candidate_id="CAND00002",
        candidate_name="Jane Smith",
        decision="Reject",
        score=75,
        reasoning="She seems too young for this role and might not fit our culture."
    )
    
    print("Biased Decision Review:")
    print(json.dumps(result2, indent=2))
    
    print("\n" + "="*50 + "\n")
    
    # Generate audit report
    report = compliance.generate_audit_report()
    print("Audit Report:")
    print(json.dumps(report, indent=2))
