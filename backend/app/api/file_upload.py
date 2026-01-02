"""
File upload API endpoint.
Handles file upload and analysis with Basic/Advanced model support.
"""

import time
from typing import Optional
from fastapi import APIRouter, HTTPException, UploadFile, File, Form

from app.api.grammar import CheckTextRequest, AnalysisResult
from app.utils.file_reader import read_uploaded_file


router = APIRouter()


MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
ALLOWED_EXTENSIONS = {'.txt', '.docx'}


@router.post("/check-file", response_model=AnalysisResult)
async def check_file(
    file: UploadFile = File(...),
    ngram: str = Form("trigram"),
    model_type: str = Form("ngram")
):
    """
    Upload and analyze a file for grammar, spelling, and punctuation errors.
    
    Args:
        file: Uploaded file (TXT or DOCX)
        ngram: N-gram model to use ("bigram", "trigram", "hybrid")
        model_type: Model type ("ngram" for Basic, "transformer" for Advanced AI)
        
    Returns:
        AnalysisResult with errors and corrections
    """
    # Import here to avoid circular dependency
    from app.api.grammar import check_text

    # Validate ngram parameter
    if ngram not in ["bigram", "trigram", "hybrid", "4gram"]:
        raise HTTPException(
            status_code=400,
            detail="Invalid ngram mode. Must be 'bigram', 'trigram', or 'hybrid'."
        )
    
    # Validate model_type parameter
    if model_type not in ["ngram", "transformer"]:
        raise HTTPException(
            status_code=400,
            detail="Invalid model_type. Must be 'ngram' or 'transformer'."
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
    
    # Use the existing check_text endpoint logic with model_type
    request = CheckTextRequest(text=text, ngram=ngram, model_type=model_type)
    
    try:
        result = await check_text(request)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")
