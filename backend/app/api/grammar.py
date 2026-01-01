"""
Grammar API endpoint.
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
from app.utils.sentence_splitter import split_sentences_with_positions
from app.utils.tokenizer import tokenize

router = APIRouter()

class CheckTextRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=50000)
    # Updated Regex to allow '4gram'
    ngram: str = Field("trigram", pattern="^(bigram|trigram|4gram)$") 

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
        # Overlap check
        if any(not (e <= ms or s >= me) for ms, me in modified): continue
        result = result[:s] + sugg + result[e:]
        modified.append((s, e))
    return result

def limit_corrections(errors: List[Dict], word_count: int) -> List[Dict]:
    if word_count == 0: return errors
    punct = [e for e in errors if e['type'] == 'punctuation']
    other = [e for e in errors if e['type'] != 'punctuation']
    
    if word_count < 5: return other + punct
    
    limit = max(1, int(word_count * 0.6)) # Slightly relaxed limit for better accuracy
    priority = {'spelling': 0, 'grammar': 1, 'semantic': 2, 'structure': 3}
    other.sort(key=lambda x: priority.get(x['type'], 4))
    
    return other[:limit] + punct

@router.post("/check-text", response_model=AnalysisResult)
async def check_text(request: CheckTextRequest):
    start_time = time.time()
    text = request.text.strip()
    if not text: raise HTTPException(status_code=400, detail="Empty text")
    
    # Determine N-Gram Order
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
            if not any(not (e['position']['end'] <= x['position']['start'] or e['position']['start'] >= x['position']['end']) for x in sent_errors):
                sent_errors.append(e)
                
        # Punctuation
        puncts = punct_checker.check_text(sent)
        for e in puncts:
            e['position']['start'] += start_offset
            e['position']['end'] += start_offset
            e['sentenceIndex'] = idx
            if not any(not (e['position']['end'] <= x['position']['start'] or e['position']['start'] >= x['position']['end']) for x in sent_errors):
                sent_errors.append(e)

        # Semantic
        try:
            sem = get_semantic_checker().check_text(sent)
            for e in sem:
                e['position']['start'] += start_offset
                e['position']['end'] += start_offset
                e['sentenceIndex'] = idx
                if not any(not (e['position']['end'] <= x['position']['start'] or e['position']['start'] >= x['position']['end']) for x in sent_errors):
                    sent_errors.append(e)
        except: pass

        # Structure (POS)
        try:
            pos = get_pos_ngram_model().check_sentence(sent)
            for e in pos:
                e['position']['start'] += start_offset
                e['position']['end'] += start_offset
                e['sentenceIndex'] = idx
                if not any(not (e['position']['end'] <= x['position']['start'] or e['position']['start'] >= x['position']['end']) for x in sent_errors):
                    sent_errors.append(e)
        except: pass
        
        # Deduplicate
        unique = []
        seen = set()
        for e in sent_errors:
            k = (e['position']['start'], e['position']['end'], e['suggestion'])
            if k not in seen:
                seen.add(k)
                unique.append(e)
        
        # Fluency Score (using the specific N-gram order)
        fluency = 100.0
        try:
            words = tokenize(sent)
            model = get_model()
            if model._trained:
                perp = model.perplexity(words, order=ngram_order)
                fluency = max(0, 100 - perp) # Simplified metric
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
