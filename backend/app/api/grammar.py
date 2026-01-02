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
    ngram: str = Field("trigram", pattern="^(bigram|trigram|4gram|hybrid)$")
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
    ngramMode: str
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


from app.models.char_ngram_model import get_char_model, initialize_char_model
from app.models.hybrid_scorer import HybridScorer

_hybrid_scorer = None

def get_initialized_hybrid_scorer():
    global _hybrid_scorer
    if _hybrid_scorer:
        return _hybrid_scorer
        
    word_model = get_model()
    char_model = get_char_model()
    
    if not char_model._trained and word_model._trained:
        print("[HYBRID] Training character N-gram model on vocabulary...")
        char_model.train(list(word_model.vocabulary))
        
    _hybrid_scorer = HybridScorer(word_model, char_model)
    return _hybrid_scorer

def check_with_ngram(sentence: str, ngram_order: int, probability_threshold: float = 0.005, use_hybrid: bool = False) -> List[Dict]:
    """
    Detect unusual word sequences.
    If use_hybrid is True, uses Character N-gram + Hybrid Scorer.
    If use_hybrid is False, uses pure Word N-gram probabilities.
    """
    errors = []
    model = get_model()
    scorer = get_initialized_hybrid_scorer() if use_hybrid else None
    
    if not model._trained:
        return errors
    
    tokens = get_word_tokens_with_positions(sentence)
    if len(tokens) < 2: return errors
    
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
    
    # Protected words - common valid words that should NEVER be changed by N-gram
    protected_words = {
        # Weather/Nature
        'raining', 'rain', 'rained', 'rainy', 'sunny', 'sun', 'snow', 'snowing',
        # Common verbs often incorrectly changed
        'wave', 'waved', 'waving', 'waves', 'sings', 'sing', 'sang', 'sung', 'singing',
        'ate', 'eat', 'eaten', 'eating', 'eats', 'wait', 'waited', 'waiting', 'waits',
        # Common nouns
        'game', 'games', 'gaming', 'ice', 'icy', 'fun', 'funny', 'cone', 'cones',
        # Spelling-related
        'spelling', 'spell', 'spelled', 'spells', 'fix', 'fixed', 'fixes', 'fixing',
        # Adjectives/Adverbs
        'hard', 'harder', 'hardest', 'good', 'well', 'better', 'best',
        # Time
        'today', 'yesterday', 'tomorrow',
        # Structure
        'structure', 'structured', 'structures', 'flow', 'flows', 'flowing',
        # Contractions - CRITICAL: never modify these
        "don't", "doesn't", "didn't", "won't", "can't", "couldn't", "wouldn't",
        "shouldn't", "isn't", "aren't", "wasn't", "weren't", "hasn't", "haven't",
        "hadn't", "it's", "that's", "what's", "who's", "there's", "here's",
        "i'm", "you're", "we're", "they're", "he's", "she's", "let's",
        "i've", "you've", "we've", "they've", "i'd", "you'd", "he'd", "she'd",
    }
    
    for i, (word, start, end) in enumerate(tokens):
        if word.lower() in skip_words or len(word) < 3:
            continue
        
        # CRITICAL: Never touch words with apostrophes (contractions)
        if "'" in word:
            continue
            
        # CRITICAL: Never touch words that are in vocabulary or protected list
        word_lower = word.lower()
        if word_lower in model.vocabulary or word_lower in protected_words:
            continue  # SKIP entirely - don't even check probability
            
        context_start = max(0, i - (ngram_order - 1))
        context = words[context_start:i]
        
        prob = model.interpolated_probability(word, context, ngram_order)
        
        if prob < probability_threshold:
            
            # --- HYBRID MODE ---
            if use_hybrid and scorer:
                raw_candidates = model.get_word_candidates(word, context, max_candidates=10, order=ngram_order)
                candidate_words = [c[0] for c in raw_candidates]
                if not candidate_words: continue

                best_candidates = scorer.rank_candidates(candidate_words, context, original_word=word)
                if best_candidates:
                    top_word = best_candidates[0]
                    current_score = scorer.score_candidate(word, context, original_word=word)
                    new_score = scorer.score_candidate(top_word, context, original_word=word)
                    
                    if top_word.lower() != word.lower() and new_score > current_score * 1.5:
                        original_text = sentence[start:end]
                        if original_text[0].isupper(): suggestion = top_word.capitalize()
                        elif original_text.isupper(): suggestion = top_word.upper()
                        else: suggestion = top_word
                        
                        errors.append({
                            'type': 'ngram',
                            'position': {'start': start, 'end': end},
                            'original': original_text,
                            'suggestion': suggestion,
                            'explanation': f'Context suggests "{suggestion}" fits better (Hybrid Score {new_score:.2f} vs {current_score:.2f}).',
                            'sentenceIndex': 0
                        })

            # --- PURE STATISTICAL MODE (Bigram/Trigram) ---
            # Only triggered for words NOT in vocabulary (already filtered above)
            # So this is essentially for misspelled words only
            else:
                candidates = model.get_word_candidates(word, context, max_candidates=3, order=ngram_order)
                if candidates:
                    top_word, top_prob = candidates[0]
                    
                    # Since we already skipped vocab words, this word is a misspelling
                    # Use a high bar: only suggest if probability is 5x better
                    if (top_word.lower() != word.lower() and 
                        top_prob > prob * 5 and
                        top_word in model.vocabulary):
                        
                        original_text = sentence[start:end]
                        if original_text[0].isupper(): suggestion = top_word.capitalize()
                        elif original_text.isupper(): suggestion = top_word.upper()
                        else: suggestion = top_word
                        
                        context_str = ' '.join(context[-2:]) if context else ''
                        errors.append({
                            'type': 'ngram',
                            'position': {'start': start, 'end': end},
                            'original': original_text,
                            'suggestion': suggestion,
                            'explanation': f'Statistically unusual word in context "{context_str} ___". Consider "{suggestion}".',
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


def check_with_transformer(text: str) -> tuple:
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
        corrected = apply_corrections(text, errors)
        
        print(f"[TRANSFORMER] Found {len(errors)} AI-detected errors")
        return errors, corrected, True
        
    except Exception as e:
        print(f"[TRANSFORMER ERROR] {e}")
        return [], text, False


# Import quote normalization for preprocessing
from app.utils.tokenizer import normalize_quotes as normalize_text_quotes


@router.post("/check-text", response_model=AnalysisResult)
async def check_text(request: CheckTextRequest):
    start_time = time.time()
    
    # CRITICAL: Normalize smart quotes BEFORE any processing
    text = normalize_text_quotes(request.text.strip())
    
    if not text: raise HTTPException(status_code=400, detail="Empty text")
    
    # ============================================================
    # TRANSFORMER MODE (Advanced/AI)
    # ============================================================
    if request.model_type == "transformer":
        print(f"[API] Using TRANSFORMER mode (Advanced AI)")
        
        transformer_errors, corrected_text, success = check_with_transformer(text)
        
        if not success:
            print("[API] Transformer failed. Falling back to N-gram mode...")
            request.model_type = "ngram"
        else:
            spell_checker = get_spell_checker()
            spell_errors = spell_checker.check_text(text)
            print(f"[TRANSFORMER+SPELL] Found {len(spell_errors)} spelling errors")
            
            all_errors = []
            
            for e in transformer_errors:
                e['sentenceIndex'] = 0
                e['type'] = 'ai'
                all_errors.append(e)
            
            for e in spell_errors:
                e['sentenceIndex'] = 0
                if not overlaps_with_existing(e, all_errors):
                    all_errors.append(e)
            
            corrected_text = apply_corrections(text, all_errors)
            
            analyses = [SentenceAnalysis(
                index=0,
                original=text,
                corrected=corrected_text,
                errors=[GrammarError(**e) for e in all_errors],
                fluencyScore=95.0 if not all_errors else max(50, 95 - len(all_errors) * 5)
            )]
            
            # Dynamic confidence for Transformer
            fluency_score = analyses[0].fluencyScore
            word_count = len(tokenize(text))
            error_density = len(all_errors) / max(word_count, 1)
            error_penalty = min(0.2, error_density * 1.5)
            transformer_confidence = max(0.50, min(0.99, 0.92 * (fluency_score / 100.0) - error_penalty))
            
            return AnalysisResult(
                originalText=text,
                correctedText=corrected_text,
                errors=[GrammarError(**e) for e in all_errors],
                confidenceScore=round(transformer_confidence, 2),
                sentences=analyses,
                ngramMode="Transformer-AI",
                processingTimeMs=int((time.time() - start_time) * 1000)
            )
    
    # ============================================================
    # N-GRAM MODE (Basic/Statistical)
    # ============================================================
    print(f"[API] Using N-GRAM mode ({request.ngram})")
    
    ngram_order = 3
    use_hybrid = False
    
    if request.ngram == "bigram": 
        ngram_order = 2
        use_hybrid = False
    elif request.ngram == "hybrid" or request.ngram == "4gram": 
        ngram_order = 4
        use_hybrid = True
    
    spell_checker = get_spell_checker()
    punct_checker = get_punctuation_checker()
    rules_checker = get_grammar_rules_checker()
    
    rule_errors = rules_checker.check_text(text)
    
    sentences = split_sentences_with_positions(text)
    
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
        
        spells = spell_checker.check_text(sent)
        for e in spells:
            e['position']['start'] += start_offset
            e['position']['end'] += start_offset
            e['sentenceIndex'] = idx
            if not overlaps_with_existing(e, sent_errors):
                sent_errors.append(e)
                
        puncts = punct_checker.check_text(sent)
        for e in puncts:
            e['position']['start'] += start_offset
            e['position']['end'] += start_offset
            e['sentenceIndex'] = idx
            if not overlaps_with_existing(e, sent_errors):
                sent_errors.append(e)

        try:
            sem = get_semantic_checker().check_text(sent)
            for e in sem:
                e['position']['start'] += start_offset
                e['position']['end'] += start_offset
                e['sentenceIndex'] = idx
                if not overlaps_with_existing(e, sent_errors):
                    sent_errors.append(e)
        except: pass

        try:
            pos = get_pos_ngram_model().check_sentence(sent)
            for e in pos:
                e['position']['start'] += start_offset
                e['position']['end'] += start_offset
                e['sentenceIndex'] = idx
                if not overlaps_with_existing(e, sent_errors):
                    sent_errors.append(e)
        except: pass
        
        ngram_errors = check_with_ngram(sent, ngram_order, use_hybrid=use_hybrid)
        for e in ngram_errors:
            e['position']['start'] += start_offset
            e['position']['end'] += start_offset
            e['sentenceIndex'] = idx
            if not overlaps_with_existing(e, sent_errors):
                sent_errors.append(e)
        print(f"[N-GRAM RESULT] Sentence {idx}: Found {len(ngram_errors)} n-gram errors")
        
        unique = []
        seen = set()
        for e in sent_errors:
            k = (e['position']['start'], e['position']['end'], e['suggestion'])
            if k not in seen:
                seen.add(k)
                unique.append(e)
        
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
    
    # Calculate dynamic confidence score based on model and analysis
    # Base confidence by model type
    if request.ngram == "bigram":
        base_confidence = 0.65
    elif request.ngram == "trigram":
        base_confidence = 0.75
    elif request.ngram == "hybrid" or request.ngram == "4gram":
        base_confidence = 0.85
    else:
        base_confidence = 0.70
    
    # Factor in average fluency score
    avg_fluency = sum(a.fluencyScore for a in analyses) / len(analyses) if analyses else 50.0
    fluency_factor = avg_fluency / 100.0  # 0.0 to 1.0
    
    # Factor in error density (fewer errors = higher confidence)
    word_count = len(tokenize(text))
    error_density = len(all_errors) / max(word_count, 1)
    error_penalty = min(0.3, error_density * 2)  # Max 30% penalty
    
    # Final confidence: base * fluency factor - error penalty
    confidence = max(0.10, min(0.99, (base_confidence * 0.6 + fluency_factor * 0.4) - error_penalty))
    
    return AnalysisResult(
        originalText=text,
        correctedText=final_text,
        errors=[GrammarError(**e) for e in all_errors],
        confidenceScore=round(confidence, 2),
        sentences=analyses,
        ngramMode=request.ngram,
        processingTimeMs=int((time.time() - start_time) * 1000)
    )
