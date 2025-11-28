"""
Batch Query Processing Module
Process multiple queries efficiently for bulk compliance checks
"""

import csv
import json
from typing import List, Dict
from datetime import datetime
import os


class BatchProcessor:
    """Process multiple queries in batch mode."""
    
    def __init__(self, rag_engine, audit_logger=None):
        """Initialize batch processor."""
        self.rag_engine = rag_engine
        self.audit_logger = audit_logger
    
    def process_csv_queries(
        self,
        csv_file_path: str,
        output_file_path: str = None
    ) -> Dict:
        """
        Process queries from CSV file.
        
        CSV Format:
        question_id,query,category (optional)
        
        Returns:
            Dict with results and statistics
        """
        if not output_file_path:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_file_path = f"batch_results_{timestamp}.csv"
        
        results = []
        errors = []
        
        try:
            with open(csv_file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                
                for row in reader:
                    question_id = row.get('question_id', '')
                    query = row.get('query', '')
                    category = row.get('category', '')
                    
                    if not query:
                        errors.append({
                            "question_id": question_id,
                            "error": "Empty query"
                        })
                        continue
                    
                    try:
                        # Process query
                        result = self.rag_engine.generate_answer(query)
                        
                        if result.get('success'):
                            results.append({
                                "question_id": question_id,
                                "query": query,
                                "category": category,
                                "answer": result['answer'],
                                "confidence": result.get('avg_confidence', 0),
                                "sources": ', '.join([s['filename'] for s in result.get('sources', [])]),
                                "source_count": len(result.get('sources', [])),
                                "timestamp": datetime.now().isoformat()
                            })
                            
                            # Log if audit logger available
                            if self.audit_logger:
                                self.audit_logger.log_query(
                                    user_id="batch_processor",
                                    query=query,
                                    answer=result['answer'],
                                    sources=result.get('sources', []),
                                    confidence=result.get('avg_confidence', 0),
                                    metadata={"batch_id": question_id, "category": category}
                                )
                        else:
                            errors.append({
                                "question_id": question_id,
                                "query": query,
                                "error": result.get('answer', 'Unknown error')
                            })
                    
                    except Exception as e:
                        errors.append({
                            "question_id": question_id,
                            "query": query,
                            "error": str(e)
                        })
            
            # Write results to CSV
            if results:
                with open(output_file_path, 'w', newline='', encoding='utf-8') as f:
                    fieldnames = ['question_id', 'query', 'category', 'answer', 
                                  'confidence', 'sources', 'source_count', 'timestamp']
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(results)
            
            # Write errors if any
            if errors:
                error_file = output_file_path.replace('.csv', '_errors.csv')
                with open(error_file, 'w', newline='', encoding='utf-8') as f:
                    fieldnames = ['question_id', 'query', 'error']
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(errors)
            
            return {
                "success": True,
                "total_queries": len(results) + len(errors),
                "successful": len(results),
                "failed": len(errors),
                "output_file": output_file_path,
                "error_file": error_file if errors else None,
                "avg_confidence": sum(r['confidence'] for r in results) / len(results) if results else 0
            }
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def process_json_queries(
        self,
        json_file_path: str,
        output_file_path: str = None
    ) -> Dict:
        """
        Process queries from JSON file.
        
        JSON Format:
        [
            {"id": "1", "query": "What is KYC?", "metadata": {...}},
            ...
        ]
        """
        if not output_file_path:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_file_path = f"batch_results_{timestamp}.json"
        
        try:
            with open(json_file_path, 'r', encoding='utf-8') as f:
                queries = json.load(f)
            
            results = []
            
            for item in queries:
                query_id = item.get('id', '')
                query = item.get('query', '')
                metadata = item.get('metadata', {})
                
                if not query:
                    continue
                
                try:
                    result = self.rag_engine.generate_answer(query)
                    
                    if result.get('success'):
                        results.append({
                            "id": query_id,
                            "query": query,
                            "answer": result['answer'],
                            "confidence": result.get('avg_confidence', 0),
                            "sources": result.get('sources', []),
                            "metadata": metadata,
                            "timestamp": datetime.now().isoformat()
                        })
                
                except Exception as e:
                    results.append({
                        "id": query_id,
                        "query": query,
                        "error": str(e)
                    })
            
            # Write results
            with open(output_file_path, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2)
            
            successful = sum(1 for r in results if 'error' not in r)
            
            return {
                "success": True,
                "total_queries": len(results),
                "successful": successful,
                "failed": len(results) - successful,
                "output_file": output_file_path
            }
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def create_sample_batch_file(self, output_path: str = "sample_batch.csv"):
        """Create a sample batch query file."""
        sample_queries = [
            {"question_id": "1", "query": "What documents are required for merchant KYC?", "category": "KYC"},
            {"question_id": "2", "query": "What are PEP screening requirements?", "category": "AML"},
            {"question_id": "3", "query": "What are transaction monitoring thresholds?", "category": "AML"},
            {"question_id": "4", "query": "What is enhanced due diligence?", "category": "KYC"},
            {"question_id": "5", "query": "What are GDPR data retention requirements?", "category": "GDPR"}
        ]
        
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            fieldnames = ['question_id', 'query', 'category']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(sample_queries)
        
        return output_path


# Example usage
if __name__ == "__main__":
    print("Batch Processor Module - Ready for integration")
