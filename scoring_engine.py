"""
Hifadhi V3: Production-Grade Scoring Engine
Multi-dimensional candidate evaluation for HR teams
"""

from typing import List, Dict, Any
import re
from datetime import datetime


class CandidateScorer:
    """
    Evaluates candidates across multiple dimensions:
    - Skills match (40%)
    - Experience depth (30%)
    - Education relevance (20%)
    - Soft skills (10%)
    """
    
    def __init__(self):
        self.weights = {
            "skills": 0.40,
            "experience": 0.30,
            "education": 0.20,
            "soft_skills": 0.10
        }
    
    def calculate_comprehensive_score(
        self,
        candidate_skills: List[str],
        required_skills: List[str],
        years_experience: int,
        required_experience: int,
        education_level: str,
        soft_skills_text: str = ""
    ) -> Dict[str, Any]:
        """
        Calculate multi-dimensional candidate score
        
        Returns:
            {
                "overall_score": 85,
                "breakdown": {
                    "skills_score": 90,
                    "experience_score": 85,
                    "education_score": 80,
                    "soft_skills_score": 75
                },
                "strengths": [...],
                "concerns": [...],
                "recommendation": "strong_match"
            }
        """
        
        # 1. Skills Match Score
        skills_score = self._score_skills_match(candidate_skills, required_skills)
        
        # 2. Experience Score
        experience_score = self._score_experience(years_experience, required_experience)
        
        # 3. Education Score
        education_score = self._score_education(education_level)
        
        # 4. Soft Skills Score (from LLM analysis or text)
        soft_skills_score = self._score_soft_skills(soft_skills_text)
        
        # Calculate weighted overall score
        overall_score = round(
            (skills_score * self.weights["skills"]) +
            (experience_score * self.weights["experience"]) +
            (education_score * self.weights["education"]) +
            (soft_skills_score * self.weights["soft_skills"])
        )
        
        # Generate insights
        breakdown = {
            "skills_score": skills_score,
            "experience_score": experience_score,
            "education_score": education_score,
            "soft_skills_score": soft_skills_score
        }
        
        strengths = self._identify_strengths(breakdown, candidate_skills, years_experience)
        concerns = self._identify_concerns(breakdown, years_experience)
        recommendation = self._get_recommendation(overall_score)
        
        return {
            "overall_score": overall_score,
            "breakdown": breakdown,
            "strengths": strengths,
            "concerns": concerns,
            "recommendation": recommendation,
            "decision": "Pass" if overall_score >= 70 else "Reject",
            "confidence": self._calculate_confidence(breakdown)
        }
    
    def _score_skills_match(self, candidate_skills: List[str], required_skills: List[str]) -> int:
        """Score based on skill overlap (0-100)"""
        if not required_skills:
            return 75  # Default if no requirements specified
        
        candidate_set = set(s.lower() for s in candidate_skills)
        required_set = set(s.lower() for s in required_skills)
        
        matches = len(candidate_set & required_set)
        total_required = len(required_set)
        
        # Bonus for extra skills
        extra_skills = len(candidate_set - required_set)
        base_score = (matches / total_required * 100) if total_required > 0 else 0
        bonus = min(extra_skills * 2, 10)  # Up to 10 bonus points
        
        return min(int(base_score + bonus), 100)
    
    def _score_experience(self, candidate_years: int, required_years: int) -> int:
        """Score based on experience level (0-100)"""
        if candidate_years >= required_years:
            # Perfect match or overqualified
            excess_years = candidate_years - required_years
            if excess_years <= 2:
                return 100  # Perfect match
            elif excess_years <= 5:
                return 95   # Slightly overqualified (good)
            else:
                return 85   # Overqualified (might leave)
        else:
            # Underqualified
            deficit = required_years - candidate_years
            penalty = deficit * 15  # -15 points per year short
            return max(0, 80 - penalty)
    
    def _score_education(self, education_level: str) -> int:
        """Score based on education level (0-100)"""
        education_scores = {
            "phd": 100,
            "doctorate": 100,
            "masters": 90,
            "mba": 90,
            "bachelors": 80,
            "bachelor": 80,
            "associate": 70,
            "diploma": 65,
            "high school": 50,
            "secondary": 50
        }
        
        education_lower = education_level.lower()
        for key, score in education_scores.items():
            if key in education_lower:
                return score
        
        return 60  # Default for unrecognized education
    
    def _score_soft_skills(self, text: str) -> int:
        """Score soft skills from text analysis (0-100)"""
        if not text:
            return 70  # Neutral score if no data
        
        positive_indicators = [
            "leadership", "team", "communication", "problem solving",
            "analytical", "creative", "collaborative", "adaptable",
            "initiative", "motivated", "proactive", "detail-oriented"
        ]
        
        text_lower = text.lower()
        matches = sum(1 for indicator in positive_indicators if indicator in text_lower)
        
        # Score based on number of positive indicators
        base_score = min(60 + (matches * 8), 100)
        return base_score
    
    def _identify_strengths(self, breakdown: Dict, skills: List[str], years_exp: int) -> List[str]:
        """Identify candidate strengths"""
        strengths = []
        
        if breakdown["skills_score"] >= 85:
            strengths.append(f"✅ Excellent skill match ({len(skills)} relevant skills)")
        
        if breakdown["experience_score"] >= 90:
            strengths.append(f"✅ {years_exp} years of highly relevant experience")
        
        if breakdown["education_score"] >= 85:
            strengths.append("✅ Advanced educational background")
        
        if breakdown["soft_skills_score"] >= 80:
            strengths.append("✅ Strong soft skills and cultural fit")
        
        return strengths if strengths else ["Good baseline qualifications"]
    
    def _identify_concerns(self, breakdown: Dict, years_exp: int) -> List[str]:
        """Identify potential concerns"""
        concerns = []
        
        if breakdown["skills_score"] < 60:
            concerns.append("⚠️ Limited skill match - may require training")
        
        if breakdown["experience_score"] < 50:
            concerns.append(f"⚠️ Only {years_exp} years experience - below requirement")
        
        if breakdown["education_score"] < 60:
            concerns.append("⚠️ Education level below typical for role")
        
        return concerns
    
    def _get_recommendation(self, score: int) -> str:
        """Get hiring recommendation based on score"""
        if score >= 85:
            return "strong_match"
        elif score >= 70:
            return "good_match"
        elif score >= 60:
            return "potential_match"
        else:
            return "weak_match"
    
    def _calculate_confidence(self, breakdown: Dict) -> str:
        """Calculate confidence in the scoring"""
        scores = list(breakdown.values())
        avg_score = sum(scores) / len(scores)
        std_dev = (sum((x - avg_score) ** 2 for x in scores) / len(scores)) ** 0.5
        
        if std_dev < 10:
            return "high"
        elif std_dev < 20:
            return "medium"
        else:
            return "low"


# Quick test
if __name__ == "__main__":
    scorer = CandidateScorer()
    
    result = scorer.calculate_comprehensive_score(
        candidate_skills=["Python", "Django", "FastAPI", "PostgreSQL"],
        required_skills=["Python", "Django", "REST API"],
        years_experience=5,
        required_experience=3,
        education_level="Bachelors",
        soft_skills_text="Strong team player with excellent communication skills"
    )
    
    print("Candidate Score:", result["overall_score"])
    print("Decision:", result["decision"])
    print("Recommendation:", result["recommendation"])
    print("\nBreakdown:")
    for key, value in result["breakdown"].items():
        print(f"  {key}: {value}")
    print("\nStrengths:")
    for s in result["strengths"]:
        print(f"  {s}")
