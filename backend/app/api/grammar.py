"""
Grammar API endpoint.
Supports Basic (N-gram) and Advanced (Transformer/AI) model modes.
"""
import time
from typing import List, Dict, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.models.ngram_model import get_model
from app.models.spell_checker import get_spell_checker
from app.models.punctuation_checker import get_punctuation_checker
from app.models.grammar_rules import get_grammar_rules_checker
from app.models.semantic_checker import get_semantic_checker
from app.models.pos_ngram_model import get_pos_ngram_model
from app.models.transformer_model import get_transformer_checker
from app.utils.sentence_splitter import split_sentences_with_positions
from app.utils.tokenizer import tokenize, get_word_tokens_with_positions

router = APIRouter()

class CheckTextRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=50000)
    ngram: str = Field("trigram", pattern="^(bigram|trigram|4gram)$")
    model_type: str = Field("ngram", pattern="^(ngram|transformer)$")

class ErrorPosition(BaseModel):
    start: int
    end: int

class GrammarError(BaseModel):
    type: str
    position: ErrorPosition
    original: str
    suggestion: str
    explanation: str
    sentenceIndex: int

class SentenceAnalysis(BaseModel):
    index: int
    original: str
    corrected: str
    errors: List[GrammarError]
    fluencyScore: float

class AnalysisResult(BaseModel):
    originalText: str
    correctedText: str
    errors: List[GrammarError]
    confidenceScore: float
    sentences: List[SentenceAnalysis]
    ngramMode: str  # Will show "Transformer-AI" when in transformer mode
    processingTimeMs: int

def apply_corrections(text: str, errors: List[Dict]) -> str:
    if not errors: return text
    sorted_errors = sorted(errors, key=lambda e: e['position']['start'], reverse=True)
    result = text
    modified = []
    for error in sorted_errors:
        s, e, sugg = error['position']['start'], error['position']['end'], error['suggestion']
        if any(not (e <= ms or s >= me) for ms, me in modified): continue
        result = result[:s] + sugg + result[e:]
        modified.append((s, e))
    return result

def limit_corrections(errors: List[Dict], word_count: int) -> List[Dict]:
    if word_count == 0: return errors
    punct = [e for e in errors if e['type'] == 'punctuation']
    other = [e for e in errors if e['type'] != 'punctuation']
    
    if word_count < 5: return other + punct
    
    limit = max(1, int(word_count * 0.6))
    priority = {'spelling': 0, 'grammar': 1, 'ngram': 2, 'semantic': 3, 'structure': 4, 'ai': 5}
    other.sort(key=lambda x: priority.get(x['type'], 6))
    
    return other[:limit] + punct


def check_with_ngram(sentence: str, ngram_order: int, probability_threshold: float = 0.005) -> List[Dict]:
    """
    Detect unusual word sequences using N-gram probability analysis.
    AGGRESSIVE MODE: Loosened thresholds for testing.
    """
    errors = []
    model = get_model()
    
    print(f"[N-GRAM DEBUG] Model trained status: {model._trained}, Vocab size: {len(model.vocabulary)}")
    
    if not model._trained:
        print("[N-GRAM WARNING] Model is NOT trained! Returning empty errors.")
        return errors
    
    tokens = get_word_tokens_with_positions(sentence)
    if len(tokens) < 2:
        print(f"[N-GRAM DEBUG] Too few tokens ({len(tokens)}), skipping.")
        return errors
    
    words = [t[0] for t in tokens]
    
    skip_words = {
        'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
        'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
        'should', 'may', 'might', 'must', 'can', 'to', 'of', 'in', 'for',
        'on', 'with', 'at', 'by', 'from', 'as', 'or', 'and', 'but', 'if',
        'that', 'this', 'it', 'i', 'you', 'he', 'she', 'we', 'they', 'my',
        'your', 'his', 'her', 'our', 'their', 'its', 'not', 'no', 'yes',
        'so', 'very', 'just', 'also', 'only', 'even', 'now', 'here', 'there'
    }
    
    for i, (word, start, end) in enumerate(tokens):
        if word.lower() in skip_words or len(word) < 3:
            continue
            
        context_start = max(0, i - (ngram_order - 1))
        context = words[context_start:i]
        
        prob = model.interpolated_probability(word, context, ngram_order)
        
        if prob < 0.01:
            print(f"[N-GRAM DEBUG] Word '{word}' | Context: {context} | Prob: {prob:.6f} | Threshold: {probability_threshold}")
        
        if prob < probability_threshold:
            candidates = model.get_word_candidates(word, context, max_candidates=3, order=ngram_order)
            
            if candidates:
                top_word, top_prob = candidates[0]
                
                if (top_word.lower() != word.lower() and 
                    top_prob > prob * 2 and 
                    top_word in model.vocabulary):
                    print(f"[N-GRAM FOUND] '{word}' -> '{top_word}' (prob {prob:.6f} -> {top_prob:.6f})")
                    
                    original_text = sentence[start:end]
                    if original_text[0].isupper():
                        suggestion = top_word.capitalize()
                    elif original_text.isupper():
                        suggestion = top_word.upper()
                    else:
                        suggestion = top_word
                    
                    context_str = ' '.join(context[-2:]) if context else ''
                    errors.append({
                        'type': 'ngram',
                        'position': {'start': start, 'end': end},
                        'original': original_text,
                        'suggestion': suggestion,
                        'explanation': f'Unusual word in context "{context_str} ___". Consider "{suggestion}".',
                        'sentenceIndex': 0
                    })
    
    return errors


