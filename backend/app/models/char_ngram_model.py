"""
Character-level N-gram Model.
Supports 3-gram, 4-gram, and 5-gram analysis for spelling and morphological validity.
"""

from collections import Counter, defaultdict
from typing import Dict, List, Set, Tuple
import math

class CharNgramModel:
    """
    Character-level N-gram model with smoothing.
    Evaluates the likelihood of character sequences (spelling validity).
    """
    
    def __init__(self, order: int = 5):
        self.order = order
        self.ngrams: Dict[int, Dict[str, Counter]] = defaultdict(lambda: defaultdict(Counter))
        self.total_counts: Dict[int, int] = defaultdict(int)
        self.vocabulary: Set[str] = set()
        self._trained = False
        
    def train(self, words: List[str]) -> None:
        """
        Train the character model on a list of words.
        """
        for word in words:
            # Add boundary markers
            padded = f"^{word}$"
            self.vocabulary.update(set(padded))
            
            # Train for all orders from 1 to self.order
            for n in range(1, self.order + 1):
                for i in range(len(padded) - n + 1):
                    gram = padded[i:i+n]
                    context = gram[:-1]
                    char = gram[-1]
                    
                    self.ngrams[n][context][char] += 1
                    self.total_counts[n] += 1
                    
        self._trained = True

    def get_probability(self, char: str, context: str, n: int) -> float:
        """
        Get probability of a character given its context using simple interpolation/smoothing.
        """
        # Witten-Bell Smoothing equivalent or Jelinek-Mercer
        # Using simple +0.5 smoothing for now
        
        counts = self.ngrams[n][context]
        total_context = sum(counts.values())
        
        if total_context == 0:
            # Backoff to lower order
            if n > 1:
                return self.get_probability(char, context[1:], n - 1)
            else:
                return 1.0 / (len(self.vocabulary) + 1)
                
        count = counts.get(char, 0)
        # Simple Add-k smoothing
        k = 0.5
        prob = (count + k) / (total_context + k * len(self.vocabulary))
        return prob

    def score_word(self, word: str) -> float:
        """
        Calculate normalized log-probability score for a word.
        Higher is better.
        """
        if not self._trained:
            return -100.0
            
        padded = f"^{word}$"
        log_prob = 0.0
        
        for i in range(1, len(padded)):
            char = padded[i]
            # Use max order available context
            n = min(self.order, i + 1)
            context = padded[i - n + 1 : i]
            
            prob = self.get_probability(char, context, n)
            log_prob += math.log(max(prob, 1e-10))
            
        # Normalize by length to avoid penalizing long words
        return log_prob / len(word)

_char_model = None

def get_char_model() -> CharNgramModel:
    global _char_model
    if _char_model is None:
        _char_model = CharNgramModel()
    return _char_model

def initialize_char_model(words: List[str]) -> CharNgramModel:
    global _char_model
    model = CharNgramModel()
    model.train(words)
    _char_model = model
    return model
