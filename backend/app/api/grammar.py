"""
Grammar API endpoint.
Handles text analysis requests.
"""

import time
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.models.ngram_model import get_model
from app.models.spell_checker import get_spell_checker
from app.models.punctuation_checker import get_punctuation_checker
from app.models.grammar_rules import get_grammar_rules_checker
from app.models.transformer_model import get_transformer_checker
from app.models.semantic_checker import get_semantic_checker
from app.models.pos_ngram_model import get_pos_ngram_model
from app.utils.sentence_splitter import split_sentences, split_sentences_with_positions
from app.utils.tokenizer import get_word_tokens_with_positions, tokenize
from app.utils.scorer import calculate_confidence_score, calculate_sentence_fluency


router = APIRouter()


class CheckTextRequest(BaseModel):
    """Request model for text checking."""
    text: str = Field(..., min_length=1, max_length=50000, description="Text to analyze")
    ngram: str = Field("trigram", pattern="^(bigram|trigram)$", description="N-gram model to use")


class ErrorPosition(BaseModel):
    """Error position in text."""
    start: int
    end: int


class GrammarError(BaseModel):
    """Grammar error model."""
    type: str
    position: ErrorPosition
    original: str
    suggestion: str
    explanation: str
    sentenceIndex: int


class SentenceAnalysis(BaseModel):
    """Per-sentence analysis."""
    index: int
    original: str
    corrected: str
    errors: List[GrammarError]
    fluencyScore: float


class AnalysisResult(BaseModel):
    """Complete analysis result."""
    originalText: str
    correctedText: str
    errors: List[GrammarError]
    confidenceScore: float
    sentences: List[SentenceAnalysis]
    ngramMode: str
    processingTimeMs: int


def apply_corrections(text: str, errors: List[Dict]) -> str:
    if not errors: return text
    sorted_errors = sorted(errors, key=lambda e: e['position']['start'], reverse=True)
    modified_ranges = []
    result = text
    for error in sorted_errors:
        start = error['position']['start']
        end = error['position']['end']
        suggestion = error['suggestion']
        overlaps = False
        for mod_start, mod_end in modified_ranges:
            if not (end <= mod_start or start >= mod_end):
                overlaps = True
                break
        if overlaps: continue
        result = result[:start] + suggestion + result[end:]
        modified_ranges.append((start, end))
    return result


def limit_corrections(errors: List[Dict], word_count: int) -> List[Dict]:
    """
    Limit corrections.
    For short sentences (< 5 words), allow ALL corrections.
    For longer sentences, limit to 50% to prevent total rewrite hallucinations.
    """
    if word_count == 0:
        return errors
    
    # Always keep punctuation errors
    punct_errors = [e for e in errors if e['type'] == 'punctuation']
    other_errors = [e for e in errors if e['type'] != 'punctuation']
    
    # RELAXED LIMIT: If sentence is short, allow everything.
    if word_count < 5:
        return other_errors + punct_errors
        
    # Strict limit for longer text
    max_corrections = max(1, int(word_count * 0.5))
    
    # Priority: Spelling > Grammar > Style
    type_priority = {'spelling': 0, 'grammar': 1, 'semantic': 2, 'structure': 3}
    sorted_errors = sorted(other_errors, key=lambda e: type_priority.get(e['type'], 4))
    
    limited_other = sorted_errors[:max_corrections]
    
    return limited_other + punct_errors


