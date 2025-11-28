"""
Document Version Control Module
Track and manage regulatory document versions
"""

from typing import Dict, List, Optional
from datetime import datetime
import hashlib
import json
import os


class DocumentVersionControl:
    """Manage document versions and track changes."""
    
    def __init__(self, version_file: str = "./document_versions.json"):
        """Initialize version control."""
        self.version_file = version_file
        self.versions = self._load_versions()
    
    def _load_versions(self) -> Dict:
        """Load version history from file."""
        if os.path.exists(self.version_file):
            with open(self.version_file, 'r') as f:
                return json.load(f)
        return {}
    
    def _save_versions(self):
        """Save version history to file."""
        with open(self.version_file, 'w') as f:
            json.dump(self.versions, f, indent=2)
    
    def _calculate_hash(self, file_path: str) -> str:
        """Calculate file hash for version tracking."""
        hasher = hashlib.md5()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                hasher.update(chunk)
        return hasher.hexdigest()
    
    def register_document(
        self,
        filename: str,
        file_path: str,
        version: str = "1.0",
        regulation_type: str = "Unknown",
        metadata: Optional[Dict] = None
    ) -> Dict:
        """
        Register a new document or version.
        
        Returns:
            Dict with registration status
        """
        file_hash = self._calculate_hash(file_path)
        file_size = os.path.getsize(file_path)
        
        if filename not in self.versions:
            # New document
            self.versions[filename] = {
                "current_version": version,
                "regulation_type": regulation_type,
                "versions": []
            }
        
        # Check if this version already exists
        existing = next(
            (v for v in self.versions[filename]['versions'] if v['hash'] == file_hash),
            None
        )
        
        if existing:
            return {
                "status": "duplicate",
                "message": f"Document already registered as version {existing['version']}"
            }
        
        # Add new version
        version_entry = {
            "version": version,
            "hash": file_hash,
            "file_size": file_size,
            "uploaded_at": datetime.now().isoformat(),
            "metadata": metadata or {}
        }
        
        self.versions[filename]['versions'].append(version_entry)
        self.versions[filename]['current_version'] = version
        self._save_versions()
        
        return {
            "status": "registered",
            "filename": filename,
            "version": version,
            "hash": file_hash
        }
    
    def get_document_info(self, filename: str) -> Optional[Dict]:
        """Get version information for a document."""
        return self.versions.get(filename)
    
    def check_for_updates(self, filename: str, current_hash: str) -> Dict:
        """Check if a newer version exists."""
        if filename not in self.versions:
            return {"has_update": False, "message": "Document not tracked"}
        
        doc_info = self.versions[filename]
        versions = doc_info['versions']
        
        if not versions:
            return {"has_update": False}
        
        # Find current version
        current_version = next(
            (v for v in versions if v['hash'] == current_hash),
            None
        )
        
        if not current_version:
            return {
                "has_update": True,
                "message": "Unknown version - update recommended",
                "latest_version": doc_info['current_version']
            }
        
        # Check if there's a newer version
        latest_version = versions[-1]
        
        if latest_version['hash'] != current_hash:
            return {
                "has_update": True,
                "current_version": current_version['version'],
                "latest_version": latest_version['version'],
                "uploaded_at": latest_version['uploaded_at']
            }
        
        return {"has_update": False, "message": "Up to date"}
    
    def get_all_documents(self) -> List[Dict]:
        """Get list of all tracked documents."""
        documents = []
        
        for filename, info in self.versions.items():
            if info['versions']:
                latest = info['versions'][-1]
                documents.append({
                    "filename": filename,
                    "regulation_type": info['regulation_type'],
                    "current_version": info['current_version'],
                    "version_count": len(info['versions']),
                    "last_updated": latest['uploaded_at'],
                    "file_size": latest['file_size']
                })
        
        return documents
    
    def get_outdated_documents(self) -> List[Dict]:
        """Get list of documents that may need updates."""
        outdated = []
        current_time = datetime.now()
        
        for filename, info in self.versions.items():
            if info['versions']:
                latest = info['versions'][-1]
                uploaded_time = datetime.fromisoformat(latest['uploaded_at'])
                days_old = (current_time - uploaded_time).days
                
                # Flag if older than 90 days
                if days_old > 90:
                    outdated.append({
                        "filename": filename,
                        "regulation_type": info['regulation_type'],
                        "version": info['current_version'],
                        "days_old": days_old,
                        "last_updated": latest['uploaded_at']
                    })
        
        return outdated
    
    def generate_version_report(self) -> str:
        """Generate a formatted version control report."""
        all_docs = self.get_all_documents()
        outdated = self.get_outdated_documents()
        
        report = f"""
# Document Version Control Report
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Summary
- Total Documents: {len(all_docs)}
- Outdated Documents (>90 days): {len(outdated)}

## All Documents
"""
        
        for doc in all_docs:
            report += f"""
### {doc['filename']}
- Regulation Type: {doc['regulation_type']}
- Current Version: {doc['current_version']}
- Total Versions: {doc['version_count']}
- Last Updated: {doc['last_updated']}
- File Size: {doc['file_size']:,} bytes
"""
        
        if outdated:
            report += "\n## ⚠️ Outdated Documents\n"
            for doc in outdated:
                report += f"- **{doc['filename']}**: {doc['days_old']} days old (Version: {doc['version']})\n"
        
        return report


# Example usage
if __name__ == "__main__":
    vc = DocumentVersionControl()
    print("Document Version Control Module - Ready for integration")
