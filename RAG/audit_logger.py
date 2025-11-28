"""
Audit Trail and Logging Module
Tracks all user interactions for compliance and regulatory requirements
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional
import hashlib


class AuditLogger:
    """Comprehensive audit logging for compliance."""
    
    def __init__(self, log_dir: str = "./audit_logs"):
        """Initialize audit logger."""
        self.log_dir = log_dir
        os.makedirs(log_dir, exist_ok=True)
        
        self.query_log_file = os.path.join(log_dir, "query_log.jsonl")
        self.access_log_file = os.path.join(log_dir, "access_log.jsonl")
        self.alert_log_file = os.path.join(log_dir, "alert_log.jsonl")
        self.document_log_file = os.path.join(log_dir, "document_log.jsonl")
    
    def log_query(
        self,
        user_id: str,
        query: str,
        answer: str,
        sources: List[Dict],
        confidence: float,
        risk_score: int = 0,
        metadata: Optional[Dict] = None
    ) -> str:
        """
        Log a user query and response.
        
        Returns:
            Query ID for reference
        """
        query_id = self._generate_id(query, user_id)
        
        log_entry = {
            "query_id": query_id,
            "timestamp": datetime.now().isoformat(),
            "user_id": user_id,
            "query": query,
            "answer_preview": answer[:200] + "..." if len(answer) > 200 else answer,
            "answer_length": len(answer),
            "sources_used": [s.get('filename', 'Unknown') for s in sources],
            "source_count": len(sources),
            "confidence_score": confidence,
            "risk_score": risk_score,
            "metadata": metadata or {}
        }
        
        self._write_log(self.query_log_file, log_entry)
        return query_id
    
    def log_access(
        self,
        user_id: str,
        action: str,
        resource: str,
        status: str = "success",
        metadata: Optional[Dict] = None
    ):
        """Log user access and actions."""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "user_id": user_id,
            "action": action,
            "resource": resource,
            "status": status,
            "metadata": metadata or {}
        }
        
        self._write_log(self.access_log_file, log_entry)
    
    def log_alert(
        self,
        alert_type: str,
        severity: str,
        message: str,
        query_id: Optional[str] = None,
        user_id: Optional[str] = None,
        metadata: Optional[Dict] = None
    ) -> str:
        """
        Log a compliance alert.
        
        Returns:
            Alert ID
        """
        alert_id = self._generate_id(message, alert_type)
        
        log_entry = {
            "alert_id": alert_id,
            "timestamp": datetime.now().isoformat(),
            "alert_type": alert_type,
            "severity": severity,
            "message": message,
            "query_id": query_id,
            "user_id": user_id,
            "metadata": metadata or {}
        }
        
        self._write_log(self.alert_log_file, log_entry)
        return alert_id
    
    def log_document_upload(
        self,
        user_id: str,
        filename: str,
        file_size: int,
        file_type: str,
        chunks_created: int,
        status: str = "success"
    ):
        """Log document upload and processing."""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "user_id": user_id,
            "filename": filename,
            "file_size": file_size,
            "file_type": file_type,
            "chunks_created": chunks_created,
            "status": status
        }
        
        self._write_log(self.document_log_file, log_entry)
    
    def get_query_history(
        self,
        user_id: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict]:
        """Retrieve query history."""
        return self._read_log(self.query_log_file, user_id, limit)
    
    def get_alerts(
        self,
        severity: Optional[str] = None,
        limit: int = 50
    ) -> List[Dict]:
        """Retrieve alerts."""
        alerts = self._read_log(self.alert_log_file, limit=limit)
        
        if severity:
            alerts = [a for a in alerts if a.get('severity') == severity]
        
        return alerts
    
    def get_statistics(self) -> Dict:
        """Get audit statistics."""
        query_count = self._count_lines(self.query_log_file)
        access_count = self._count_lines(self.access_log_file)
        alert_count = self._count_lines(self.alert_log_file)
        document_count = self._count_lines(self.document_log_file)
        
        # Get recent alerts
        recent_alerts = self.get_alerts(limit=10)
        high_severity_alerts = [a for a in recent_alerts if a.get('severity') == 'HIGH']
        
        return {
            "total_queries": query_count,
            "total_access_logs": access_count,
            "total_alerts": alert_count,
            "total_documents_processed": document_count,
            "recent_high_severity_alerts": len(high_severity_alerts),
            "last_updated": datetime.now().isoformat()
        }
    
    def export_audit_trail(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        output_file: Optional[str] = None
    ) -> str:
        """Export audit trail for compliance reporting."""
        if not output_file:
            output_file = os.path.join(
                self.log_dir,
                f"audit_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            )
        
        export_data = {
            "export_timestamp": datetime.now().isoformat(),
            "date_range": {
                "start": start_date,
                "end": end_date
            },
            "queries": self._read_log(self.query_log_file),
            "access_logs": self._read_log(self.access_log_file),
            "alerts": self._read_log(self.alert_log_file),
            "documents": self._read_log(self.document_log_file)
        }
        
        with open(output_file, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        return output_file
    
    def _generate_id(self, *args) -> str:
        """Generate unique ID from arguments."""
        content = ''.join(str(arg) for arg in args) + str(datetime.now())
        return hashlib.md5(content.encode()).hexdigest()[:12]
    
    def _write_log(self, log_file: str, entry: Dict):
        """Write log entry to file."""
        with open(log_file, 'a') as f:
            f.write(json.dumps(entry) + '\n')
    
    def _read_log(
        self,
        log_file: str,
        user_id: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict]:
        """Read log entries from file."""
        if not os.path.exists(log_file):
            return []
        
        entries = []
        with open(log_file, 'r') as f:
            for line in f:
                try:
                    entry = json.loads(line.strip())
                    if user_id is None or entry.get('user_id') == user_id:
                        entries.append(entry)
                except json.JSONDecodeError:
                    continue
        
        # Return most recent entries
        return entries[-limit:]
    
    def _count_lines(self, log_file: str) -> int:
        """Count lines in log file."""
        if not os.path.exists(log_file):
            return 0
        
        with open(log_file, 'r') as f:
            return sum(1 for _ in f)


# Example usage
if __name__ == "__main__":
    logger = AuditLogger()
    
    # Log a query
    query_id = logger.log_query(
        user_id="user123",
        query="What are KYC requirements?",
        answer="KYC requirements include...",
        sources=[{"filename": "rbi_kyc.pdf"}],
        confidence=0.89,
        risk_score=15
    )
    print(f"Logged query: {query_id}")
    
    # Log an alert
    alert_id = logger.log_alert(
        alert_type="HIGH_RISK_QUERY",
        severity="HIGH",
        message="Suspicious query detected",
        query_id=query_id,
        user_id="user123"
    )
    print(f"Logged alert: {alert_id}")
    
    # Get statistics
    stats = logger.get_statistics()
    print(json.dumps(stats, indent=2))
