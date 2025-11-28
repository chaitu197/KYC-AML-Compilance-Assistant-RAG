"""
KYC/AML Compliance RAG Chatbot - LOCAL VERSION
No API key required! Uses local embeddings and Ollama for LLM.
"""

import streamlit as st
import os
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.config import Settings
from pypdf import PdfReader
import hashlib
import tempfile
from langchain.text_splitter import RecursiveCharacterTextSplitter

# Page configuration
st.set_page_config(
    page_title="KYC/AML Compliance Assistant (Local)",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .source-box {
        background-color: #262730;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
        border-left: 3px solid #FF4B4B;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .user-message {
        background-color: #1E1E1E;
        border-left: 3px solid #4B8BFF;
    }
    .assistant-message {
        background-color: #262730;
        border-left: 3px solid #FF4B4B;
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
        path="./chroma_db_local",
        settings=Settings(anonymized_telemetry=False)
    )
    try:
        collection = client.get_collection(name="kyc_documents_local")
    except:
        collection = client.create_collection(
            name="kyc_documents_local",
            metadata={"description": "KYC/AML regulatory documents"}
        )
    return client, collection


def extract_text_from_file(file_path):
    """Extract text from PDF or TXT file."""
    if file_path.lower().endswith('.pdf'):
        reader = PdfReader(file_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        return text
    else:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()


def process_document(file_path, filename, embedding_model, collection):
    """Process and index a document."""
    try:
        # Extract text
        text = extract_text_from_file(file_path)
        
        # Split into chunks
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len
        )
        chunks = text_splitter.split_text(text)
        
        if not chunks:
            return {"success": False, "error": "No text extracted"}
        
        # Generate embeddings
        embeddings = embedding_model.encode(chunks).tolist()
        
        # Create IDs
        doc_hash = hashlib.md5(filename.encode()).hexdigest()[:8]
        ids = [f"{doc_hash}_chunk_{i}" for i in range(len(chunks))]
        
        # Metadata
        metadatas = [
            {"source": filename, "chunk_index": i, "total_chunks": len(chunks)}
            for i in range(len(chunks))
        ]
        
        # Add to ChromaDB
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
    """Query the document collection."""
    query_embedding = embedding_model.encode([query]).tolist()
    results = collection.query(
        query_embeddings=query_embedding,
        n_results=n_results
    )
    
    formatted_results = []
    if results['documents'] and results['documents'][0]:
        for i, doc in enumerate(results['documents'][0]):
            formatted_results.append({
                "content": doc,
                "metadata": results['metadatas'][0][i] if results['metadatas'] else {},
                "distance": results['distances'][0][i] if results.get('distances') else None
            })
    
    return formatted_results


def generate_answer_local(query, context_chunks):
    """Generate answer using simple extraction (no LLM needed for demo)."""
    if not context_chunks:
        return "No relevant information found in the documents."
    
    # Simple answer: combine top chunks
    answer = "Based on the regulatory documents:\n\n"
    for i, chunk in enumerate(context_chunks[:3], 1):
        answer += f"{i}. {chunk['content'][:300]}...\n\n"
    
    answer += "\n💡 **Note**: This is a simplified answer. For AI-generated responses, enable an LLM (OpenAI, Ollama, etc.)"
    
    return answer


def main():
    """Main application."""
    st.title("🔍 KYC/AML Compliance Assistant (Local)")
    st.markdown("**No API key required!** Uses local embeddings.")
    
    # Initialize
    if 'embedding_model' not in st.session_state:
        with st.spinner("Loading embedding model..."):
            st.session_state.embedding_model = load_embedding_model()
            st.session_state.chroma_client, st.session_state.collection = initialize_chroma()
    
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    
    # Sidebar
    with st.sidebar:
        st.header("📚 Document Management")
        
        # Load sample documents
        if st.button("Load Sample Documents"):
            with st.spinner("Processing documents..."):
                docs_dir = "./documents"
                if os.path.exists(docs_dir):
                    processed = []
                    for filename in os.listdir(docs_dir):
                        if filename.endswith(('.txt', '.pdf')):
                            file_path = os.path.join(docs_dir, filename)
                            result = process_document(
                                file_path,
                                filename,
                                st.session_state.embedding_model,
                                st.session_state.collection
                            )
                            if result.get("success"):
                                processed.append(filename)
                    
                    if processed:
                        st.success(f"✅ Loaded {len(processed)} documents")
                        with st.expander("Loaded"):
                            for doc in processed:
                                st.write(f"• {doc}")
        
        # File upload
        st.subheader("Upload Documents")
        uploaded_file = st.file_uploader("Upload PDF or TXT", type=['pdf', 'txt'])
        
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
        
        # Stats
        st.subheader("📊 Database Stats")
        count = st.session_state.collection.count()
        st.metric("Total Chunks", count)
        
        if st.button("🗑️ Clear Database"):
            st.session_state.chroma_client.delete_collection("kyc_documents_local")
            st.session_state.chroma_client, st.session_state.collection = initialize_chroma()
            st.session_state.chat_history = []
            st.success("Database cleared!")
            st.rerun()
    
    # Chat interface
    st.info("💡 This version uses local embeddings - no API key needed! Upload documents and ask questions.")
    
    # Display chat history
    for msg in st.session_state.chat_history:
        st.markdown(f"""
            <div class="chat-message user-message">
                <strong>🧑 You:</strong><br>{msg['query']}
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
            <div class="chat-message assistant-message">
                <strong>🤖 Assistant:</strong><br>{msg['answer']}
            </div>
        """, unsafe_allow_html=True)
        
        if msg.get('sources'):
            with st.expander("📚 Sources"):
                for src in msg['sources']:
                    st.markdown(f"📄 {src['filename']}")
    
    # Chat input
    query = st.chat_input("Ask about KYC/AML compliance...")
    
    if query:
        # Query documents
        context_chunks = query_documents(
            query,
            st.session_state.embedding_model,
            st.session_state.collection
        )
        
        # Generate answer
        answer = generate_answer_local(query, context_chunks)
        
        # Extract sources
        sources = []
        seen = set()
        for chunk in context_chunks:
            src = chunk['metadata'].get('source', 'Unknown')
            if src not in seen:
                sources.append({"filename": src})
                seen.add(src)
        
        # Add to history
        st.session_state.chat_history.append({
            "query": query,
            "answer": answer,
            "sources": sources
        })
        
        st.rerun()
    
    # Clear chat
    if st.session_state.chat_history and st.button("🗑️ Clear Chat"):
        st.session_state.chat_history = []
        st.rerun()


if __name__ == "__main__":
    main()
