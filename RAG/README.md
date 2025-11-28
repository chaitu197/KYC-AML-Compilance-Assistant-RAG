# KYC/AML Compliance RAG Chatbot

A Retrieval-Augmented Generation (RAG) chatbot that answers questions about KYC (Know Your Customer) and AML (Anti-Money Laundering) compliance by querying regulatory documents from RBI, FATF, SEBI, and GDPR.

## Features

- 📄 **Document Upload**: Upload PDF or text files containing regulatory documents
- 🔍 **Intelligent Search**: Semantic search across all uploaded documents
- 💬 **Interactive Chat**: Ask questions in natural language
- 📚 **Source Citations**: Get answers with references to source documents
- 🗄️ **Vector Database**: Persistent storage using ChromaDB
- 🎯 **Pre-loaded Samples**: Includes sample regulatory documents for testing

## Sample Documents Included

- **RBI AML Guidelines**: Merchant KYC requirements and red-flag transaction detection
- **FATF Recommendations**: Customer due diligence and international AML standards
- **SEBI Compliance**: KYC norms for securities market participants
- **GDPR Requirements**: Data protection requirements for KYC processes

## Installation

1. **Clone or download this repository**

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Set up your Google API key**:
   - Get your API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
   - Create a `.env` file in the project root:
   ```bash
   cp .env.example .env
   ```
   - Edit `.env` and add your API key:
   ```
   GOOGLE_API_KEY=your_actual_api_key_here
   ```

## Usage

1. **Start the application**:
```bash
streamlit run app.py
```

2. **Configure API Key**:
   - Enter your Google API key in the sidebar
   - Click "Set API Key"

3. **Load Documents**:
   - Click "Load Sample Documents" to load the pre-included regulatory documents
   - Or upload your own PDF/TXT files using the file uploader

4. **Ask Questions**:
   - Type your question in the chat input
   - Get answers with source citations

## Example Questions

- "What documents are required for merchant KYC?"
- "Define AML red-flag transaction detection"
- "What are FATF recommendations for customer due diligence?"
- "What are GDPR requirements for KYC data retention?"
- "What is beneficial ownership identification?"
- "What are the penalties for KYC non-compliance under SEBI?"

## Architecture

### Components

1. **Document Processor** (`document_processor.py`)
   - Extracts text from PDF and TXT files
   - Chunks documents for optimal retrieval
   - Generates embeddings using Google's embedding model
   - Stores vectors in ChromaDB

2. **RAG Engine** (`rag_engine.py`)
   - Processes user queries
   - Retrieves relevant context from vector database
   - Generates answers using Google Gemini
   - Manages conversation history

3. **Streamlit App** (`app.py`)
   - Web-based user interface
   - Document management
   - Interactive chat interface
   - Database statistics and controls

### Technology Stack

- **LLM**: Google Gemini Pro
- **Embeddings**: Google Generative AI Embeddings
- **Vector Database**: ChromaDB
- **Framework**: LangChain
- **UI**: Streamlit
- **Document Processing**: PyPDF

## Project Structure

```
RAG/
├── app.py                      # Streamlit web application
├── document_processor.py       # Document ingestion and vectorization
├── rag_engine.py              # RAG pipeline and answer generation
├── requirements.txt           # Python dependencies
├── .env.example              # Environment variable template
├── .gitignore                # Git ignore patterns
├── .streamlit/
│   └── config.toml           # Streamlit configuration
├── documents/                # Sample regulatory documents
│   ├── sample_rbi_aml.txt
│   ├── sample_fatf.txt
│   ├── sample_sebi.txt
│   └── sample_gdpr.txt
└── chroma_db/                # Vector database (created automatically)
```

## Configuration

### Streamlit Configuration

The `.streamlit/config.toml` file contains UI theming and server settings. You can customize:
- Color scheme
- Font
- Server port
- Other Streamlit options

### Environment Variables

- `GOOGLE_API_KEY`: Your Google API key for Gemini and embeddings

## Database Management

- **View Stats**: Check the sidebar for total chunks and documents
- **Clear Database**: Remove all documents and start fresh
- **Persistent Storage**: Documents are saved in `chroma_db/` directory

## Troubleshooting

### API Key Issues
- Ensure your Google API key is valid and has access to Gemini API
- Check that the `.env` file is in the project root directory

### Document Processing Errors
- Verify PDF files are not password-protected
- Ensure text files are UTF-8 encoded
- Check file size (very large files may take longer to process)

### Import Errors
- Make sure all dependencies are installed: `pip install -r requirements.txt`
- Use Python 3.8 or higher

## Security Notes

- Never commit your `.env` file or API keys to version control
- The `.gitignore` file is configured to exclude sensitive files
- Keep your API keys secure and rotate them regularly

## License

This project is provided as-is for educational and compliance purposes.

## Support

For issues or questions:
1. Check the example queries in the sidebar
2. Review the sample documents in the `documents/` folder
3. Ensure all dependencies are correctly installed
