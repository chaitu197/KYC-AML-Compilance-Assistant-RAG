"""
Quick Test Script for KYC/AML RAG Chatbot
Run this to verify the basic functionality without starting the full Streamlit app.
"""

import os
import sys

def test_imports():
    """Test if all required packages can be imported."""
    print("Testing imports...")
    try:
        import streamlit
        print("✓ Streamlit")
    except ImportError as e:
        print(f"✗ Streamlit: {e}")
        return False
    
    try:
        import langchain
        print("✓ LangChain")
    except ImportError as e:
        print(f"✗ LangChain: {e}")
        return False
    
    try:
        import chromadb
        print("✓ ChromaDB")
    except ImportError as e:
        print(f"✗ ChromaDB: {e}")
        return False
    
    try:
        import google.generativeai
        print("✓ Google Generative AI")
    except ImportError as e:
        print(f"✗ Google Generative AI: {e}")
        return False
    
    try:
        from pypdf import PdfReader
        print("✓ PyPDF")
    except ImportError as e:
        print(f"✗ PyPDF: {e}")
        return False
    
    try:
        from sentence_transformers import SentenceTransformer
        print("✓ Sentence Transformers")
    except ImportError as e:
        print(f"✗ Sentence Transformers: {e}")
        return False
    
    print("\n✅ All imports successful!\n")
    return True


def test_document_files():
    """Test if sample documents exist."""
    print("Testing sample documents...")
    docs_dir = "./documents"
    
    if not os.path.exists(docs_dir):
        print(f"✗ Documents directory not found: {docs_dir}")
        return False
    
    expected_docs = [
        "sample_rbi_aml.txt",
        "sample_fatf.txt",
        "sample_sebi.txt",
        "sample_gdpr.txt"
    ]
    
    all_found = True
    for doc in expected_docs:
        doc_path = os.path.join(docs_dir, doc)
        if os.path.exists(doc_path):
            size = os.path.getsize(doc_path)
            print(f"✓ {doc} ({size:,} bytes)")
        else:
            print(f"✗ {doc} not found")
            all_found = False
    
    if all_found:
        print("\n✅ All sample documents found!\n")
    return all_found


def test_api_key():
    """Test if API key is configured."""
    print("Testing API key configuration...")
    
    from dotenv import load_dotenv
    load_dotenv()
    
    api_key = os.getenv("GOOGLE_API_KEY")
    
    if api_key and api_key != "your_google_api_key_here":
        print(f"✓ API key configured (length: {len(api_key)})")
        print("\n✅ API key is set!\n")
        return True
    else:
        print("✗ API key not configured")
        print("\nPlease set your GOOGLE_API_KEY in the .env file")
        print("Get your key from: https://makersuite.google.com/app/apikey\n")
        return False


def test_module_imports():
    """Test if custom modules can be imported."""
    print("Testing custom modules...")
    
    try:
        from document_processor import DocumentProcessor
        print("✓ document_processor.py")
    except ImportError as e:
        print(f"✗ document_processor.py: {e}")
        return False
    
    try:
        from rag_engine import RAGEngine
        print("✓ rag_engine.py")
    except ImportError as e:
        print(f"✗ rag_engine.py: {e}")
        return False
    
    print("\n✅ All custom modules can be imported!\n")
    return True


def main():
    """Run all tests."""
    print("=" * 60)
    print("KYC/AML RAG Chatbot - System Test")
    print("=" * 60)
    print()
    
    results = []
    
    # Test imports
    results.append(("Package Imports", test_imports()))
    
    # Test documents
    results.append(("Sample Documents", test_document_files()))
    
    # Test API key
    results.append(("API Key", test_api_key()))
    
    # Test custom modules (only if imports work)
    if results[0][1]:
        results.append(("Custom Modules", test_module_imports()))
    
    # Summary
    print("=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{test_name:.<40} {status}")
    
    print()
    
    all_passed = all(result[1] for result in results)
    
    if all_passed:
        print("🎉 All tests passed! You can now run: streamlit run app.py")
    else:
        print("⚠️  Some tests failed. Please fix the issues above.")
        print("\nTo install dependencies, run:")
        print("  pip3 install -r requirements.txt")
    
    print()


if __name__ == "__main__":
    main()
