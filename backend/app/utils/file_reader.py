"""
File reader module for TXT and DOCX file parsing.
"""

import os
from typing import Optional


def read_txt_file(file_path: str) -> str:
    """
    Read a plain text file.
    
    Args:
        file_path: Path to the text file
        
    Returns:
        File contents as string
    """
    encodings = ['utf-8', 'latin-1', 'cp1252']
    
    for encoding in encodings:
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                return f.read()
        except UnicodeDecodeError:
            continue
    
    raise ValueError(f"Could not decode file with any supported encoding: {encodings}")


def read_docx_file(file_path: str) -> str:
    """
    Read a DOCX file and extract plain text.
    
    Args:
        file_path: Path to the DOCX file
        
    Returns:
        Extracted text content
    """
    try:
        from docx import Document
    except ImportError:
        raise ImportError("python-docx is required to read DOCX files. Install with: pip install python-docx")
    
    doc = Document(file_path)
    paragraphs = []
    
    for para in doc.paragraphs:
        text = para.text.strip()
        if text:
            paragraphs.append(text)
    
    return '\n\n'.join(paragraphs)


def read_file(file_path: str) -> str:
    """
    Read a file and return its text content.
    Supports TXT and DOCX formats.
    
    Args:
        file_path: Path to the file
        
    Returns:
        File contents as string
        
    Raises:
        ValueError: If file format is not supported
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    
    ext = os.path.splitext(file_path)[1].lower()
    
    if ext == '.txt':
        return read_txt_file(file_path)
    elif ext == '.docx':
        return read_docx_file(file_path)
    else:
        raise ValueError(f"Unsupported file format: {ext}. Supported formats: .txt, .docx")


async def read_uploaded_file(file_content: bytes, filename: str) -> str:
    """
    Read uploaded file content.
    
    Args:
        file_content: Raw file bytes
        filename: Original filename
        
    Returns:
        Extracted text content
    """
    import tempfile
    
    ext = os.path.splitext(filename)[1].lower()
    
    if ext not in ['.txt', '.docx']:
        raise ValueError(f"Unsupported file format: {ext}. Supported formats: .txt, .docx")
    
    # Write to temp file for processing
    with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
        tmp.write(file_content)
        tmp_path = tmp.name
    
    try:
        content = read_file(tmp_path)
        return content
    finally:
        # Clean up temp file
        os.unlink(tmp_path)