def overlaps_with_existing(error: Dict, existing_errors: List[Dict]) -> bool:
    """Check if error overlaps with any existing error."""
    e_start = error['position']['start']
    e_end = error['position']['end']
    for ex in existing_errors:
        ex_start = ex['position']['start']
        ex_end = ex['position']['end']
        if not (e_end <= ex_start or e_start >= ex_end):
            return True
    return False


def check_with_transformer(text: str) -> tuple[List[Dict], str, bool]:
    """
    Use the Transformer model (T5) to check text.
    Returns: (errors, corrected_text, success)
    """
    print("[TRANSFORMER] Starting AI-powered grammar check...")
    
    try:
        checker = get_transformer_checker()
        
        if not checker.pipe:
            print("[TRANSFORMER] Model not initialized. Falling back to N-gram.")
            return [], text, False
        
        errors = checker.check_text(text)
        
        # Apply corrections to get corrected text
        corrected = apply_corrections(text, errors)
        
        print(f"[TRANSFORMER] Found {len(errors)} AI-detected errors")
        return errors, corrected, True
        
    except Exception as e:
        print(f"[TRANSFORMER ERROR] {e}")
        return [], text, False


@router.post("/check-text", response_model=AnalysisResult)
async def check_text(request: CheckTextRequest):
    start_time = time.time()
    text = request.text.strip()
    if not text: raise HTTPException(status_code=400, detail="Empty text")
    
    # ============================================================
    # TRANSFORMER MODE (Advanced/AI)
    # ============================================================
    if request.model_type == "transformer":
        print(f"[API] Using TRANSFORMER mode (Advanced AI)")
        
        transformer_errors, corrected_text, success = check_with_transformer(text)
        
        if not success:
            # Fallback to N-gram mode if Transformer fails
            print("[API] Transformer failed. Falling back to N-gram mode...")
            request.model_type = "ngram"  # Fall through to N-gram processing
        else:
            # Also run spell checker - Transformer is grammar-focused, spell checker catches spelling
            spell_checker = get_spell_checker()
            spell_errors = spell_checker.check_text(text)
            print(f"[TRANSFORMER+SPELL] Found {len(spell_errors)} spelling errors")
            
            # Format errors for response
            all_errors = []
            
            # Add transformer errors
            for e in transformer_errors:
                e['sentenceIndex'] = 0
                e['type'] = 'ai'
                all_errors.append(e)
            
            # Add spell errors (avoid duplicates by position)
            for e in spell_errors:
                e['sentenceIndex'] = 0
                # Check if position overlaps with transformer errors
                if not overlaps_with_existing(e, all_errors):
                    all_errors.append(e)
            
            # Apply all corrections
            corrected_text = apply_corrections(text, all_errors)
            
            # Create a single sentence analysis for transformer mode
            analyses = [SentenceAnalysis(
                index=0,
                original=text,
                corrected=corrected_text,
                errors=[GrammarError(**e) for e in all_errors],
                fluencyScore=95.0 if not all_errors else max(50, 95 - len(all_errors) * 5)
            )]
            
            return AnalysisResult(
                originalText=text,
                correctedText=corrected_text,
                errors=[GrammarError(**e) for e in all_errors],
                confidenceScore=0.95,
                sentences=analyses,
                ngramMode="Transformer-AI",
                processingTimeMs=int((time.time() - start_time) * 1000)
            )
    
    # ============================================================
    # N-GRAM MODE (Basic/Statistical)
    # ============================================================
    print(f"[API] Using N-GRAM mode ({request.ngram})")
    
    ngram_order = 3
    if request.ngram == "bigram": ngram_order = 2
    elif request.ngram == "4gram": ngram_order = 4
    
    spell_checker = get_spell_checker()
    punct_checker = get_punctuation_checker()
    rules_checker = get_grammar_rules_checker()
    
    # 1. Rules
    rule_errors = rules_checker.check_text(text)
    
    # 2. Sentences
    sentences = split_sentences_with_positions(text)
    
    # Map rules to sentences
    for err in rule_errors:
        estart = err['position']['start']
        for idx, (sent, sstart, send) in enumerate(sentences):
            if sstart <= estart < send:
                err['sentenceIndex'] = idx
                break
        else: err['sentenceIndex'] = 0
        
    all_errors = []
    analyses = []
    
    for idx, (sent, start_offset, end_offset) in enumerate(sentences):
        sent_errors = [e.copy() for e in rule_errors if e.get('sentenceIndex') == idx]
        
        # Spelling
        spells = spell_checker.check_text(sent)
        for e in spells:
            e['position']['start'] += start_offset
            e['position']['end'] += start_offset
            e['sentenceIndex'] = idx
            if not overlaps_with_existing(e, sent_errors):
                sent_errors.append(e)
                
        # Punctuation
        puncts = punct_checker.check_text(sent)
        for e in puncts:
            e['position']['start'] += start_offset
            e['position']['end'] += start_offset
            e['sentenceIndex'] = idx
            if not overlaps_with_existing(e, sent_errors):
                sent_errors.append(e)

        # Semantic
        try:
            sem = get_semantic_checker().check_text(sent)
            for e in sem:
                e['position']['start'] += start_offset
                e['position']['end'] += start_offset
                e['sentenceIndex'] = idx
                if not overlaps_with_existing(e, sent_errors):
                    sent_errors.append(e)
        except: pass

        # Structure (POS)
        try:
            pos = get_pos_ngram_model().check_sentence(sent)
            for e in pos:
                e['position']['start'] += start_offset
                e['position']['end'] += start_offset
                e['sentenceIndex'] = idx
                if not overlaps_with_existing(e, sent_errors):
                    sent_errors.append(e)
        except: pass
        
        # N-GRAM BASED ERROR DETECTION
        ngram_errors = check_with_ngram(sent, ngram_order)
        for e in ngram_errors:
            e['position']['start'] += start_offset
            e['position']['end'] += start_offset
            e['sentenceIndex'] = idx
            if not overlaps_with_existing(e, sent_errors):
                sent_errors.append(e)
        print(f"[N-GRAM RESULT] Sentence {idx}: Found {len(ngram_errors)} n-gram errors")
        
        # Deduplicate
        unique = []
        seen = set()
        for e in sent_errors:
            k = (e['position']['start'], e['position']['end'], e['suggestion'])
            if k not in seen:
                seen.add(k)
                unique.append(e)
        
        # Fluency Score
        fluency = 100.0
        try:
            words = tokenize(sent)
            model = get_model()
            if model._trained:
                perp = model.perplexity(words, order=ngram_order)
                fluency = max(0, min(100, 100 - (perp - 1) * 5))
        except: pass
        
        final_errors = limit_corrections(unique, len(tokenize(sent)))
        corrected = apply_corrections(sent, final_errors)
        
        analyses.append(SentenceAnalysis(
            index=idx,
            original=sent,
            corrected=corrected,
            errors=[GrammarError(**e) for e in final_errors],
            fluencyScore=fluency
        ))
        all_errors.extend(final_errors)
        
    final_text = apply_corrections(text, all_errors)
    
    return AnalysisResult(
        originalText=text,
        correctedText=final_text,
        errors=[GrammarError(**e) for e in all_errors],
        confidenceScore=0.9,
        sentences=analyses,
        ngramMode=request.ngram,
        processingTimeMs=int((time.time() - start_time) * 1000)
    )
