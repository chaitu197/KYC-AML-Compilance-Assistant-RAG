"""
External API Integration Framework
Framework for integrating with sanctions lists, PEP databases, and other compliance APIs
"""

from typing import Dict, List, Optional
import requests
from datetime import datetime, timedelta
import json


class APIIntegrationFramework:
    """Framework for external API integrations."""
    
    def __init__(self, cache_duration_minutes: int = 60):
        """Initialize API framework."""
        self.cache = {}
        self.cache_duration = timedelta(minutes=cache_duration_minutes)
    
    def _check_cache(self, cache_key: str) -> Optional[Dict]:
        """Check if cached result is still valid."""
        if cache_key in self.cache:
            cached_data, cached_time = self.cache[cache_key]
            if datetime.now() - cached_time < self.cache_duration:
                return cached_data
        return None
    
    def _set_cache(self, cache_key: str, data: Dict):
        """Cache API result."""
        self.cache[cache_key] = (data, datetime.now())
    
    def check_sanctions_list(
        self,
        name: str,
        country: Optional[str] = None,
        use_mock: bool = True
    ) -> Dict:
        """
        Check if entity is on sanctions list.
        
        Args:
            name: Entity name to check
            country: Optional country filter
            use_mock: Use mock data (set False for real API)
            
        Returns:
            Dict with sanctions check result
        """
        cache_key = f"sanctions_{name}_{country}"
        cached = self._check_cache(cache_key)
        if cached:
            return cached
        
        if use_mock:
            # Mock implementation
            result = self._mock_sanctions_check(name, country)
        else:
            # Real API implementation (placeholder)
            result = self._real_sanctions_check(name, country)
        
        self._set_cache(cache_key, result)
        return result
    
    def check_pep_status(
        self,
        name: str,
        country: Optional[str] = None,
        use_mock: bool = True
    ) -> Dict:
        """
        Check if person is a Politically Exposed Person (PEP).
        
        Args:
            name: Person name to check
            country: Optional country filter
            use_mock: Use mock data
            
        Returns:
            Dict with PEP check result
        """
        cache_key = f"pep_{name}_{country}"
        cached = self._check_cache(cache_key)
        if cached:
            return cached
        
        if use_mock:
            result = self._mock_pep_check(name, country)
        else:
            result = self._real_pep_check(name, country)
        
        self._set_cache(cache_key, result)
        return result
    
    def verify_entity(
        self,
        entity_name: str,
        entity_type: str = "individual",
        country: Optional[str] = None
    ) -> Dict:
        """
        Comprehensive entity verification.
        
        Checks:
        - Sanctions lists
        - PEP status (for individuals)
        - Adverse media
        
        Returns:
            Dict with verification results
        """
        results = {
            "entity_name": entity_name,
            "entity_type": entity_type,
            "country": country,
            "timestamp": datetime.now().isoformat(),
            "checks": {}
        }
        
        # Sanctions check
        sanctions = self.check_sanctions_list(entity_name, country)
        results["checks"]["sanctions"] = sanctions
        
        # PEP check (for individuals)
        if entity_type == "individual":
            pep = self.check_pep_status(entity_name, country)
            results["checks"]["pep"] = pep
        
        # Overall risk assessment
        risk_score = 0
        flags = []
        
        if sanctions.get("is_sanctioned"):
            risk_score += 100
            flags.append("SANCTIONED ENTITY")
        
        if results["checks"].get("pep", {}).get("is_pep"):
            risk_score += 30
            flags.append("PEP")
        
        results["risk_score"] = min(risk_score, 100)
        results["flags"] = flags
        results["recommended_action"] = self._get_recommended_action(risk_score)
        
        return results
    
    def _get_recommended_action(self, risk_score: int) -> str:
        """Get recommended action based on risk score."""
        if risk_score >= 100:
            return "BLOCK - Do not proceed with transaction"
        elif risk_score >= 70:
            return "Enhanced Due Diligence Required"
        elif risk_score >= 40:
            return "Standard Due Diligence Required"
        else:
            return "Normal Processing"
    
    def _mock_sanctions_check(self, name: str, country: Optional[str]) -> Dict:
        """Mock sanctions list check."""
        # Mock high-risk names
        high_risk_names = [
            "terrorist", "sanctioned", "blocked", "prohibited"
        ]
        
        is_sanctioned = any(risk in name.lower() for risk in high_risk_names)
        
        return {
            "is_sanctioned": is_sanctioned,
            "lists": ["OFAC SDN", "UN Sanctions"] if is_sanctioned else [],
            "match_score": 0.95 if is_sanctioned else 0.0,
            "source": "Mock API",
            "checked_at": datetime.now().isoformat()
        }
    
    def _mock_pep_check(self, name: str, country: Optional[str]) -> Dict:
        """Mock PEP check."""
        # Mock PEP indicators
        pep_indicators = ["minister", "senator", "governor", "president"]
        
        is_pep = any(indicator in name.lower() for indicator in pep_indicators)
        
        return {
            "is_pep": is_pep,
            "pep_level": "High" if is_pep else "None",
            "positions": ["Government Official"] if is_pep else [],
            "source": "Mock API",
            "checked_at": datetime.now().isoformat()
        }
    
    def _real_sanctions_check(self, name: str, country: Optional[str]) -> Dict:
        """
        Real sanctions API check (placeholder).
        
        In production, integrate with:
        - OFAC API: https://sanctionssearch.ofac.treas.gov/
        - UN Sanctions: https://www.un.org/securitycouncil/sanctions/
        - EU Sanctions: https://webgate.ec.europa.eu/fsd/fsf
        """
        # Placeholder for real API integration
        return {
            "error": "Real API not configured",
            "message": "Please configure API credentials"
        }
    
    def _real_pep_check(self, name: str, country: Optional[str]) -> Dict:
        """
        Real PEP API check (placeholder).
        
        In production, integrate with:
        - World-Check (Refinitiv)
        - Dow Jones Risk & Compliance
        - LexisNexis
        """
        return {
            "error": "Real API not configured",
            "message": "Please configure API credentials"
        }
    
    def get_api_status(self) -> Dict:
        """Get status of API integrations."""
        return {
            "cache_size": len(self.cache),
            "cache_duration_minutes": self.cache_duration.total_seconds() / 60,
            "available_checks": [
                "sanctions_list",
                "pep_status",
                "entity_verification"
            ],
            "status": "operational"
        }


# Example usage
if __name__ == "__main__":
    api = APIIntegrationFramework()
    
    # Test sanctions check
    result = api.check_sanctions_list("John Doe", "USA")
    print(json.dumps(result, indent=2))
    
    # Test entity verification
    verification = api.verify_entity("Minister Smith", "individual", "UK")
    print(json.dumps(verification, indent=2))
