"""
KYC/AML Compliance RAG Chatbot
Streamlit web application for querying regulatory documents.
"""

import streamlit as st
import os
from dotenv import load_dotenv
from rag_engine import RAGEngine
import tempfile

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="KYC/AML Compliance Assistant",
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
    .stAlert {
        margin-top: 1rem;
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


def initialize_session_state():
    """Initialize Streamlit session state variables."""
    if 'rag_engine' not in st.session_state:
        st.session_state.rag_engine = None
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'documents_loaded' not in st.session_state:
        st.session_state.documents_loaded = False
    if 'api_key_set' not in st.session_state:
        st.session_state.api_key_set = False


def initialize_rag_engine(api_key: str):
    """Initialize the RAG engine with API key."""
    try:
        st.session_state.rag_engine = RAGEngine(api_key)
        st.session_state.api_key_set = True
        return True
    except Exception as e:
        st.error(f"Error initializing RAG engine: {str(e)}")
        return False


def load_sample_documents():
    """Load sample regulatory documents."""
    if st.session_state.rag_engine is None:
        st.error("Please set your API key first.")
        return
    
    with st.spinner("Loading sample documents..."):
        result = st.session_state.rag_engine.process_sample_documents()
        
        if result.get("success"):
            st.success(f"✅ Loaded {len(result['processed'])} documents with {result['total_chunks']} chunks")
            st.session_state.documents_loaded = True
            
            with st.expander("📄 Loaded Documents"):
                for doc in result['processed']:
                    st.write(f"• {doc}")
        else:
            st.error("Failed to load sample documents")
            if result.get("failed"):
                for failure in result['failed']:
                    st.error(f"• {failure['filename']}: {failure['error']}")


def process_uploaded_file(uploaded_file):
    """Process an uploaded file."""
    if st.session_state.rag_engine is None:
        st.error("Please set your API key first.")
        return
    
    # Save uploaded file temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as tmp_file:
        tmp_file.write(uploaded_file.getvalue())
        tmp_path = tmp_file.name
    
    try:
        with st.spinner(f"Processing {uploaded_file.name}..."):
            result = st.session_state.rag_engine.doc_processor.process_document(
                tmp_path, 
                uploaded_file.name
            )
            
            if result.get("success"):
                st.success(f"✅ {result['message']}")
                st.session_state.documents_loaded = True
            else:
                st.error(f"❌ {result.get('error', 'Unknown error')}")
    finally:
        # Clean up temporary file
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)


def display_chat_message(role: str, content: str, sources: list = None):
    """Display a chat message with optional sources."""
    if role == "user":
        st.markdown(f"""
            <div class="chat-message user-message">
                <strong>🧑 You:</strong><br>
                {content}
            </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
            <div class="chat-message assistant-message">
                <strong>🤖 Assistant:</strong><br>
                {content}
            </div>
        """, unsafe_allow_html=True)
        
        if sources:
            with st.expander("📚 Sources", expanded=False):
                for source in sources:
                    st.markdown(f"""
                        <div class="source-box">
                            📄 {source['filename']}
                        </div>
                    """, unsafe_allow_html=True)


def main():
    """Main application function."""
    initialize_session_state()
    
    # Header
    st.title("🔍 KYC/AML Compliance Assistant")
    st.markdown("Ask questions about KYC and AML compliance regulations")
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # API Key input
        api_key = st.text_input(
            "Google API Key",
            type="password",
            value=os.getenv("GOOGLE_API_KEY", ""),
            help="Enter your Google API key from https://makersuite.google.com/app/apikey"
        )
        
        if api_key and not st.session_state.api_key_set:
            if st.button("Set API Key"):
                if initialize_rag_engine(api_key):
                    st.success("✅ API Key set successfully!")
                    st.rerun()
        
        if st.session_state.api_key_set:
            st.success("✅ API Key configured")
        
        st.divider()
        
        # Document Management
        st.header("📚 Document Management")
        
        # Load sample documents
        if st.button("Load Sample Documents", disabled=not st.session_state.api_key_set):
            load_sample_documents()
        
        # File upload
        st.subheader("Upload Documents")
        uploaded_file = st.file_uploader(
            "Upload PDF or TXT",
            type=['pdf', 'txt'],
            disabled=not st.session_state.api_key_set
        )
        
        if uploaded_file is not None:
            if st.button("Process Upload"):
                process_uploaded_file(uploaded_file)
        
        st.divider()
        
        # Database stats
        if st.session_state.rag_engine:
            st.subheader("📊 Database Stats")
            stats = st.session_state.rag_engine.get_database_stats()
            st.metric("Total Chunks", stats.get("total_chunks", 0))
            st.metric("Documents", stats.get("unique_documents", 0))
            
            if stats.get("documents"):
                with st.expander("View Documents"):
                    for doc in stats["documents"]:
                        st.write(f"• {doc}")
            
            # Clear database
            if st.button("🗑️ Clear Database", type="secondary"):
                if st.session_state.rag_engine.clear_database().get("success"):
                    st.success("Database cleared!")
                    st.session_state.chat_history = []
                    st.session_state.documents_loaded = False
                    st.rerun()
        
        st.divider()
        
        # Example queries
        st.subheader("💡 Example Queries")
        st.markdown("""
        - What documents are required for merchant KYC?
        - Define AML red-flag transaction detection
        - What are FATF recommendations for customer due diligence?
        - What are GDPR requirements for KYC data retention?
        - What is beneficial ownership identification?
        - What are the penalties for KYC non-compliance?
        """)
    
    # Main chat interface
    if not st.session_state.api_key_set:
        st.info("👈 Please set your Google API key in the sidebar to get started.")
        return
    
    if not st.session_state.documents_loaded:
        st.info("👈 Please load sample documents or upload your own documents to begin.")
        return
    
    # Display chat history
    for message in st.session_state.chat_history:
        display_chat_message("user", message["query"])
        display_chat_message("assistant", message["answer"], message.get("sources"))
    
    # Chat input
    query = st.chat_input("Ask a question about KYC/AML compliance...")
    
    if query:
        # Add user message to history
        st.session_state.chat_history.append({
            "query": query,
            "answer": "",
            "sources": []
        })
        
        # Display user message
        display_chat_message("user", query)
        
        # Generate answer
        with st.spinner("Thinking..."):
            result = st.session_state.rag_engine.generate_answer(query)
            
            if result.get("success"):
                answer = result["answer"]
                sources = result.get("sources", [])
                
                # Update chat history
                st.session_state.chat_history[-1]["answer"] = answer
                st.session_state.chat_history[-1]["sources"] = sources
                
                # Display assistant message
                display_chat_message("assistant", answer, sources)
            else:
                error_msg = result.get("answer", "An error occurred")
                st.session_state.chat_history[-1]["answer"] = error_msg
                display_chat_message("assistant", error_msg)
    
    # Clear chat button
    if st.session_state.chat_history:
        if st.button("🗑️ Clear Chat History"):
            st.session_state.chat_history = []
            if st.session_state.rag_engine:
                st.session_state.rag_engine.clear_conversation_history()
            st.rerun()


if __name__ == "__main__":
    main()
