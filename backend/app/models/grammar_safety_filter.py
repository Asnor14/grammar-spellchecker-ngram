"""
Grammar Safety Filter - Post-Transformer Grammar Validation Layer

PURPOSE:
This module provides a statistical grammar validation layer that uses
n-gram probabilities to fix common grammatical errors (agreement, tense, adverbs).
It does NOT use hard grammar rules - only statistical likelihood.

DESIGN PHILOSOPHY:
- Does NOT modify existing models or behavior
- Does NOT use syntax trees or transformers
- Uses ONLY n-gram probability scoring from existing model
- Acts as a FINAL grammar safety net before returning output

PIPELINE:
Transformer Output → Spell-Safety → GRAMMAR-SAFETY → Final Output
"""

from typing import List, Tuple, Optional, Dict
import re


class GrammarSafetyFilter:
    """
    Validates transformer output using n-gram probability scoring.
    Fixes agreement and tense errors by comparing variant probabilities.
    """
    
    # Grammar-sensitive patterns: (pattern_words, variants)
    # Each entry defines a word and its grammatical alternatives
    GRAMMAR_PATTERNS: Dict[str, List[str]] = {
        # Negation + auxiliary
        "don't": ["don't", "doesn't", "didn't"],
        "doesn't": ["don't", "doesn't", "didn't"],
        "didn't": ["don't", "doesn't", "didn't"],
        
        # Have/Has
        "have": ["have", "has", "had"],
        "has": ["have", "has", "had"],
        "had": ["have", "has", "had"],
        
        # Was/Were
        "was": ["was", "were"],
        "were": ["was", "were"],
        
        # Is/Are
        "is": ["is", "are"],
        "are": ["is", "are"],
        
        # Go variants
        "go": ["go", "goes", "went", "going"],
        "goes": ["go", "goes", "went", "going"],
        "went": ["go", "goes", "went", "going"],
        
        # Do variants
        "do": ["do", "does", "did"],
        "does": ["do", "does", "did"],
        "did": ["do", "does", "did"],
        
        # Good/Well (adverb confusion)
        "good": ["good", "well"],
        "well": ["good", "well"],
        
        # Like after auxiliary (didn't like vs didn't liked)
        "like": ["like", "liked", "likes"],
        "liked": ["like", "liked", "likes"],
        
        # Fix after only (only fix vs only fixes)
        "fix": ["fix", "fixes", "fixed"],
        "fixes": ["fix", "fixes", "fixed"],
        
        # Help variants
        "help": ["help", "helps", "helped"],
        "helps": ["help", "helps", "helped"],
        
        # Say variants
        "say": ["say", "says", "said"],
        "says": ["say", "says", "said"],
        
        # Bring variants
        "bring": ["bring", "brings", "brought"],
        "brought": ["bring", "brings", "brought"],
        
        # Wait variants
        "wait": ["wait", "waits", "waited"],
        "waited": ["wait", "waits", "waited"],
    }
    
    # Context window for n-gram scoring
    CONTEXT_WINDOW = 2  # Look at 2 words before and after
    
    # Minimum probability improvement ratio to trigger replacement
    MIN_IMPROVEMENT_RATIO = 1.5
    
    def __init__(self, ngram_model):
        """
        Initialize with existing n-gram model for probability scoring.
        
        Args:
            ngram_model: The existing trained n-gram model
        """
        self.model = ngram_model
    
    def validate_and_correct(self, text: str) -> str:
        """
        Main entry point: Validate grammar using n-gram probabilities.
        
        This replaces grammar-sensitive words ONLY if an alternative
        has significantly higher n-gram probability in context.
        
        Args:
            text: Text to validate (after spell-safety)
            
        Returns:
            Text with grammatical fixes applied
        """
        if not text or not text.strip():
            return text
        
        # Tokenize
        tokens = self._tokenize(text)
        words = [t[0].lower() for t in tokens]
        
        corrected_text = text
        offset = 0
        
        for i, (word, start, end) in enumerate(tokens):
            word_lower = word.lower()
            
            # Check if word is grammar-sensitive
            if word_lower not in self.GRAMMAR_PATTERNS:
                continue
            
            # Get context window
            context_before = words[max(0, i - self.CONTEXT_WINDOW):i]
            context_after = words[i + 1:i + 1 + self.CONTEXT_WINDOW]
            
            # Get variants to compare
            variants = self.GRAMMAR_PATTERNS[word_lower]
            
            # Score each variant
            best_variant = word_lower
            best_score = self._score_variant(word_lower, context_before, context_after)
            
            for variant in variants:
                if variant == word_lower:
                    continue
                    
                score = self._score_variant(variant, context_before, context_after)
                
                # Replace only if significantly better
                if score > best_score * self.MIN_IMPROVEMENT_RATIO:
                    best_variant = variant
                    best_score = score
            
            # Apply correction if better variant found
            if best_variant != word_lower:
                # Preserve casing
                corrected_variant = self._preserve_casing(word, best_variant)
                
                adj_start = start + offset
                adj_end = end + offset
                corrected_text = corrected_text[:adj_start] + corrected_variant + corrected_text[adj_end:]
                
                offset += len(corrected_variant) - len(word)
        
        return corrected_text
    
    def _tokenize(self, text: str) -> List[Tuple[str, int, int]]:
        """Tokenize text with positions."""
        tokens = []
        for match in re.finditer(r"\b[\w']+\b", text):
            tokens.append((match.group(), match.start(), match.end()))
        return tokens
    
    def _score_variant(self, word: str, context_before: List[str], context_after: List[str]) -> float:
        """
        Score a word variant using n-gram probability.
        
        Uses both forward and backward context for bidirectional scoring.
        """
        if not self.model._trained:
            return 0.0
        
        score = 0.0
        
        # Forward probability: P(word | context_before)
        if context_before:
            forward_prob = self.model.interpolated_probability(
                word, 
                context_before[-2:],  # Last 2 words
                order=3
            )
            score += forward_prob
        
        # Backward probability: P(next_word | word + context)
        if context_after:
            context_with_word = (context_before[-1:] if context_before else []) + [word]
            backward_prob = self.model.interpolated_probability(
                context_after[0],
                context_with_word,
                order=3
            )
            score += backward_prob
        
        return score
    
    def _preserve_casing(self, original: str, correction: str) -> str:
        """Preserve the casing pattern of original word."""
        if original.isupper():
            return correction.upper()
        elif original[0].isupper():
            return correction.capitalize()
        else:
            return correction.lower()


# ============================================================
# SINGLETON INSTANCE - Initialized with existing n-gram model
# ============================================================

_grammar_safety_filter: Optional[GrammarSafetyFilter] = None


def get_grammar_safety_filter() -> GrammarSafetyFilter:
    """
    Get or create the grammar safety filter using existing n-gram model.
    """
    global _grammar_safety_filter
    
    if _grammar_safety_filter is None:
        from app.models.ngram_model import get_model
        
        model = get_model()
        _grammar_safety_filter = GrammarSafetyFilter(model)
        print("[GRAMMAR-SAFETY] Initialized with n-gram probability scoring")
    
    return _grammar_safety_filter


def validate_transformer_grammar(text: str) -> str:
    """
    MAIN API: Validate grammar using n-gram probabilities.
    
    This is the single function to call after spell-safety filtering.
    It fixes agreement and tense errors by comparing variant probabilities.
    
    Usage in transformer_model.py:
        from app.models.grammar_safety_filter import validate_transformer_grammar
        corrected_text = validate_transformer_grammar(corrected_text)
    
    Args:
        text: Text after spell-safety filtering
        
    Returns:
        Text with grammatical fixes applied
    """
    filter_instance = get_grammar_safety_filter()
    return filter_instance.validate_and_correct(text)
