
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
    """
    Apply error corrections to text.
    
    Args:
        text: Original text
        errors: List of error dictionaries
        
    Returns:
        Corrected text
    """
    if not errors:
        return text
    
    # Sort errors by position (reverse order for safe replacement)
    sorted_errors = sorted(errors, key=lambda e: e['position']['start'], reverse=True)
    
    # Track which positions have been modified to avoid overlapping edits
    modified_ranges = []
    
    result = text
    for error in sorted_errors:
        start = error['position']['start']
        end = error['position']['end']
        suggestion = error['suggestion']
        
        # Skip if this range overlaps with an already modified range
        overlaps = False
        for mod_start, mod_end in modified_ranges:
            if not (end <= mod_start or start >= mod_end):
                overlaps = True
                break
        
        if overlaps:
            continue
        
        # Apply the correction
        result = result[:start] + suggestion + result[end:]
        modified_ranges.append((start, end))
    
    return result


def limit_corrections(errors: List[Dict], word_count: int) -> List[Dict]:
    """
    Limit corrections to max 50% of words per sentence.
    Punctuation errors are always included.
    
    Args:
        errors: List of errors
        word_count: Total word count
        
    Returns:
        Limited list of errors
    """
    if word_count == 0:
        return errors
    
    # Separate punctuation errors (always keep them)
    punct_errors = [e for e in errors if e['type'] == 'punctuation']
    other_errors = [e for e in errors if e['type'] != 'punctuation']
    
    # Limit non-punctuation errors to 50% of words
    max_corrections = max(1, int(word_count * 0.5))
    
    # Prioritize by error type: spelling > grammar
    type_priority = {'spelling': 0, 'grammar': 1}
    sorted_errors = sorted(other_errors, key=lambda e: type_priority.get(e['type'], 2))
    
    limited_other = sorted_errors[:max_corrections]
    
    # Always include punctuation errors
    return limited_other + punct_errors


