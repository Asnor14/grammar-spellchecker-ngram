"""
Spell Safety Filter - Post-Transformer Validation Layer

PURPOSE:
This module provides a deterministic safety layer that validates transformer
output against the corpus-derived vocabulary (Brown + Gutenberg). It catches
spelling artifacts introduced by probabilistic token generation (e.g., "becausee").

DESIGN PHILOSOPHY:
- Does NOT modify existing models or behavior
- Does NOT use neural networks or external APIs  
- Reuses existing vocabulary and n-gram scoring
- Acts as a FINAL safety net before returning output

PIPELINE:
Transformer Output → Tokenization → Word Validation → Correction → Final Output
"""

from typing import List, Tuple, Optional
import re


class SpellSafetyFilter:
    """
    Validates transformer output against corpus vocabulary.
    Catches and fixes spelling artifacts from probabilistic generation.
    """
    
    def __init__(self, vocabulary: set, word_frequencies: dict = None):
        """
        Initialize with existing vocabulary from n-gram models.
        
        Args:
            vocabulary: Set of valid words from corpus (Brown + Gutenberg)
            word_frequencies: Optional frequency dict for ranking corrections
        """
        self.vocabulary = vocabulary
        self.word_frequencies = word_frequencies or {}
        
        # Common valid contractions that should never be flagged
        self.valid_contractions = {
            "don't", "doesn't", "didn't", "won't", "can't", "couldn't", 
            "wouldn't", "shouldn't", "isn't", "aren't", "wasn't", "weren't",
            "hasn't", "haven't", "hadn't", "it's", "that's", "what's",
            "who's", "there's", "here's", "let's", "i'm", "you're", "we're",
            "they're", "he's", "she's", "i've", "you've", "we've", "they've",
            "i'd", "you'd", "he'd", "she'd", "we'd", "they'd", "i'll",
            "you'll", "he'll", "she'll", "we'll", "they'll"
        }
    
    def validate_and_correct(self, text: str) -> str:
        """
        Main entry point: Validate transformer output and fix spelling artifacts.
        
        This is the ONLY function that needs to be called after transformer inference.
        It preserves punctuation and casing while fixing invalid words.
        
        Args:
            text: Transformer-generated text
            
        Returns:
            Validated text with spelling artifacts fixed
        """
        if not text or not text.strip():
            return text
            
        # Tokenize preserving positions for reconstruction
        tokens = self._tokenize_with_positions(text)
        
        corrected_text = text
        offset = 0  # Track position changes from corrections
        
        for word, start, end in tokens:
            # Skip punctuation, numbers, contractions
            if not word.isalpha():
                continue
            if "'" in word or word.lower() in self.valid_contractions:
                continue
            
            # Check if word is valid
            if not self._is_valid_word(word):
                # Find best correction using existing vocabulary + n-gram scoring
                correction = self._get_best_correction(word)
                
                if correction and correction.lower() != word.lower():
                    # Preserve original casing
                    correction = self._preserve_casing(word, correction)
                    
                    # Apply correction
                    adj_start = start + offset
                    adj_end = end + offset
                    corrected_text = corrected_text[:adj_start] + correction + corrected_text[adj_end:]
                    
                    # Update offset for subsequent corrections
                    offset += len(correction) - len(word)
        
        return corrected_text
    
    def _tokenize_with_positions(self, text: str) -> List[Tuple[str, int, int]]:
        """
        Tokenize text and return words with their start/end positions.
        """
        tokens = []
        # Match words (including contractions) and track positions
        for match in re.finditer(r"\b[\w']+\b", text):
            tokens.append((match.group(), match.start(), match.end()))
        return tokens
    
    def _is_valid_word(self, word: str) -> bool:
        """
        Check if word exists in corpus vocabulary.
        """
        word_lower = word.lower()
        
        # Check vocabulary
        if word_lower in self.vocabulary:
            return True
            
        # Allow single letters and numbers
        if len(word) <= 1 or word.isdigit():
            return True
            
        return False
    
    def _get_best_correction(self, word: str, max_distance: int = 2) -> Optional[str]:
        """
        Find best correction using edit distance and frequency ranking.
        Reuses existing n-gram vocabulary for candidate generation.
        
        Args:
            word: Invalid word to correct
            max_distance: Maximum Levenshtein distance (default: 2)
            
        Returns:
            Best correction or None if no suitable candidate found
        """
        word_lower = word.lower()
        candidates = []
        
        # Generate candidates within edit distance
        for vocab_word in self.vocabulary:
            # Quick length filter to avoid expensive computation
            if abs(len(vocab_word) - len(word_lower)) > max_distance:
                continue
                
            distance = self._levenshtein_distance(word_lower, vocab_word)
            if distance <= max_distance:
                # Score by frequency (higher = better)
                freq = self.word_frequencies.get(vocab_word, 1)
                candidates.append((vocab_word, distance, freq))
        
        if not candidates:
            return None
            
        # Sort by: 1) edit distance (lower better), 2) frequency (higher better)
        candidates.sort(key=lambda x: (x[0], -x[2]))
        
        return candidates[0][0]
    
    def _levenshtein_distance(self, s1: str, s2: str) -> int:
        """
        Compute Levenshtein edit distance between two strings.
        Standard dynamic programming implementation.
        """
        if len(s1) < len(s2):
            return self._levenshtein_distance(s2, s1)
            
        if len(s2) == 0:
            return len(s1)
            
        previous_row = range(len(s2) + 1)
        
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row
            
        return previous_row[-1]
    
    def _preserve_casing(self, original: str, correction: str) -> str:
        """
        Preserve the casing pattern of original word in correction.
        """
        if original.isupper():
            return correction.upper()
        elif original[0].isupper():
            return correction.capitalize()
        else:
            return correction.lower()


# ============================================================
# SINGLETON INSTANCE - Initialized with existing n-gram vocab
# ============================================================

_spell_safety_filter: Optional[SpellSafetyFilter] = None


def get_spell_safety_filter() -> SpellSafetyFilter:
    """
    Get or create the spell safety filter using existing n-gram vocabulary.
    
    This reuses the vocabulary already loaded by the n-gram model,
    ensuring no additional memory or loading overhead.
    """
    global _spell_safety_filter
    
    if _spell_safety_filter is None:
        # Import existing n-gram model to reuse its vocabulary
        from app.models.ngram_model import get_model
        
        model = get_model()
        vocabulary = model.vocabulary if model._trained else set()
        frequencies = dict(model.word_counts) if model._trained else {}
        
        _spell_safety_filter = SpellSafetyFilter(vocabulary, frequencies)
        print(f"[SPELL-SAFETY] Initialized with {len(vocabulary)} vocabulary words")
    
    return _spell_safety_filter


def validate_transformer_output(text: str) -> str:
    """
    MAIN API: Validate and correct transformer output.
    
    This is the single function to call after transformer inference.
    It ensures spelling artifacts like "becausee" are caught and fixed.
    
    Usage in transformer_model.py:
        from app.models.spell_safety_filter import validate_transformer_output
        corrected_text = validate_transformer_output(transformer_output)
    
    Args:
        text: Raw transformer output
        
    Returns:
        Validated text with spelling artifacts fixed
    """
    filter_instance = get_spell_safety_filter()
    return filter_instance.validate_and_correct(text)
