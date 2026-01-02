"""
Hybrid Scorer for N-gram System.
Combines scores from Word N-gram, Character N-gram, and 4-gram models.
"""

from typing import Dict, List, Optional
from app.models.ngram_model import NgramModel
from app.models.char_ngram_model import CharNgramModel

class HybridScorer:
    """
    Combines probabilistic scores from multiple models to rank correction candidates.
    """
    
    def __init__(self, 
                 word_model: NgramModel, 
                 char_model: Optional[CharNgramModel] = None,
                 weights: Optional[Dict[str, float]] = None):
        
        self.word_model = word_model
        self.char_model = char_model
        
        # Default weights
        self.weights = {
            'word': 0.6,
            'char': 0.3, # Higher weight for spelling correction
            'fourgram': 0.1
        }
        if weights:
            self.weights.update(weights)

    def score_candidate(self, 
                       candidate: str, 
                       context: List[str], 
                       original_word: Optional[str] = None) -> float:
        """
        Calculate final weighted score for a candidate word.
        Returns a normalized score (higher is better).
        """
        score = 0.0
        
        # 1. Word N-gram Score (Fluency/Grammar)
        # Using trigram probability (standard)
        word_prob = self.word_model.interpolated_probability(candidate, context, order=3)
        score += self.weights['word'] * word_prob
        
        # 2. Character N-gram Score (Spelling Validity)
        if self.char_model:
            # Char model returns log-prob, convert to linear scale roughly [0, 1]
            # or treat as feature. Here we use exponential to make it comparable
            char_log_prob = self.char_model.score_word(candidate)
            # Normalize: typical log probs are negative. 
            # Exp(log_prob) gives probability [0, 1]
            char_prob = 0.0
            try:
                char_prob = pow(2.718, char_log_prob) 
            except:
                char_prob = 0.0
                
            score += self.weights['char'] * char_prob
            
        # 3. 4-gram Score (Long Context) - if enabled/available
        # Check if context allows for 4-gram checks
        if len(context) >= 3:
             fourgram_prob = self.word_model.interpolated_probability(candidate, context, order=4)
             score += self.weights['fourgram'] * fourgram_prob
             
        # Bonus: Edit Distance penalty if original_word provided
        # This keeps corrections close to original
        if original_word:
            from app.utils.edit_distance import levenshtein_distance
            dist = levenshtein_distance(original_word.lower(), candidate.lower())
            if dist > 0:
                # Penalty factor
                score = score * (1.0 / (dist + 1))
                
        return score

    def rank_candidates(self, 
                       candidates: List[str], 
                       context: List[str],
                       original_word: Optional[str] = None) -> List[str]:
        """
        Rank a list of candidates and return them sorted by score.
        """
        scored = []
        for cand in candidates:
            score = self.score_candidate(cand, context, original_word)
            scored.append((cand, score))
            
        # Sort desc
        scored.sort(key=lambda x: x[1], reverse=True)
        return [s[0] for s in scored]
