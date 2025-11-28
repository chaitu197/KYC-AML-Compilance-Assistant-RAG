"""
RAG Engine Module
Handles query processing, context retrieval, and answer generation.
"""

from typing import List, Dict, Optional
import google.generativeai as genai
from document_processor import DocumentProcessor


class RAGEngine:
    """RAG engine for question answering over documents."""
    
    def __init__(self, api_key: str):
        """
        Initialize the RAG engine.
        
        Args:
            api_key: Google API key
        """
        self.api_key = api_key
        self.doc_processor = DocumentProcessor()
        self.doc_processor.initialize_embeddings(api_key)
        
        # Configure Gemini
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-pro')
        
        # Conversation history
        self.conversation_history = []
    
    def generate_answer(
        self, 
        query: str, 
        n_context_chunks: int = 5,
        include_sources: bool = True
    ) -> Dict:
        """
        Generate an answer to a query using RAG.
        
        Args:
            query: User's question
            n_context_chunks: Number of context chunks to retrieve
            include_sources: Whether to include source citations
            
        Returns:
            Dictionary with answer and metadata
        """
        try:
            # Retrieve relevant context
            context_chunks = self.doc_processor.query_documents(
                query=query,
                n_results=n_context_chunks
            )
            
            if not context_chunks:
                return {
                    "success": False,
                    "answer": "I don't have any documents to answer this question. Please upload relevant regulatory documents first.",
                    "sources": []
                }
            
            # Build context string
            context_text = "\n\n".join([
                f"[Source: {chunk['metadata'].get('source', 'Unknown')}]\n{chunk['content']}"
                for chunk in context_chunks
            ])
            
            # Create prompt
            prompt = self._create_prompt(query, context_text)
            
            # Generate response
            response = self.model.generate_content(prompt)
            answer = response.text
            
            # Extract unique sources
            sources = []
            seen_sources = set()
            for chunk in context_chunks:
                source = chunk['metadata'].get('source', 'Unknown')
                if source not in seen_sources:
                    sources.append({
                        "filename": source,
                        "chunk_index": chunk['metadata'].get('chunk_index', 0)
                    })
                    seen_sources.add(source)
            
            # Add to conversation history
            self.conversation_history.append({
                "query": query,
                "answer": answer,
                "sources": sources
            })
            
            return {
                "success": True,
                "answer": answer,
                "sources": sources if include_sources else [],
                "context_chunks_used": len(context_chunks)
            }
            
        except Exception as e:
            return {
                "success": False,
                "answer": f"Error generating answer: {str(e)}",
                "sources": []
            }
    
    def _create_prompt(self, query: str, context: str) -> str:
        """
        Create a prompt for the LLM.
        
        Args:
            query: User's question
            context: Retrieved context from documents
            
        Returns:
            Formatted prompt
        """
        prompt = f"""You are an expert assistant specializing in KYC (Know Your Customer) and AML (Anti-Money Laundering) compliance regulations. Your role is to provide accurate, detailed answers based on regulatory documents.

Context from regulatory documents:
{context}

User Question: {query}

Instructions:
1. Answer the question based ONLY on the information provided in the context above.
2. Be specific and cite relevant regulations, requirements, or guidelines.
3. If the context doesn't contain enough information to fully answer the question, acknowledge this and provide what information is available.
4. Use clear, professional language suitable for compliance professionals.
5. Organize your answer with bullet points or numbered lists when appropriate.
6. If mentioning specific requirements, be precise about what is mandatory vs. recommended.

Answer:"""
        
        return prompt
    
    def get_conversation_history(self) -> List[Dict]:
        """
        Get the conversation history.
        
        Returns:
            List of conversation exchanges
        """
        return self.conversation_history
    
    def clear_conversation_history(self):
        """Clear the conversation history."""
        self.conversation_history = []
    
    def process_sample_documents(self, documents_dir: str = "./documents") -> Dict:
        """
        Process all sample documents in a directory.
        
        Args:
            documents_dir: Directory containing sample documents
            
        Returns:
            Processing results
        """
        import os
        
        results = {
            "success": True,
            "processed": [],
            "failed": [],
            "total_chunks": 0
        }
        
        if not os.path.exists(documents_dir):
            return {
                "success": False,
                "error": f"Directory {documents_dir} not found."
            }
        
        # Process each file in the directory
        for filename in os.listdir(documents_dir):
            if filename.endswith(('.txt', '.pdf')):
                file_path = os.path.join(documents_dir, filename)
                result = self.doc_processor.process_document(file_path, filename)
                
                if result.get("success"):
                    results["processed"].append(filename)
                    results["total_chunks"] += result.get("chunks_created", 0)
                else:
                    results["failed"].append({
                        "filename": filename,
                        "error": result.get("error", "Unknown error")
                    })
        
        if results["failed"]:
            results["success"] = False
        
        return results
    
    def get_database_stats(self) -> Dict:
        """
        Get statistics about the document database.
        
        Returns:
            Database statistics
        """
        return self.doc_processor.get_collection_stats()
    
    def clear_database(self) -> Dict:
        """
        Clear all documents from the database.
        
        Returns:
            Operation result
        """
        result = self.doc_processor.clear_collection()
        if result.get("success"):
            self.clear_conversation_history()
        return result
