"""
Grammar Checker Backend - FastAPI Application

An academic-grade grammar, spelling, and punctuation checker
using statistical n-gram language models.
"""

import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import grammar, file_upload
from app.models.ngram_model import initialize_model, get_model
from app.models.spell_checker import initialize_spell_checker
from app.models.pos_ngram_model import get_pos_ngram_model
from app.models.semantic_checker import get_semantic_checker


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan handler.
    Initializes models on startup.
    """
    print("Initializing Grammar Checker Backend...")
    print("Loading language models and corpora...")
    
    # Initialize n-gram model
    model = initialize_model()
    
    # Initialize spell checker with vocabulary from n-gram model
    initialize_spell_checker(model.vocabulary, model.unigram_counts)
    
    # Initialize Transformer (Hugging Face) - DISABLED for N-gram rubrics
    # try:
    #     from app.models.transformer_model import get_transformer_checker
    #     print("Initializing Transformer model...")
    #     get_transformer_checker()
    # except Exception as e:
    #     print(f"Failed to initialize Transformer: {e}")
    
    # Pre-load advanced models to prevent lag on first request
    print("Initializing POS N-gram model...")
    get_pos_ngram_model()
    
    print("Initializing Semantic Checker...")
    get_semantic_checker()
    
    print(f"Models loaded successfully!")
    print(f"Vocabulary size: {len(model.vocabulary):,} words")
    print(f"Total words trained: {model.total_words:,}")
    print("Server is ready to accept requests.")
    
    yield
    
    print("Shutting down Grammar Checker Backend...")


# Create FastAPI application
app = FastAPI(
    title="Grammar Checker API",
    description="Academic-grade grammar, spelling, and punctuation checker using statistical n-gram language models.",
    version="1.0.0",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:3001",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(grammar.router, tags=["Grammar"])
app.include_router(file_upload.router, tags=["File Upload"])


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": "Grammar Checker API",
        "version": "1.0.0",
        "description": "Academic-grade grammar, spelling, and punctuation checker",
        "endpoints": {
            "POST /check-text": "Analyze text for errors",
            "POST /check-file": "Upload and analyze a file",
            "GET /health": "Health check",
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    model = get_model()
    
    return {
        "status": "healthy",
        "model_loaded": model._trained,
        "vocabulary_size": len(model.vocabulary),
        "total_words": model.total_words,
    }


@app.get("/test-grammar")
async def test_grammar():
    """
    Test endpoint to verify grammar rules are loaded correctly.
    Tests the sentence: 'my brother buy a new phone but it battery are drain very fast'
    """
    from app.models.grammar_rules import GrammarRulesChecker
    from app.models.punctuation_checker import PunctuationChecker
    
    text = "my brother buy a new phone but it battery are drain very fast"
    
    grammar_checker = GrammarRulesChecker()
    punct_checker = PunctuationChecker()
    
    grammar_errors = grammar_checker.check_text(text)
    punct_errors = punct_checker.check_text(text)
    
    # Apply corrections
    all_errors = grammar_errors + punct_errors
    sorted_errors = sorted(all_errors, key=lambda e: e['position']['start'], reverse=True)
    
    result = text
    for error in sorted_errors:
        start = error['position']['start']
        end = error['position']['end']
        result = result[:start] + error['suggestion'] + result[end:]
    
    return {
        "original": text,
        "corrected": result,
        "expected": "My brother bought a new phone, but its battery is draining very fast.",
        "grammar_errors": [{"original": e["original"], "suggestion": e["suggestion"]} for e in grammar_errors],
        "punct_errors": [{"original": e["original"], "suggestion": e["suggestion"]} for e in punct_errors],
        "is_correct": result == "My brother bought a new phone, but its battery is draining very fast."
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
