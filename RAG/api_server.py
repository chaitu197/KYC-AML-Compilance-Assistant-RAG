"""
FastAPI Backend for KYC/AML RAG System
Provides REST API endpoints for the React frontend
"""

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import os
import tempfile
from datetime import datetime

# Import existing modules
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.config import Settings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from multi_format_processor import extract_text_from_file
from risk_scoring import analyze_query_risk, calculate_transaction_risk
from audit_logger import AuditLogger
from performance_monitor import PerformanceMonitor
from compliance_dashboard import ComplianceDashboard
import time

# Initialize FastAPI
app = FastAPI(
    title="KYC/AML Compliance API",
    description="REST API for KYC/AML RAG System",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],  # React dev servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global instances
embedding_model = None
chroma_client = None
collection = None
audit_logger = None
performance_monitor = None
compliance_dashboard = None

# Pydantic models
class QueryRequest(BaseModel):
    query: str
    n_results: int = 5

class QueryResponse(BaseModel):
    answer: str
    sources: List[dict]
    confidence: float
    risk_score: int
    risk_level: str
    risk_flags: List[str]
    query_time: float

class DocumentInfo(BaseModel):
    filename: str
    chunks: int
    status: str

class DashboardMetrics(BaseModel):
    compliance_score: float
    total_documents: int
    total_chunks: int
    total_queries: int
    avg_confidence: float

@app.on_event("startup")
async def startup_event():
    """Initialize models and databases on startup."""
    global embedding_model, chroma_client, collection, audit_logger, performance_monitor, compliance_dashboard
    
    print("🚀 Initializing KYC/AML RAG System...")
    
    # Load embedding model
    embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
    print("✅ Embedding model loaded")
    
    # Initialize ChromaDB
    chroma_client = chromadb.Client(Settings(
        persist_directory="./chroma_db_api",
        anonymized_telemetry=False
    ))
    
    try:
        collection = chroma_client.get_collection("kyc_aml_docs")
        print("✅ Existing collection loaded")
    except:
        collection = chroma_client.create_collection(
            name="kyc_aml_docs",
            metadata={"description": "KYC/AML regulatory documents"}
        )
        print("✅ New collection created")
    
    # Initialize production modules
    audit_logger = AuditLogger(log_dir="./audit_logs_api")
    performance_monitor = PerformanceMonitor()
    compliance_dashboard = ComplianceDashboard(collection, audit_logger)
    
    # Load documents from documents folder
    await load_documents_from_folder()
    
    print("✅ System ready!")

async def load_documents_from_folder():
    """Load all documents from the documents/ folder on startup."""
    documents_dir = "./documents"
    
    if not os.path.exists(documents_dir):
        print("⚠️ No documents folder found")
        return
    
    # Get all PDF files
    pdf_files = [f for f in os.listdir(documents_dir) if f.endswith('.pdf')]
    
    if not pdf_files:
        print("⚠️ No PDF documents found in documents/ folder")
        return
    
    print(f"📚 Loading {len(pdf_files)} documents from documents/ folder...")
    
    for filename in pdf_files:
        file_path = os.path.join(documents_dir, filename)
        
        try:
            # Check if already loaded (check if any chunks exist for this file)
            existing = collection.get(where={"source": filename})
            if existing and existing['ids']:
                print(f"   ⏭️  Skipping {filename} (already loaded)")
                continue
            
            # Extract text
            text = extract_text_from_file(file_path)
            
            # Split into chunks
            splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200
            )
            chunks = splitter.split_text(text)
            
            # Generate embeddings and store
            for i, chunk in enumerate(chunks):
                embedding = embedding_model.encode(chunk).tolist()
                collection.add(
                    embeddings=[embedding],
                    documents=[chunk],
                    metadatas=[{
                        "source": filename,
                        "chunk_index": i,
                        "upload_time": datetime.now().isoformat(),
                        "preloaded": True
                    }],
                    ids=[f"{filename}_{i}"]
                )
            
            print(f"   ✅ Loaded {filename} ({len(chunks)} chunks)")
            
        except Exception as e:
            print(f"   ❌ Error loading {filename}: {str(e)}")
    
    print("✅ Document loading complete!")

@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "status": "online",
        "message": "KYC/AML Compliance API",
        "version": "1.0.0"
    }

