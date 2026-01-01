"""
File upload API endpoint.
Handles file upload and analysis.
"""

import time
from typing import Optional
from fastapi import APIRouter, HTTPException, UploadFile, File, Form

from app.api.grammar import check_text, CheckTextRequest, AnalysisResult
from app.utils.file_reader import read_uploaded_file


router = APIRouter()


MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
ALLOWED_EXTENSIONS = {'.txt', '.docx'}


@router.post("/check-file", response_model=AnalysisResult)
async def check_file(
    file: UploadFile = File(...),
    ngram: str = Form("trigram")
):
    """
    Upload and analyze a file for grammar, spelling, and punctuation errors.
    
    Args:
        file: Uploaded file (TXT or DOCX)
        ngram: N-gram model to use ("bigram" or "trigram")
        
    Returns:
        AnalysisResult with errors and corrections
    """
    # Validate ngram parameter
    if ngram not in ["bigram", "trigram", "4gram"]:
        raise HTTPException(
            status_code=400,
            detail="Invalid ngram mode. Must be 'bigram', 'trigram', or '4gram'."
        )
    
    # Validate filename
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")
    
    # Check file extension
    ext = '.' + file.filename.split('.')[-1].lower() if '.' in file.filename else ''
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {ext}. Supported types: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    
    # Read file content
    try:
        content = await file.read()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to read file: {str(e)}")
    
    # Check file size
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum size: {MAX_FILE_SIZE // (1024*1024)}MB"
        )
    
    # Extract text from file
    try:
        text = await read_uploaded_file(content, file.filename)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to extract text: {str(e)}")
    
    if not text or not text.strip():
        raise HTTPException(status_code=400, detail="File appears to be empty or contains no text")
    
    # Use the existing check_text endpoint logic
    request = CheckTextRequest(text=text, ngram=ngram)
    
    try:
        result = await check_text(request)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")
