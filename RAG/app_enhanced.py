"""
KYC/AML Compliance RAG Chatbot - ENHANCED VERSION
Professional features: detailed sources, confidence scores, export, branding
"""

import streamlit as st
import os
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.config import Settings
import hashlib
import tempfile
from langchain.text_splitter import RecursiveCharacterTextSplitter
from datetime import datetime
import json
from multi_format_processor import extract_text_from_file, get_supported_formats, get_format_description

# Import production modules
from risk_scoring import analyze_query_risk, calculate_transaction_risk
from audit_logger import AuditLogger
from performance_monitor import PerformanceMonitor, TimingContext
from compliance_dashboard import ComplianceDashboard
import time

# Page configuration
st.set_page_config(
    page_title="KYC/AML Compliance Assistant",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS - Visa Branded Professional Design
st.markdown("""
    <style>
    /* Visa Color Palette */
    :root {
        --visa-blue: #1A1F71;
        --visa-gold: #F7B600;
        --visa-light-blue: #2C3E95;
        --visa-dark: #0D1136;
        --success-green: #00D084;
        --warning-yellow: #FFD700;
        --danger-red: #FF4B4B;
    }
    
    /* Main Layout */
    .main {
        padding: 1rem 2rem;
        background: linear-gradient(135deg, #0D1136 0%, #1A1F71 100%);
    }
    
    /* Header Styling */
    .stApp header {
        background-color: var(--visa-blue);
    }
    
    /* Visa Branded Header */
    .visa-header {
        background: linear-gradient(90deg, #1A1F71 0%, #2C3E95 100%);
        padding: 2rem;
        border-radius: 1rem;
        margin-bottom: 2rem;
        border: 2px solid #F7B600;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
    
    .visa-title {
        color: #F7B600;
        font-size: 2.5rem;
        font-weight: 800;
        margin: 0;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
    }
    
    .visa-subtitle {
        color: #FFFFFF;
        font-size: 1.1rem;
        margin-top: 0.5rem;
        opacity: 0.9;
    }
    
    /* Metric Cards */
    .metric-card {
        background: linear-gradient(135deg, #1A1F71 0%, #2C3E95 100%);
        padding: 1.5rem;
        border-radius: 0.8rem;
        border-left: 4px solid #F7B600;
        margin: 0.5rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.2);
    }
    
    .metric-value {
        font-size: 2rem;
        font-weight: bold;
        color: #F7B600;
    }
    
    .metric-label {
        color: #FFFFFF;
        opacity: 0.8;
        font-size: 0.9rem;
        margin-top: 0.3rem;
    }
    
    /* Chat Messages */
    .chat-message {
        padding: 1.2rem;
        border-radius: 0.8rem;
        margin: 1rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.2);
    }
    
    .user-message {
        background: linear-gradient(135deg, #2C3E95 0%, #1A1F71 100%);
        border-left: 4px solid #F7B600;
    }
    
    .assistant-message {
        background: linear-gradient(135deg, #1A1F71 0%, #0D1136 100%);
        border-left: 4px solid #00D084;
    }
    
    /* Risk Score Badges */
    .risk-badge {
        display: inline-block;
        padding: 0.5rem 1rem;
        border-radius: 2rem;
        font-weight: bold;
        font-size: 0.95rem;
        margin: 0.5rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.3);
    }
    
    .risk-high {
        background: linear-gradient(135deg, #FF4B4B 0%, #CC0000 100%);
        color: white;
    }
    
    .risk-medium {
        background: linear-gradient(135deg, #FFD700 0%, #FFA500 100%);
        color: #000;
    }
    
    .risk-low {
        background: linear-gradient(135deg, #00D084 0%, #00A86B 100%);
        color: white;
    }
    
    /* Confidence Badges */
    .confidence-badge {
        display: inline-block;
        padding: 0.4rem 0.9rem;
        border-radius: 1.5rem;
        font-weight: 600;
        margin: 0.5rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.2);
    }
    
    .confidence-high {
        background: linear-gradient(135deg, #00D084 0%, #00A86B 100%);
        color: white;
    }
    
    .confidence-medium {
        background: linear-gradient(135deg, #FFD700 0%, #FFA500 100%);
        color: #000;
    }
    
    .confidence-low {
        background: linear-gradient(135deg, #FF4B4B 0%, #CC0000 100%);
        color: white;
    }
    
    /* Source Boxes */
    .source-box {
        background: linear-gradient(135deg, #1A1F71 0%, #2C3E95 100%);
        padding: 1rem;
        border-radius: 0.6rem;
        margin: 0.8rem 0;
        border-left: 4px solid #F7B600;
        box-shadow: 0 2px 4px rgba(0,0,0,0.2);
    }
    
    .source-snippet {
        background-color: rgba(0,0,0,0.3);
        padding: 0.8rem;
        border-radius: 0.4rem;
        font-family: 'Courier New', monospace;
        font-size: 0.85em;
        margin-top: 0.5rem;
        border-left: 3px solid #00D084;
        color: #E0E0E0;
    }
    
    /* Prompt Box */
    .prompt-box {
        background: linear-gradient(135deg, #0D1136 0%, #1A1F71 100%);
        padding: 1rem;
        border-radius: 0.6rem;
        border-left: 4px solid #9B59B6;
        font-family: 'Courier New', monospace;
        font-size: 0.85em;
        white-space: pre-wrap;
        max-height: 400px;
        overflow-y: auto;
        box-shadow: 0 2px 4px rgba(0,0,0,0.2);
    }
    
    /* Buttons */
    .stButton>button {
        background: linear-gradient(135deg, #F7B600 0%, #FFA500 100%);
        color: #1A1F71;
        font-weight: bold;
        border: none;
        border-radius: 0.5rem;
        padding: 0.6rem 1.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.2);
        transition: all 0.3s ease;
    }
    
    .stButton>button:hover {
        background: linear-gradient(135deg, #FFD700 0%, #F7B600 100%);
        box-shadow: 0 4px 8px rgba(0,0,0,0.3);
        transform: translateY(-2px);
    }
    
    /* Sidebar */
    .css-1d391kg {
        background: linear-gradient(180deg, #1A1F71 0%, #0D1136 100%);
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background-color: rgba(26, 31, 113, 0.3);
        border-radius: 0.5rem;
        border-left: 3px solid #F7B600;
    }
    
    /* Info Box */
    .info-box {
        background: linear-gradient(135deg, #2C3E95 0%, #1A1F71 100%);
        padding: 1rem;
        border-radius: 0.6rem;
        border-left: 4px solid #00D084;
        margin: 1rem 0;
    }
    
    /* Alert Box */
    .alert-box {
        background: linear-gradient(135deg, #FF4B4B 0%, #CC0000 100%);
        padding: 1rem;
        border-radius: 0.6rem;
        color: white;
        margin: 1rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.3);
    }
    
    /* Performance Metrics */
    .perf-metric {
        display: inline-block;
        background: rgba(247, 182, 0, 0.2);
        padding: 0.3rem 0.8rem;
        border-radius: 1rem;
        font-size: 0.85rem;
        margin: 0.2rem;
        border: 1px solid #F7B600;
    }
    
    /* Scrollbar */
    ::-webkit-scrollbar {
        width: 10px;
    }
    
    ::-webkit-scrollbar-track {
        background: #0D1136;
    }
    
    ::-webkit-scrollbar-thumb {
        background: #F7B600;
        border-radius: 5px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #FFD700;
    }
    </style>
""", unsafe_allow_html=True)


@st.cache_resource
def load_embedding_model():
    """Load the local embedding model."""
    return SentenceTransformer('all-MiniLM-L6-v2')


def initialize_chroma():
    """Initialize ChromaDB."""
    client = chromadb.PersistentClient(
        path="./chroma_db_enhanced",
        settings=Settings(anonymized_telemetry=False)
    )
    try:
        collection = client.get_collection(name="kyc_documents_enhanced")
    except:
        collection = client.create_collection(
            name="kyc_documents_enhanced",
            metadata={"description": "KYC/AML regulatory documents"}
        )
    return client, collection


def extract_text_from_file_wrapper(file_path):
    """Extract text from any supported file format."""
    return extract_text_from_file(file_path)


def process_document(file_path, filename, embedding_model, collection):
    """Process and index a document."""
    try:
        text = extract_text_from_file_wrapper(file_path)
        
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len
        )
        chunks = text_splitter.split_text(text)
        
        if not chunks:
            return {"success": False, "error": "No text extracted"}
        
        embeddings = embedding_model.encode(chunks).tolist()
        
        doc_hash = hashlib.md5(filename.encode()).hexdigest()[:8]
        ids = [f"{doc_hash}_chunk_{i}" for i in range(len(chunks))]
        
        metadatas = [
            {
                "source": filename,
                "chunk_index": i,
                "total_chunks": len(chunks),
                "chunk_text": chunks[i][:200]  # Store snippet for display
            }
            for i in range(len(chunks))
        ]
        
        collection.add(
            embeddings=embeddings,
            documents=chunks,
            metadatas=metadatas,
            ids=ids
        )
        
        return {
            "success": True,
            "filename": filename,
            "chunks_created": len(chunks)
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def query_documents(query, embedding_model, collection, n_results=5):
    """Query the document collection with similarity scores."""
    query_embedding = embedding_model.encode([query]).tolist()
    results = collection.query(
        query_embeddings=query_embedding,
        n_results=n_results
    )
    
    formatted_results = []
    if results['documents'] and results['documents'][0]:
        for i, doc in enumerate(results['documents'][0]):
            # Calculate similarity score (ChromaDB returns distance, convert to similarity)
            distance = results['distances'][0][i] if results.get('distances') else 1.0
            similarity = 1 / (1 + distance)  # Convert distance to similarity (0-1)
            
            formatted_results.append({
                "content": doc,
                "metadata": results['metadatas'][0][i] if results['metadatas'] else {},
                "distance": distance,
                "similarity": similarity
            })
    
    return formatted_results


def create_prompt(query, context_chunks):
    """Create prompt for LLM (or display purposes)."""
    context_text = "\n\n".join([
        f"[Source: {chunk['metadata'].get('source', 'Unknown')}, Chunk {chunk['metadata'].get('chunk_index', 0)}]\n{chunk['content']}"
        for chunk in context_chunks
    ])
    
    prompt = f"""You are a compliance expert. Using ONLY the content below, answer the question.

CONTEXT FROM DOCUMENTS:
{context_text}

USER QUESTION:
{query}

INSTRUCTIONS:
1. Answer based ONLY on the context provided above
2. Be specific and cite relevant regulations
3. If context doesn't contain enough information, acknowledge this
4. Use clear, professional language
5. Organize with bullet points when appropriate

ANSWER:"""
    
    return prompt


def generate_answer_enhanced(query, context_chunks):
    """Generate enhanced answer with comprehensive details and metadata."""
    if not context_chunks:
        return {
            "answer": "No relevant information found in the documents. Please upload relevant regulatory documents first.",
            "sources": [],
            "avg_confidence": 0.0,
            "prompt": ""
        }
    
    # Create prompt
    prompt = create_prompt(query, context_chunks)
    
    # Generate comprehensive answer from top chunks
    answer = "# 📋 Comprehensive Answer\n\n"
    
    # Add executive summary
    answer += "## Executive Summary\n\n"
    answer += f"Based on analysis of **{len(context_chunks)} relevant document sections** from regulatory sources, here is a detailed response to your query:\n\n"
    
    # Add main content from chunks
    answer += "## Detailed Explanation\n\n"
    
    for i, chunk in enumerate(context_chunks[:5], 1):  # Use top 5 chunks
        source = chunk['metadata'].get('source', 'Unknown')
        chunk_idx = chunk['metadata'].get('chunk_index', 0)
        content = chunk['content']
        
        # Add section header
        answer += f"### {i}. From {source} (Section {chunk_idx})\n\n"
        
        # Add full content
        answer += f"{content}\n\n"
        
        # Add separator
        if i < len(context_chunks[:5]):
            answer += "---\n\n"
    
    # Add key points summary
    answer += "## 📌 Key Points Summary\n\n"
    answer += "Based on the regulatory documents:\n\n"
    
    # Extract key points from first 3 chunks
    for i, chunk in enumerate(context_chunks[:3], 1):
        # Get first sentence or first 150 chars as key point
        content = chunk['content']
        sentences = content.split('.')
        key_point = sentences[0] if sentences else content[:150]
        answer += f"{i}. {key_point.strip()}.\n"
    
    answer += "\n"
    
    # Add regulatory context
    answer += "## 📚 Regulatory Context\n\n"
    sources_list = list(set([c['metadata'].get('source', 'Unknown') for c in context_chunks]))
    answer += f"This information is sourced from **{len(sources_list)} regulatory document(s)**:\n\n"
    for src in sources_list:
        answer += f"- 📄 {src}\n"
    
    answer += "\n"
    
    # Add compliance notes
    answer += "## ⚠️ Compliance Notes\n\n"
    answer += "- This information is extracted from official regulatory documents\n"
    answer += "- Always verify with the latest version of regulations\n"
    answer += "- Consult legal/compliance team for specific implementation\n"
    answer += "- Regulations may vary by jurisdiction and change over time\n\n"
    
    # Add next steps
    answer += "## 🎯 Recommended Next Steps\n\n"
    answer += "1. Review the complete source documents for full context\n"
    answer += "2. Verify current applicability to your specific situation\n"
    answer += "3. Consult with compliance officers for implementation guidance\n"
    answer += "4. Check for any recent regulatory updates\n\n"
    
    # Add note about AI-generated content
    answer += "---\n\n"
    answer += "*💡 Note: This is a RAG-based response using local embeddings. For AI-generated summaries, integrate an LLM (OpenAI, Ollama, etc.)*\n"
    
    # Extract sources with snippets
    sources = []
    seen_sources = set()
    for chunk in context_chunks:
        source = chunk['metadata'].get('source', 'Unknown')
        if source not in seen_sources:
            sources.append({
                "filename": source,
                "chunk_index": chunk['metadata'].get('chunk_index', 0),
                "snippet": chunk['content'][:300] + "...",  # Longer snippet
                "similarity": chunk.get('similarity', 0.0)
            })
            seen_sources.add(source)
    
    # Calculate average confidence
    avg_confidence = sum(s['similarity'] for s in sources) / len(sources) if sources else 0.0
    
    return {
        "answer": answer,
        "sources": sources,
        "avg_confidence": avg_confidence,
        "prompt": prompt
    }


def export_chat_history(chat_history):
    """Export chat history as markdown."""
    export_text = f"""# KYC/AML Compliance Chat Export
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

"""
    
    for i, msg in enumerate(chat_history, 1):
        export_text += f"## Query {i}\n\n"
        export_text += f"**Question:** {msg['query']}\n\n"
        export_text += f"**Answer:**\n{msg['answer']}\n\n"
        
        if msg.get('sources'):
            export_text += f"**Sources:**\n"
            for src in msg['sources']:
                export_text += f"- 📄 {src['filename']} (Chunk {src.get('chunk_index', 0)})\n"
                if 'snippet' in src:
                    export_text += f"  > \"{src['snippet']}\"\n"
                if 'similarity' in src:
                    export_text += f"  > Relevance: {src['similarity']:.2f}\n"
            export_text += "\n"
        
        export_text += "---\n\n"
    
    return export_text


def get_confidence_badge(score):
    """Get HTML badge for confidence score."""
    if score >= 0.7:
        return f'<span class="confidence-badge confidence-high">🔍 Relevance: {score:.2f} (High)</span>'
    elif score >= 0.4:
        return f'<span class="confidence-badge confidence-medium">🔍 Relevance: {score:.2f} (Medium)</span>'
    else:
        return f'<span class="confidence-badge confidence-low">🔍 Relevance: {score:.2f} (Low)</span>'


def main():
    """Main application."""
    
    # Visa Branded Header
    st.markdown("""
        <div class="visa-header">
            <h1 class="visa-title">🔐 KYC/AML Compliance Assistant</h1>
            <p class="visa-subtitle">
                <strong>Enterprise RAG System</strong> | Powered by AI | Locally Hosted | Production-Ready
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    # Initialize
    if 'embedding_model' not in st.session_state:
        with st.spinner("Loading embedding model..."):
            st.session_state.embedding_model = load_embedding_model()
            st.session_state.chroma_client, st.session_state.collection = initialize_chroma()
    
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    
    # Initialize production modules
    if 'audit_logger' not in st.session_state:
        st.session_state.audit_logger = AuditLogger()
    
    if 'performance_monitor' not in st.session_state:
        st.session_state.performance_monitor = PerformanceMonitor()
    
    if 'compliance_dashboard' not in st.session_state:
        st.session_state.compliance_dashboard = ComplianceDashboard(
            st.session_state.collection,
            st.session_state.audit_logger
        )
    
    # Sidebar
    with st.sidebar:
        # About Section
        with st.expander("ℹ️ About This App", expanded=False):
            st.markdown("""
            This **AI-powered KYC/AML Compliance Assistant** uses **RAG (Retrieval-Augmented Generation)** to answer questions based on uploaded regulatory documents like:
            
            - 📄 RBI KYC Guidelines
            - 📄 SEBI Regulations
            - 📄 FATF Standards
            - 📄 GDPR Requirements
            
            **💡 Built with:**
            - Streamlit (UI)
            - sentence-transformers (Embeddings)
            - ChromaDB (Vector Database)
            - LangChain (RAG Framework)
            
            **🔒 Privacy:** All processing happens locally on your machine.
            """)
        
        st.divider()
        
        # System Information
        st.subheader("⚙️ System Information")
        
        chunk_count = st.session_state.collection.count()
        
        system_info = {
            "Embedding Model": "all-MiniLM-L6-v2",
            "Vector Database": "ChromaDB",
            "Chunk Size": "1000 characters",
            "Chunk Overlap": "200 characters",
            "Total Chunks": str(chunk_count),
            "Search Type": "Semantic (Cosine)"
        }
        
        for key, value in system_info.items():
            col1, col2 = st.columns([1, 1])
            with col1:
                st.markdown(f"**{key}:**")
            with col2:
                st.markdown(value)
        
        st.divider()
        
        # Document Management
        st.subheader("📚 Document Management")
        
        if st.button("📥 Load Sample Documents"):
            with st.spinner("Processing documents..."):
                docs_dir = "./documents"
                if os.path.exists(docs_dir):
                    processed = []
                    total_chunks = 0
                    supported_exts = tuple(f'.{ext}' for ext in get_supported_formats())
                    for filename in os.listdir(docs_dir):
                        if filename.endswith(supported_exts):
                            file_path = os.path.join(docs_dir, filename)
                            result = process_document(
                                file_path,
                                filename,
                                st.session_state.embedding_model,
                                st.session_state.collection
                            )
                            if result.get("success"):
                                processed.append(filename)
                                total_chunks += result.get("chunks_created", 0)
                    
                    if processed:
                        st.success(f"✅ Loaded {len(processed)} documents ({total_chunks} chunks)")
                        with st.expander("📄 Loaded Documents"):
                            for doc in processed:
                                st.write(f"• {doc}")
        
        # Supported formats info
        with st.expander("📋 Supported Formats", expanded=False):
            formats = get_format_description()
            for fmt, desc in formats.items():
                st.write(f"**{fmt}**: {desc}")
        
        uploaded_file = st.file_uploader(
            "📤 Upload Document", 
            type=get_supported_formats(),
            help="Supports: PDF, DOCX, DOC, TXT, CSV, JSON, HTML, XLSX, XML"
        )
        
        if uploaded_file and st.button("Process Upload"):
            with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as tmp:
                tmp.write(uploaded_file.getvalue())
                tmp_path = tmp.name
            
            result = process_document(
                tmp_path,
                uploaded_file.name,
                st.session_state.embedding_model,
                st.session_state.collection
            )
            
            if result.get("success"):
                st.success(f"✅ Processed {uploaded_file.name}")
            else:
                st.error(f"❌ {result.get('error')}")
            
            os.unlink(tmp_path)
        
        st.divider()
        
        # Export Feature
        st.subheader("📥 Export Chat")
        if st.session_state.chat_history:
            export_data = export_chat_history(st.session_state.chat_history)
            st.download_button(
                label="📄 Download as Markdown",
                data=export_data,
                file_name=f"kyc_aml_chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
                mime="text/markdown"
            )
        else:
            st.info("No chat history to export")
        
        st.divider()
        
        if st.button("🗑️ Clear Database"):
            st.session_state.chroma_client.delete_collection("kyc_documents_enhanced")
            st.session_state.chroma_client, st.session_state.collection = initialize_chroma()
            st.session_state.chat_history = []
            st.success("Database cleared!")
            st.rerun()
    
    # Main content area with tabs
    tab1, tab2, tab3 = st.tabs(["💬 Chat Assistant", "📊 Dashboard", "📈 Performance"])
    
    with tab1:
        # Chat interface
        st.info("💡 Upload regulatory documents and ask compliance questions. All processing happens locally!")
        
        # Display chat history
        for msg in st.session_state.chat_history:
        # User message
        st.markdown(f"""
            <div class="chat-message user-message">
                <strong>🧑 You:</strong><br>{msg['query']}
            </div>
        """, unsafe_allow_html=True)
        
        # Risk score badge (if present)
        if msg.get('risk_score') is not None:
            risk_score = msg['risk_score']
            risk_level = msg.get('risk_level', 'LOW')
            
            if risk_level == 'HIGH':
                risk_color = '#FF4B4B'
                risk_icon = '🚨'
            elif risk_level == 'MEDIUM':
                risk_color = '#FFD700'
                risk_icon = '⚠️'
            else:
                risk_color = '#00D084'
                risk_icon = '✅'
            
            st.markdown(f"""
                <div style="background-color: {risk_color}; color: white; padding: 0.5rem; border-radius: 0.3rem; margin: 0.5rem 0; display: inline-block;">
                    {risk_icon} <strong>Risk Score: {risk_score}/100 ({risk_level})</strong>
                </div>
            """, unsafe_allow_html=True)
            
            if msg.get('risk_flags'):
                st.markdown("**Risk Flags:**")
                for flag in msg['risk_flags']:
                    st.markdown(f"- ⚠️ {flag}")
        
        # Assistant message
        st.markdown(f"""
            <div class="chat-message assistant-message">
                <strong>🤖 Assistant:</strong><br>{msg['answer']}
            </div>
        """, unsafe_allow_html=True)
        
        # Confidence score
        if msg.get('avg_confidence'):
            st.markdown(get_confidence_badge(msg['avg_confidence']), unsafe_allow_html=True)
        
        # Query time (if present)
        if msg.get('query_time'):
            st.markdown(f"<small>⏱️ Response time: {msg['query_time']:.2f}s</small>", unsafe_allow_html=True)
        
        # Sources with snippets
        if msg.get('sources'):
            with st.expander("📚 Source Documents & Snippets", expanded=False):
                for i, src in enumerate(msg['sources'], 1):
                    st.markdown(f"""
                        <div class="source-box">
                            <strong>📄 {src['filename']}</strong> – Chunk {src.get('chunk_index', 0)}
                            <div class="source-snippet">
                                "{src.get('snippet', 'No snippet available')}"
                            </div>
                            <small>Similarity Score: {src.get('similarity', 0):.3f}</small>
                        </div>
                    """, unsafe_allow_html=True)
        
        # Show prompt
        if msg.get('prompt'):
            with st.expander("🔧 Prompt Sent to System", expanded=False):
                st.markdown(f'<div class="prompt-box">{msg["prompt"]}</div>', unsafe_allow_html=True)
    
    # Chat input
    query = st.chat_input("Ask about KYC/AML compliance...")
    
    if query:
        start_time = time.time()
        
        # Analyze query risk
        query_risk = analyze_query_risk(query)
        
        # Query documents with performance tracking
        with TimingContext(st.session_state.performance_monitor, 'search'):
            context_chunks = query_documents(
                query,
                st.session_state.embedding_model,
                st.session_state.collection,
                n_results=5
            )
        
        # Generate enhanced answer
        with TimingContext(st.session_state.performance_monitor, 'llm'):
            result = generate_answer_enhanced(query, context_chunks)
        
        # Record total query time
        total_time = time.time() - start_time
        st.session_state.performance_monitor.record_query_time(total_time)
        
        # Log query to audit trail
        query_id = st.session_state.audit_logger.log_query(
            user_id="demo_user",
            query=query,
            answer=result['answer'],
            sources=result['sources'],
            confidence=result['avg_confidence'],
            risk_score=query_risk['risk_score'],
            metadata={"query_time": total_time}
        )
        
        # Log alert if high risk
        if query_risk['requires_alert']:
            st.session_state.audit_logger.log_alert(
                alert_type="HIGH_RISK_QUERY",
                severity="HIGH",
                message=f"High-risk keywords detected: {', '.join(query_risk['keywords_found'])}",
                query_id=query_id,
                user_id="demo_user"
            )
        
        # Add to history with risk info
        st.session_state.chat_history.append({
            "query": query,
            "answer": result['answer'],
            "sources": result['sources'],
            "avg_confidence": result['avg_confidence'],
            "prompt": result['prompt'],
            "risk_score": query_risk['risk_score'],
            "risk_level": query_risk['risk_level'],
            "risk_flags": query_risk['flags'],
            "query_time": total_time
        })
        
        st.rerun()
    
        # Clear chat
        if st.session_state.chat_history and st.button("🗑️ Clear Chat History"):
            st.session_state.chat_history = []
            st.rerun()
    
    with tab2:
        # Dashboard tab
        st.subheader("📊 Compliance Dashboard")
        
        # Get dashboard metrics
        coverage = st.session_state.compliance_dashboard.get_document_coverage()
        stats = st.session_state.compliance_dashboard.get_query_statistics()
        compliance_score = st.session_state.compliance_dashboard.get_compliance_score()
        
        # Overall compliance score
        score = compliance_score.get('overall_score', 0)
        status = compliance_score.get('status', 'UNKNOWN')
        
        if status == 'EXCELLENT':
            score_color = '#00D084'
        elif status == 'GOOD':
            score_color = '#FFD700'
        else:
            score_color = '#FF4B4B'
        
        st.markdown(f"""
            <div class="metric-card" style="text-align: center;">
                <div class="metric-value" style="font-size: 3rem; color: {score_color};">
                    {score}/100
                </div>
                <div class="metric-label" style="font-size: 1.2rem;">
                    Overall Compliance Score - {status}
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        # Metrics row
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-value">{coverage.get('total_documents', 0)}</div>
                    <div class="metric-label">Documents Loaded</div>
                </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-value">{coverage.get('total_chunks', 0)}</div>
                    <div class="metric-label">Total Chunks</div>
                </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-value">{stats.get('total_queries', 0)}</div>
                    <div class="metric-label">Total Queries</div>
                </div>
            """, unsafe_allow_html=True)
        
        with col4:
            avg_conf = stats.get('avg_confidence_score', 0)
            st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-value">{avg_conf:.2f}</div>
                    <div class="metric-label">Avg Confidence</div>
                </div>
            """, unsafe_allow_html=True)
        
        # Document coverage by regulation
        st.subheader("📚 Document Coverage by Regulation")
        
        coverage_data = coverage.get('coverage_by_regulation', {})
        for reg, count in coverage_data.items():
            if count > 0:
                percentage = min(count, 100)
                st.markdown(f"**{reg}**: {count} chunks")
                st.progress(percentage / 100)
        
        # Recent alerts
        st.subheader("🚨 Recent Alerts")
        alerts = st.session_state.audit_logger.get_alerts(limit=5)
        
        if alerts:
            for alert in alerts:
                severity = alert.get('severity', 'INFO')
                message = alert.get('message', 'No message')
                
                if severity == 'HIGH':
                    st.markdown(f"""
                        <div class="alert-box">
                            🚨 <strong>HIGH:</strong> {message}
                        </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"⚠️ **{severity}**: {message}")
        else:
            st.info("No alerts recorded")
    
    with tab3:
        # Performance tab
        st.subheader("📈 Performance Metrics")
        
        metrics = st.session_state.performance_monitor.get_metrics()
        
        # Performance overview
        col1, col2, col3 = st.columns(3)
        
        with col1:
            uptime = metrics.get('uptime_formatted', '0s')
            st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-value" style="font-size: 1.5rem;">{uptime}</div>
                    <div class="metric-label">System Uptime</div>
                </div>
            """, unsafe_allow_html=True)
        
        with col2:
            qpm = metrics.get('queries_per_minute', 0)
            st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-value" style="font-size: 1.5rem;">{qpm:.1f}</div>
                    <div class="metric-label">Queries/Minute</div>
                </div>
            """, unsafe_allow_html=True)
        
        with col3:
            cache_rate = metrics.get('cache_hit_rate', 0)
            st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-value" style="font-size: 1.5rem;">{cache_rate}%</div>
                    <div class="metric-label">Cache Hit Rate</div>
                </div>
            """, unsafe_allow_html=True)
        
        # Query performance
        if 'query_time' in metrics:
            st.subheader("⚡ Query Performance")
            qt = metrics['query_time']
            
            perf_col1, perf_col2, perf_col3 = st.columns(3)
            
            with perf_col1:
                st.metric("Average", f"{qt['avg']}s")
                st.metric("Median", f"{qt['median']}s")
            
            with perf_col2:
                st.metric("Min", f"{qt['min']}s")
                st.metric("Max", f"{qt['max']}s")
            
            with perf_col3:
                st.metric("P95", f"{qt['p95']}s")
                st.metric("P99", f"{qt['p99']}s")


if __name__ == "__main__":
    main()
