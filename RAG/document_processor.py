"""
Document Processor Module
Handles document ingestion, chunking, and vectorization for the RAG system.
"""

import os
from typing import List, Dict
import chromadb
from chromadb.config import Settings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from pypdf import PdfReader
import hashlib


class DocumentProcessor:
    """Processes documents and manages vector database operations."""
    
    def __init__(self, persist_directory: str = "./chroma_db"):
        """
        Initialize the document processor.
        
        Args:
            persist_directory: Directory to persist ChromaDB data
        """
        self.persist_directory = persist_directory
        self.embeddings = None
        self.chroma_client = None
        self.collection = None
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
            separators=["\n\n", "\n", ".", "!", "?", ",", " ", ""]
        )
        
    def initialize_embeddings(self, api_key: str):
        """
        Initialize the embedding model.
        
        Args:
            api_key: Google API key for embeddings
        """
        self.embeddings = GoogleGenerativeAIEmbeddings(
            model="models/embedding-001",
            google_api_key=api_key
        )
        
        # Initialize ChromaDB
        self.chroma_client = chromadb.PersistentClient(
            path=self.persist_directory,
            settings=Settings(anonymized_telemetry=False)
        )
        
        # Get or create collection
        try:
            self.collection = self.chroma_client.get_collection(name="kyc_documents")
        except:
            self.collection = self.chroma_client.create_collection(
                name="kyc_documents",
                metadata={"description": "KYC/AML regulatory documents"}
            )
    
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """
        Extract text from a PDF file.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Extracted text content
        """
        try:
            reader = PdfReader(pdf_path)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            return text
        except Exception as e:
            raise Exception(f"Error reading PDF {pdf_path}: {str(e)}")
    
    def extract_text_from_txt(self, txt_path: str) -> str:
        """
        Extract text from a text file.
        
        Args:
            txt_path: Path to the text file
            
        Returns:
            File content
        """
        try:
            with open(txt_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            raise Exception(f"Error reading text file {txt_path}: {str(e)}")
    
    def process_document(self, file_path: str, filename: str) -> Dict:
        """
        Process a document and add it to the vector database.
        
        Args:
            file_path: Path to the document file
            filename: Name of the file
            
        Returns:
            Dictionary with processing results
        """
        try:
            # Extract text based on file type
            if file_path.lower().endswith('.pdf'):
                text = self.extract_text_from_pdf(file_path)
            elif file_path.lower().endswith('.txt'):
                text = self.extract_text_from_txt(file_path)
            else:
                return {
                    "success": False,
                    "error": "Unsupported file type. Please upload PDF or TXT files."
                }
            
            # Split text into chunks
            chunks = self.text_splitter.split_text(text)
            
            if not chunks:
                return {
                    "success": False,
                    "error": "No text could be extracted from the document."
                }
            
            # Generate embeddings for chunks
            chunk_embeddings = self.embeddings.embed_documents(chunks)
            
            # Create unique IDs for chunks
            doc_hash = hashlib.md5(filename.encode()).hexdigest()[:8]
            ids = [f"{doc_hash}_chunk_{i}" for i in range(len(chunks))]
            
            # Prepare metadata
            metadatas = [
                {
                    "source": filename,
                    "chunk_index": i,
                    "total_chunks": len(chunks)
                }
                for i in range(len(chunks))
            ]
            
            # Add to ChromaDB
            self.collection.add(
                embeddings=chunk_embeddings,
                documents=chunks,
                metadatas=metadatas,
                ids=ids
            )
            
            return {
                "success": True,
                "filename": filename,
                "chunks_created": len(chunks),
                "message": f"Successfully processed {filename} into {len(chunks)} chunks."
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Error processing document: {str(e)}"
            }
    
    def query_documents(self, query: str, n_results: int = 5) -> List[Dict]:
        """
        Query the vector database for relevant document chunks.
        
        Args:
            query: Search query
            n_results: Number of results to return
            
        Returns:
            List of relevant document chunks with metadata
        """
        try:
            # Generate query embedding
            query_embedding = self.embeddings.embed_query(query)
            
            # Query ChromaDB
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results
            )
            
            # Format results
            formatted_results = []
            if results['documents'] and results['documents'][0]:
                for i, doc in enumerate(results['documents'][0]):
                    formatted_results.append({
                        "content": doc,
                        "metadata": results['metadatas'][0][i] if results['metadatas'] else {},
                        "distance": results['distances'][0][i] if results.get('distances') else None
                    })
            
            return formatted_results
            
        except Exception as e:
            raise Exception(f"Error querying documents: {str(e)}")
    
    def get_collection_stats(self) -> Dict:
        """
        Get statistics about the document collection.
        
        Returns:
            Dictionary with collection statistics
        """
        try:
            count = self.collection.count()
            
            # Get unique sources
            if count > 0:
                all_metadata = self.collection.get()
                sources = set()
                if all_metadata['metadatas']:
                    for metadata in all_metadata['metadatas']:
                        if 'source' in metadata:
                            sources.add(metadata['source'])
                
                return {
                    "total_chunks": count,
                    "unique_documents": len(sources),
                    "documents": list(sources)
                }
            else:
                return {
                    "total_chunks": 0,
                    "unique_documents": 0,
                    "documents": []
                }
        except Exception as e:
            return {
                "total_chunks": 0,
                "unique_documents": 0,
                "documents": [],
                "error": str(e)
            }
    
    def clear_collection(self):
        """Clear all documents from the collection."""
        try:
            # Delete the collection
            self.chroma_client.delete_collection(name="kyc_documents")
            
            # Recreate empty collection
            self.collection = self.chroma_client.create_collection(
                name="kyc_documents",
                metadata={"description": "KYC/AML regulatory documents"}
            )
            
            return {"success": True, "message": "Database cleared successfully."}
        except Exception as e:
            return {"success": False, "error": f"Error clearing database: {str(e)}"}