@app.post("/api/query", response_model=QueryResponse)
async def query_documents(request: QueryRequest):
    """Query the RAG system."""
    start_time = time.time()
    
    try:
        # Analyze query risk
        query_risk = analyze_query_risk(request.query)
        
        # Generate embedding
        query_embedding = embedding_model.encode(request.query).tolist()
        
        # Query ChromaDB
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=request.n_results
        )
        
        # Process results
        context_chunks = []
        if results['documents'] and results['documents'][0]:
            for i, doc in enumerate(results['documents'][0]):
                context_chunks.append({
                    'content': doc,
                    'metadata': results['metadatas'][0][i] if results['metadatas'] else {},
                    'similarity': 1 - results['distances'][0][i] if results['distances'] else 0
                })
        
        # Generate answer
        answer = generate_comprehensive_answer(request.query, context_chunks)
        
        # Extract sources
        sources = []
        seen = set()
        for chunk in context_chunks:
            source = chunk['metadata'].get('source', 'Unknown')
            if source not in seen:
                sources.append({
                    "filename": source,
                    "chunk_index": chunk['metadata'].get('chunk_index', 0),
                    "snippet": chunk['content'][:300],
                    "similarity": chunk.get('similarity', 0)
                })
                seen.add(source)
        
        avg_confidence = sum(s['similarity'] for s in sources) / len(sources) if sources else 0
        
        # Record metrics
        query_time = time.time() - start_time
        performance_monitor.record_query_time(query_time)
        
        # Log to audit
        query_id = audit_logger.log_query(
            user_id="api_user",
            query=request.query,
            answer=answer,
            sources=sources,
            confidence=avg_confidence,
            risk_score=query_risk['risk_score']
        )
        
        # Log alert if high risk
        if query_risk['requires_alert']:
            audit_logger.log_alert(
                alert_type="HIGH_RISK_QUERY",
                severity="HIGH",
                message=f"High-risk keywords: {', '.join(query_risk['keywords_found'])}",
                query_id=query_id
            )
        
        return QueryResponse(
            answer=answer,
            sources=sources,
            confidence=avg_confidence,
            risk_score=query_risk['risk_score'],
            risk_level=query_risk['risk_level'],
            risk_flags=query_risk['flags'],
            query_time=query_time
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/upload")
async def upload_document(file: UploadFile = File(...)):
    """Upload and process a document."""
    try:
        # Save uploaded file
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = tmp.name
        
        # Extract text
        text = extract_text_from_file(tmp_path)
        
        # Split into chunks
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
        chunks = splitter.split_text(text)
        
        # Generate embeddings and store
        for i, chunk in enumerate(chunks):
            embedding = embedding_model.encode(chunk).tolist()
            collection.add(
                embeddings=[embedding],
                documents=[chunk],
                metadatas=[{
                    "source": file.filename,
                    "chunk_index": i,
                    "upload_time": datetime.now().isoformat()
                }],
                ids=[f"{file.filename}_{i}"]
            )
        
        # Log upload
        audit_logger.log_document_upload(
            user_id="api_user",
            filename=file.filename,
            file_size=len(content),
            file_type=file.content_type or "unknown",
            chunks_created=len(chunks)
        )
        
        # Cleanup
        os.unlink(tmp_path)
        
        return {
            "filename": file.filename,
            "chunks": len(chunks),
            "status": "success"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/dashboard", response_model=DashboardMetrics)
async def get_dashboard():
    """Get dashboard metrics."""
    try:
        coverage = compliance_dashboard.get_document_coverage()
        stats = compliance_dashboard.get_query_statistics()
        compliance_score = compliance_dashboard.get_compliance_score()
        
        return DashboardMetrics(
            compliance_score=compliance_score.get('overall_score', 0),
            total_documents=coverage.get('total_documents', 0),
            total_chunks=coverage.get('total_chunks', 0),
            total_queries=stats.get('total_queries', 0),
            avg_confidence=stats.get('avg_confidence_score', 0)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/performance")
async def get_performance():
    """Get performance metrics."""
    try:
        return performance_monitor.get_metrics()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/documents")
async def list_documents():
    """List all uploaded documents."""
    try:
        results = collection.get()
        documents = {}
        
        if results and results.get('metadatas'):
            for metadata in results['metadatas']:
                source = metadata.get('source', 'Unknown')
                if source not in documents:
                    documents[source] = 0
                documents[source] += 1
        
        return {
            "documents": [
                {"filename": name, "chunks": count}
                for name, count in documents.items()
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def generate_comprehensive_answer(query: str, context_chunks: List[dict]) -> str:
    """Generate comprehensive answer from context chunks."""
    if not context_chunks:
        return "No relevant information found. Please upload regulatory documents first."
    
    answer = f"# Answer to: {query}\n\n"
    answer += "## Key Information\n\n"
    
    for i, chunk in enumerate(context_chunks[:3], 1):
        source = chunk['metadata'].get('source', 'Unknown')
        content = chunk['content'][:500]
        answer += f"**{i}. From {source}:**\n{content}...\n\n"
    
    answer += "\n## Sources\n"
    sources = list(set([c['metadata'].get('source', 'Unknown') for c in context_chunks]))
    for src in sources:
        answer += f"- {src}\n"
    
    return answer

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