@router.post("/check-text", response_model=AnalysisResult)
async def check_text(request: CheckTextRequest):
    """Analyze text for grammar, spelling, and punctuation errors."""
    start_time = time.time()
    text = request.text.strip()
    if not text: raise HTTPException(status_code=400, detail="Text cannot be empty")
    
    use_transformer = False 
    
    spell_checker = get_spell_checker()
    punctuation_checker = get_punctuation_checker()
    grammar_rules_checker = get_grammar_rules_checker()
    
    # 1. Run Global Rule Checker
    rule_based_errors = grammar_rules_checker.check_text(text)
    
    sentences_with_pos = split_sentences_with_positions(text)
    
    # Map global errors to sentences
    for error in rule_based_errors:
        error_start = error['position']['start']
        for sent_idx, (sentence, sent_start, sent_end) in enumerate(sentences_with_pos):
            if sent_start <= error_start < sent_end:
                error['sentenceIndex'] = sent_idx
                break
        else:
            error['sentenceIndex'] = 0
            
    all_errors = []
    sentence_analyses = []
    
    for sent_idx, (sentence, sent_start, sent_end) in enumerate(sentences_with_pos):
        sentence_errors = []
        
        # Add Rule Errors
        for error in rule_based_errors:
            if error.get('sentenceIndex') == sent_idx:
                sentence_errors.append(error.copy())
        
        # Check Spelling (Avoid overlapping with Grammar errors)
        spell_errors = spell_checker.check_text(sentence)
        for error in spell_errors:
            error['position']['start'] += sent_start
            error['position']['end'] += sent_start
            error['sentenceIndex'] = sent_idx
            
            overlaps = False
            for existing in sentence_errors:
                if not (error['position']['end'] <= existing['position']['start'] or error['position']['start'] >= existing['position']['end']):
                    overlaps = True
                    break
            if not overlaps:
                sentence_errors.append(error)
                
        # Check Punctuation
        punct_errors = punctuation_checker.check_text(sentence)
        for error in punct_errors:
            error['position']['start'] += sent_start
            error['position']['end'] += sent_start
            error['sentenceIndex'] = sent_idx
            overlaps = False
            for existing in sentence_errors:
                if not (error['position']['end'] <= existing['position']['start'] or error['position']['start'] >= existing['position']['end']):
                    overlaps = True
                    break
            if not overlaps:
                sentence_errors.append(error)

        # Check Semantic
        try:
            semantic_checker = get_semantic_checker()
            sem_errors = semantic_checker.check_text(sentence) # Note: check_text, not check_sentence
            for error in sem_errors:
                error['position']['start'] += sent_start
                error['position']['end'] += sent_start
                error['sentenceIndex'] = sent_idx
                overlaps = False
                for existing in sentence_errors:
                    if not (error['position']['end'] <= existing['position']['start'] or error['position']['start'] >= existing['position']['end']):
                        overlaps = True
                        break
                if not overlaps:
                    sentence_errors.append(error)
        except Exception: pass

        # Check Structure (POS)
        try:
            pos_model = get_pos_ngram_model()
            struct_errors = pos_model.check_sentence(sentence)
            for error in struct_errors:
                error['position']['start'] += sent_start
                error['position']['end'] += sent_start
                error['sentenceIndex'] = sent_idx
                overlaps = False
                for existing in sentence_errors:
                    if not (error['position']['end'] <= existing['position']['start'] or error['position']['start'] >= existing['position']['end']):
                        overlaps = True
                        break
                if not overlaps:
                    sentence_errors.append(error)
        except Exception: pass
        
        # Deduplicate
        seen_pos = set()
        unique_errors = []
        for error in sentence_errors:
            key = (error['position']['start'], error['position']['end'], error['suggestion'])
            if key not in seen_pos:
                seen_pos.add(key)
                unique_errors.append(error)
        
        # Limit corrections
        word_count = len(tokenize(sentence))
        limited_errors = limit_corrections(unique_errors, word_count)
        
        corrected_sent = apply_corrections(sentence, limited_errors)
        
        sentence_analyses.append(SentenceAnalysis(
            index=sent_idx,
            original=sentence,
            corrected=corrected_sent,
            errors=[GrammarError(**e) for e in limited_errors],
            fluencyScore=100.0
        ))
        
        all_errors.extend(limited_errors)
    
    corrected_text = apply_corrections(text, all_errors)
    
    return AnalysisResult(
        originalText=text,
        correctedText=corrected_text,
        errors=[GrammarError(**e) for e in all_errors],
        confidenceScore=0.9, # Simplified
        sentences=sentence_analyses,
        ngramMode=request.ngram,
        processingTimeMs=int((time.time() - start_time) * 1000)
    )