@router.post("/check-text", response_model=AnalysisResult)
async def check_text(request: CheckTextRequest):
    """
    Analyze text for grammar, spelling, and punctuation errors.
    
    Args:
        request: CheckTextRequest with text and ngram mode
        
    Returns:
        AnalysisResult with errors and corrections
    """
    start_time = time.time()
    
    text = request.text.strip()
    use_trigram = request.ngram == "trigram"
    
    if not text:
        raise HTTPException(status_code=400, detail="Text cannot be empty")
    
    # Get checkers
    # NOTE: Transformer disabled - using N-gram model as per project rubrics
    # transformer_checker = get_transformer_checker()
    # use_transformer = transformer_checker.pipe is not None
    use_transformer = False  # Force N-gram mode for academic requirements
    
    spell_checker = get_spell_checker()
    punctuation_checker = get_punctuation_checker()
    grammar_rules_checker = get_grammar_rules_checker()
    
    rule_based_errors = []
    
    # Run rule-based checker only if NOT using transformer (or maybe for supplementary?)
    # Actually, Transformer might miss some mechanical things like introductory commas if untested.
    # But usually T5 is good.
    # Let's run Punctuation Checker ALWAYS, because it's deterministic.
    # But GrammarRulesChecker is legacy.
    
    if not use_transformer:
        # First, run rule-based grammar check on full text
        rule_based_errors = grammar_rules_checker.check_text(text)
    
    # Split into sentences
    sentences_with_pos = split_sentences_with_positions(text)
    
    # Assign sentence indices to rule-based errors
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
        
        if use_transformer:
            # --- TRANSFORMER MODE ---
            t5_errors = transformer_checker.check_text(sentence)
            for error in t5_errors:
                # Adjust positions relative to global text
                error['position']['start'] += sent_start
                error['position']['end'] += sent_start
                error['sentenceIndex'] = sent_idx
                sentence_errors.append(error)
                
            # Also run punctuation checker for specific mechanical rules (like double spaces)
            # that T5 might skip or handle implicitly. 
            # We add them only if they don't overlap.
            punct_errors = punctuation_checker.check_text(sentence)
            for error in punct_errors:
                error['position']['start'] += sent_start
                error['position']['end'] += sent_start
                error['sentenceIndex'] = sent_idx
                
                # Check overlap
                is_overlap = False
                for existing in sentence_errors:
                    if not (error['position']['end'] <= existing['position']['start'] or
                            error['position']['start'] >= existing['position']['end']):
                        is_overlap = True
                        break
                if not is_overlap:
                    sentence_errors.append(error)

        else:
            # --- LEGACY MODE ---
            
            # Get rule-based errors for this sentence
            for error in rule_based_errors:
                if error.get('sentenceIndex') == sent_idx:
                    sentence_errors.append(error.copy())
            
            # Check spelling - skip words already flagged by grammar
            # Use range overlap check, not just exact position match
            spell_errors = spell_checker.check_text(sentence)
            for error in spell_errors:
                error['position']['start'] += sent_start
                error['position']['end'] += sent_start
                error['sentenceIndex'] = sent_idx
                
                # Check if this position overlaps with any existing grammar error
                spell_start = error['position']['start']
                spell_end = error['position']['end']
                
                overlaps_grammar = False
                for existing in sentence_errors:
                    exist_start = existing['position']['start']
                    exist_end = existing['position']['end']
                    # Check for any overlap
                    if not (spell_end <= exist_start or spell_start >= exist_end):
                        overlaps_grammar = True
                        break
                
                if not overlaps_grammar:
                    sentence_errors.append(error)
            
            # Check punctuation - also use overlap detection
            punct_errors = punctuation_checker.check_text(sentence)
            for error in punct_errors:
                error['position']['start'] += sent_start
                error['position']['end'] += sent_start
                error['sentenceIndex'] = sent_idx
                
                # Check overlap with existing errors
                punct_start = error['position']['start']
                punct_end = error['position']['end']
                
                overlaps = False
                for existing in sentence_errors:
                    exist_start = existing['position']['start']
                    exist_end = existing['position']['end']
                    if not (punct_end <= exist_start or punct_start >= exist_end):
                        overlaps = True
                        break
                
                if not overlaps:
                    sentence_errors.append(error)
        
        # Remove duplicate errors (same position)
        seen_positions = set()
        unique_errors = []
        for error in sentence_errors:
            pos_key = (error['position']['start'], error['position']['end'])
            if pos_key not in seen_positions:
                seen_positions.add(pos_key)
                unique_errors.append(error)
        
        # Limit corrections per sentence (keep limiting to avoid overwhelming)
        word_count = len(tokenize(sentence))
        limited_errors = limit_corrections(unique_errors, word_count)
        
        # Calculate sentence fluency (Legacy metric, helpful for debugging)
        fluency = 100.0
        try:
             words = tokenize(sentence)
             model = get_model() # N-Gram model still used for scoring?
             # N-Gram model might be untrained if we focused on T5.
             if model._trained:
                 perplexity = model.perplexity(words, use_trigram) if words else 100
                 fluency = calculate_sentence_fluency(sentence, perplexity, len(limited_errors))
        except:
             pass
        
        # Apply corrections to get corrected sentence
        corrected_sentence = apply_corrections(sentence, limited_errors)
        
        sentence_analyses.append(SentenceAnalysis(
            index=sent_idx,
            original=sentence,
            corrected=corrected_sentence,
            errors=[GrammarError(**e) for e in limited_errors],
            fluencyScore=fluency
        ))
        
        # Collect all errors (no duplicates)
        all_errors.extend(limited_errors)
    
    # Calculate corrected text from all unique errors
    corrected_text = apply_corrections(text, all_errors)
    
    # Calculate confidence score
    fluency_scores = [s.fluencyScore for s in sentence_analyses]
    confidence = calculate_confidence_score(text, all_errors, fluency_scores)
    
    processing_time = int((time.time() - start_time) * 1000)
    
    return AnalysisResult(
        originalText=text,
        correctedText=corrected_text,
        errors=[GrammarError(**e) for e in all_errors],
        confidenceScore=confidence,
        sentences=sentence_analyses,
        ngramMode=request.ngram,
        processingTimeMs=processing_time
    )
