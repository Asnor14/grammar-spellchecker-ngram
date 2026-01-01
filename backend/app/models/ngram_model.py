"""
N-gram Language Model with Kneser-Ney Smoothing.
Supports Bigram, Trigram, and 4-gram (Quadgram) models.
"""

import math
from collections import Counter, defaultdict
from typing import Dict, List, Set, Tuple, Optional
import pickle

class NgramModel:
    """
    Interpolated N-gram Language Model (up to 4-grams).
    """
    
    # Interpolation weights
    # 4-gram mode: 0.4, 0.3, 0.2, 0.1
    # Trigram mode: 0.5, 0.3, 0.2
    # Bigram mode: 0.7, 0.3
    
    DISCOUNT = 0.75
    
    def __init__(self):
        self.unigram_counts: Counter = Counter()
        self.bigram_counts: Dict[str, Counter] = defaultdict(Counter)
        self.trigram_counts: Dict[Tuple[str, str], Counter] = defaultdict(Counter)
        self.fourgram_counts: Dict[Tuple[str, str, str], Counter] = defaultdict(Counter)
        
        self.vocabulary: Set[str] = set()
        self.total_words: int = 0
        
        # Continuation counts for Kneser-Ney
        self.bigram_continuation: Counter = Counter()
        self.trigram_continuation: Counter = Counter()
        self.fourgram_continuation: Counter = Counter()
        
        self._trained = False
    
    def train(self, corpus: List[List[str]]) -> None:
        """Train the model on a corpus."""
        for sentence in corpus:
            if len(sentence) < 1: continue
            
            words = [w.lower() for w in sentence if w.isalpha() or "'" in w]
            
            for i, word in enumerate(words):
                self.unigram_counts[word] += 1
                self.vocabulary.add(word)
                self.total_words += 1
                
                # Bigrams
                if i >= 1:
                    prev = words[i - 1]
                    self.bigram_counts[prev][word] += 1
                    self.bigram_continuation[word] += 1
                
                # Trigrams
                if i >= 2:
                    context = (words[i-2], words[i-1])
                    self.trigram_counts[context][word] += 1
                    self.trigram_continuation[word] += 1
                
                # 4-grams
                if i >= 3:
                    context = (words[i-3], words[i-2], words[i-1])
                    self.fourgram_counts[context][word] += 1
                    self.fourgram_continuation[word] += 1
        
        self._trained = True
    
    def train_from_text(self, text: str) -> None:
        from app.utils.sentence_splitter import split_sentences
        from app.utils.tokenizer import tokenize
        sentences = split_sentences(text)
        corpus = [tokenize(s) for s in sentences]
        self.train(corpus)
    
    def unigram_probability(self, word: str) -> float:
        word = word.lower()
        if self.total_words == 0: return 1e-10
        count = self.unigram_counts.get(word, 0)
        if count == 0: return 1.0 / (self.total_words + len(self.vocabulary))
        return count / self.total_words
    
    def bigram_probability(self, word: str, context: str) -> float:
        word = word.lower()
        context = context.lower()
        context_count = sum(self.bigram_counts[context].values())
        if context_count == 0: return self.unigram_probability(word)
        
        word_count = self.bigram_counts[context].get(word, 0)
        discounted = max(word_count - self.DISCOUNT, 0) / context_count
        
        unique_contexts = len(self.bigram_counts[context])
        lambda_weight = (self.DISCOUNT * unique_contexts) / context_count
        
        # Approximate continuation probability
        total_types = len(self.bigram_continuation) or 1
        p_continuation = self.bigram_continuation.get(word, 0) / total_types
        
        return discounted + lambda_weight * max(p_continuation, 1e-10)
    
    def trigram_probability(self, word: str, c1: str, c2: str) -> float:
        word = word.lower()
        c1, c2 = c1.lower(), c2.lower()
        context = (c1, c2)
        
        context_count = sum(self.trigram_counts[context].values())
        if context_count == 0: return self.bigram_probability(word, c2)
        
        word_count = self.trigram_counts[context].get(word, 0)
        discounted = max(word_count - self.DISCOUNT, 0) / context_count
        
        unique_contexts = len(self.trigram_counts[context])
        lambda_weight = (self.DISCOUNT * unique_contexts) / context_count
        
        return discounted + lambda_weight * self.bigram_probability(word, c2)

    def fourgram_probability(self, word: str, c1: str, c2: str, c3: str) -> float:
        word = word.lower()
        c1, c2, c3 = c1.lower(), c2.lower(), c3.lower()
        context = (c1, c2, c3)
        
        context_count = sum(self.fourgram_counts[context].values())
        if context_count == 0: return self.trigram_probability(word, c2, c3)
        
        word_count = self.fourgram_counts[context].get(word, 0)
        discounted = max(word_count - self.DISCOUNT, 0) / context_count
        
        unique_contexts = len(self.fourgram_counts[context])
        lambda_weight = (self.DISCOUNT * unique_contexts) / context_count
        
        return discounted + lambda_weight * self.trigram_probability(word, c2, c3)
    
    def interpolated_probability(self, word: str, context: List[str], order: int = 3) -> float:
        """
        Calculate probability based on N-gram order (2, 3, or 4).
        """
        p_uni = self.unigram_probability(word)
        if len(context) < 1: return p_uni
        
        p_bi = self.bigram_probability(word, context[-1])
        
        if order == 2 or len(context) < 2:
            return 0.7 * p_bi + 0.3 * p_uni
            
        p_tri = self.trigram_probability(word, context[-2], context[-1])
        
        if order == 3 or len(context) < 3:
            return 0.5 * p_tri + 0.3 * p_bi + 0.2 * p_uni
            
        # 4-gram logic
        p_four = self.fourgram_probability(word, context[-3], context[-2], context[-1])
        return 0.4 * p_four + 0.3 * p_tri + 0.2 * p_bi + 0.1 * p_uni
    
    def sentence_probability(self, words: List[str], order: int = 3) -> float:
        if not words: return 0.0
        log_prob = 0.0
        for i, word in enumerate(words):
            # Grab up to 3 previous words for 4-gram context
            context = words[max(0, i-3):i]
            prob = self.interpolated_probability(word, context, order)
            log_prob += math.log(max(prob, 1e-10))
        return log_prob
    
    def perplexity(self, words: List[str], order: int = 3) -> float:
        if not words: return float('inf')
        log_prob = self.sentence_probability(words, order)
        return math.exp(-log_prob / len(words))
    
    def get_word_candidates(self, word: str, context: List[str], max_candidates: int = 5, order: int = 3) -> List[Tuple[str, float]]:
        from app.utils.edit_distance import generate_edits_1
        
        word = word.lower()
        candidates = {word}
        
        # Simple edit distance 1
        for edit in generate_edits_1(word):
            if edit in self.vocabulary:
                candidates.add(edit)
        
        scored = []
        for cand in candidates:
            prob = self.interpolated_probability(cand, context, order)
            scored.append((cand, prob))
        
        scored.sort(key=lambda x: x[1], reverse=True)
        return scored[:max_candidates]

    def save(self, filepath: str) -> None:
        with open(filepath, 'wb') as f:
            pickle.dump({
                'unigram': self.unigram_counts,
                'bigram': dict(self.bigram_counts),
                'trigram': dict(self.trigram_counts),
                'fourgram': dict(self.fourgram_counts),
                'vocab': self.vocabulary,
                'total': self.total_words
            }, f)

    def load(self, filepath: str) -> None:
        with open(filepath, 'rb') as f:
            data = pickle.load(f)
        self.unigram_counts = data['unigram']
        self.bigram_counts = defaultdict(Counter, data['bigram'])
        self.trigram_counts = defaultdict(Counter, data['trigram'])
        self.fourgram_counts = defaultdict(Counter, data.get('fourgram', {})) # Backward compat
        self.vocabulary = data['vocab']
        self.total_words = data['total']
        self._trained = True

_model = None
def get_model():
    global _model
    if _model is None: _model = NgramModel()
    return _model

def initialize_model():
    global _model
    model = NgramModel()
    import nltk
    try:
        from nltk.corpus import brown, gutenberg
        model.train(list(brown.sents()))
        model.train(list(gutenberg.sents()))
        print(f"Model trained. Vocab: {len(model.vocabulary)}")
    except Exception as e:
        print(f"Model training fallback: {e}")
    _model = model
    return model
