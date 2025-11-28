"""
Multi-Format Document Processor
Supports: PDF, TXT, DOCX, DOC, CSV, JSON, HTML, XLSX, XML
"""

import os
from typing import Dict, List
from pypdf import PdfReader
import json
import csv
from io import StringIO


def extract_text_from_pdf(file_path: str) -> str:
    """Extract text from PDF file."""
    reader = PdfReader(file_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
    return text


def extract_text_from_txt(file_path: str) -> str:
    """Extract text from TXT file."""
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        return f.read()


def extract_text_from_docx(file_path: str) -> str:
    """Extract text from DOCX file."""
    try:
        from docx import Document
        doc = Document(file_path)
        text = []
        for paragraph in doc.paragraphs:
            text.append(paragraph.text)
        return '\n'.join(text)
    except ImportError:
        return "Error: python-docx not installed. Run: pip install python-docx"


def extract_text_from_csv(file_path: str) -> str:
    """Extract text from CSV file."""
    try:
        import pandas as pd
        df = pd.read_csv(file_path)
        # Convert DataFrame to readable text
        text = f"CSV Data:\n\n"
        text += df.to_string(index=False)
        return text
    except ImportError:
        # Fallback to basic CSV reading
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            reader = csv.reader(f)
            rows = list(reader)
            return '\n'.join([', '.join(row) for row in rows])


def extract_text_from_json(file_path: str) -> str:
    """Extract text from JSON file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        # Convert JSON to readable text
        return json.dumps(data, indent=2)


def extract_text_from_html(file_path: str) -> str:
    """Extract text from HTML file."""
    try:
        from bs4 import BeautifulSoup
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            soup = BeautifulSoup(f.read(), 'html.parser')
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            text = soup.get_text()
            # Clean up whitespace
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = '\n'.join(chunk for chunk in chunks if chunk)
            return text
    except ImportError:
        return "Error: beautifulsoup4 not installed. Run: pip install beautifulsoup4"


def extract_text_from_xlsx(file_path: str) -> str:
    """Extract text from XLSX file."""
    try:
        import pandas as pd
        # Read all sheets
        excel_file = pd.ExcelFile(file_path)
        text = ""
        for sheet_name in excel_file.sheet_names:
            df = pd.read_excel(file_path, sheet_name=sheet_name)
            text += f"\n\n=== Sheet: {sheet_name} ===\n\n"
            text += df.to_string(index=False)
        return text
    except ImportError:
        return "Error: openpyxl not installed. Run: pip install openpyxl pandas"


def extract_text_from_xml(file_path: str) -> str:
    """Extract text from XML file."""
    try:
        from bs4 import BeautifulSoup
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            soup = BeautifulSoup(f.read(), 'xml')
            return soup.get_text()
    except ImportError:
        # Fallback to basic reading
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            return f.read()


def extract_text_from_doc(file_path: str) -> str:
    """Extract text from legacy DOC file."""
    try:
        import textract
        text = textract.process(file_path).decode('utf-8')
        return text
    except ImportError:
        return "Error: textract not installed. Run: pip install textract"
    except Exception as e:
        return f"Error reading DOC file: {str(e)}"


def extract_text_from_file(file_path: str) -> str:
    """
    Extract text from various file formats.
    
    Supported formats: PDF, TXT, DOCX, DOC, CSV, JSON, HTML, XLSX, XML
    """
    ext = os.path.splitext(file_path)[1].lower()
    
    extractors = {
        '.pdf': extract_text_from_pdf,
        '.txt': extract_text_from_txt,
        '.docx': extract_text_from_docx,
        '.doc': extract_text_from_doc,
        '.csv': extract_text_from_csv,
        '.json': extract_text_from_json,
        '.html': extract_text_from_html,
        '.htm': extract_text_from_html,
        '.xlsx': extract_text_from_xlsx,
        '.xls': extract_text_from_xlsx,
        '.xml': extract_text_from_xml,
    }
    
    if ext in extractors:
        try:
            return extractors[ext](file_path)
        except Exception as e:
            return f"Error extracting text from {ext} file: {str(e)}"
    else:
        return f"Unsupported file format: {ext}"


def get_supported_formats() -> List[str]:
    """Get list of supported file formats."""
    return [
        'pdf', 'txt', 'docx', 'doc', 
        'csv', 'json', 'html', 'htm',
        'xlsx', 'xls', 'xml'
    ]


def get_format_description() -> Dict[str, str]:
    """Get description of each supported format."""
    return {
        'PDF': 'Adobe PDF documents',
        'TXT': 'Plain text files',
        'DOCX': 'Microsoft Word (2007+)',
        'DOC': 'Microsoft Word (Legacy)',
        'CSV': 'Comma-separated values',
        'JSON': 'JSON data files',
        'HTML': 'Web pages',
        'XLSX': 'Microsoft Excel (2007+)',
        'XLS': 'Microsoft Excel (Legacy)',
        'XML': 'XML documents'
    }
