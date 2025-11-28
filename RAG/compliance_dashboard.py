"""
Compliance Dashboard Module
Provides metrics and statistics for regulatory compliance monitoring
"""

from typing import Dict, List
from datetime import datetime, timedelta
import json
import os


class ComplianceDashboard:
    """Generate compliance metrics and dashboards."""
    
    def __init__(self, collection, audit_logger=None):
        """Initialize compliance dashboard."""
        self.collection = collection
        self.audit_logger = audit_logger
    
    def get_document_coverage(self) -> Dict:
        """Get coverage by regulatory body."""
        try:
            # Get all documents
            results = self.collection.get()
            
            if not results or not results.get('metadatas'):
                return {
                    "total_documents": 0,
                    "coverage_by_regulation": {},
                    "last_updated": datetime.now().isoformat()
                }
            
            # Count documents by source
            sources = {}
            for metadata in results['metadatas']:
                source = metadata.get('source', 'Unknown')
                if source not in sources:
                    sources[source] = 0
                sources[source] += 1
            
            # Categorize by regulation
            coverage = {
                "RBI": 0,
                "SEBI": 0,
                "FATF": 0,
                "GDPR": 0,
                "Other": 0
            }
            
            for source, count in sources.items():
                source_lower = source.lower()
                if 'rbi' in source_lower:
                    coverage["RBI"] += count
                elif 'sebi' in source_lower:
                    coverage["SEBI"] += count
                elif 'fatf' in source_lower:
                    coverage["FATF"] += count
                elif 'gdpr' in source_lower:
                    coverage["GDPR"] += count
                else:
                    coverage["Other"] += count
            
            total_chunks = sum(coverage.values())
            
            # Calculate percentages (assuming 100 chunks per regulation is 100%)
            coverage_percent = {}
            for reg, count in coverage.items():
                if count > 0:
                    # Simplified: 100 chunks = 100% coverage
                    coverage_percent[reg] = min(count, 100)
                else:
                    coverage_percent[reg] = 0
            
            return {
                "total_documents": len(sources),
                "total_chunks": total_chunks,
                "coverage_by_regulation": coverage,
                "coverage_percentage": coverage_percent,
                "document_list": list(sources.keys()),
                "last_updated": datetime.now().isoformat()
            }
        
        except Exception as e:
            return {
                "error": str(e),
                "total_documents": 0,
                "coverage_by_regulation": {},
                "last_updated": datetime.now().isoformat()
            }
    
    def get_query_statistics(self) -> Dict:
        """Get query statistics from audit logs."""
        if not self.audit_logger:
            return {"error": "Audit logger not configured"}
        
        stats = self.audit_logger.get_statistics()
        
        # Get recent queries for analysis
        recent_queries = self.audit_logger.get_query_history(limit=100)
        
        if recent_queries:
            # Calculate average confidence
            confidences = [q.get('confidence_score', 0) for q in recent_queries]
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0
            
            # Calculate average risk
            risks = [q.get('risk_score', 0) for q in recent_queries]
            avg_risk = sum(risks) / len(risks) if risks else 0
            
            # Count high-risk queries
            high_risk_count = sum(1 for r in risks if r >= 70)
            
            stats.update({
                "avg_confidence_score": round(avg_confidence, 2),
                "avg_risk_score": round(avg_risk, 2),
                "high_risk_queries": high_risk_count,
                "recent_query_count": len(recent_queries)
            })
        
        return stats
    
    def get_compliance_score(self) -> Dict:
        """Calculate overall compliance score."""
        coverage = self.get_document_coverage()
        query_stats = self.get_query_statistics()
        
        # Calculate compliance score (0-100)
        score_components = []
        
        # Document coverage (40% weight)
        if coverage.get('coverage_percentage'):
            avg_coverage = sum(coverage['coverage_percentage'].values()) / len(coverage['coverage_percentage'])
            score_components.append(avg_coverage * 0.4)
        
        # Query confidence (30% weight)
        if 'avg_confidence_score' in query_stats:
            score_components.append(query_stats['avg_confidence_score'] * 100 * 0.3)
        
        # Low risk queries (30% weight)
        if 'avg_risk_score' in query_stats:
            # Inverse risk score (lower risk = higher compliance)
            risk_compliance = (100 - query_stats['avg_risk_score']) * 0.3
            score_components.append(risk_compliance)
        
        overall_score = sum(score_components) if score_components else 0
        
        # Determine status
        if overall_score >= 80:
            status = "EXCELLENT"
            color = "green"
        elif overall_score >= 60:
            status = "GOOD"
            color = "yellow"
        elif overall_score >= 40:
            status = "FAIR"
            color = "orange"
        else:
            status = "NEEDS IMPROVEMENT"
            color = "red"
        
        return {
            "overall_score": round(overall_score, 1),
            "status": status,
            "status_color": color,
            "components": {
                "document_coverage": round(score_components[0] if len(score_components) > 0 else 0, 1),
                "query_confidence": round(score_components[1] if len(score_components) > 1 else 0, 1),
                "risk_management": round(score_components[2] if len(score_components) > 2 else 0, 1)
            },
            "timestamp": datetime.now().isoformat()
        }
    
    def get_recent_alerts(self, limit: int = 10) -> List[Dict]:
        """Get recent compliance alerts."""
        if not self.audit_logger:
            return []
        
        return self.audit_logger.get_alerts(limit=limit)
    
    def generate_dashboard_summary(self) -> str:
        """Generate a formatted dashboard summary."""
        coverage = self.get_document_coverage()
        stats = self.get_query_statistics()
        compliance = self.get_compliance_score()
        alerts = self.get_recent_alerts(limit=5)
        
        summary = f"""
# Compliance Dashboard Summary
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Overall Compliance Score: {compliance['overall_score']}/100 - {compliance['status']}

### Document Coverage
- Total Documents: {coverage.get('total_documents', 0)}
- Total Chunks: {coverage.get('total_chunks', 0)}

Regulation Coverage:
"""
        
        for reg, percent in coverage.get('coverage_percentage', {}).items():
            summary += f"- {reg}: {percent}%\n"
        
        summary += f"""
### Query Statistics
- Total Queries: {stats.get('total_queries', 0)}
- Average Confidence: {stats.get('avg_confidence_score', 0):.2f}
- Average Risk Score: {stats.get('avg_risk_score', 0):.2f}
- High-Risk Queries: {stats.get('high_risk_queries', 0)}

### Recent Alerts ({len(alerts)})
"""
        
        for alert in alerts:
            summary += f"- [{alert.get('severity')}] {alert.get('message')}\n"
        
        return summary


# Example usage
if __name__ == "__main__":
    # This would be used with actual collection and logger
    print("Compliance Dashboard Module - Ready for integration")
