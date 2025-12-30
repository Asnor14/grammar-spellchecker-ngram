"""
N-gram Language Model with Kneser-Ney Smoothing.
Implements interpolated trigram model for grammar checking.
"""

import math
from collections import Counter, defaultdict
from typing import Dict, List, Set, Tuple, Optional
import os


class NgramModel:
    """
    Interpolated N-gram Language Model with Kneser-Ney smoothing.
    
    Uses the interpolation formula:
    P(w_i | w_{i-2}, w_{i-1}) = 0.5 * P_trigram + 0.3 * P_bigram + 0.2 * P_unigram
    """
    
    # Interpolation weights
    TRIGRAM_WEIGHT = 0.5
    BIGRAM_WEIGHT = 0.3
    UNIGRAM_WEIGHT = 0.2
    
    # Kneser-Ney discount
    DISCOUNT = 0.75
    
    def __init__(self):
        self.unigram_counts: Counter = Counter()
        self.bigram_counts: Dict[str, Counter] = defaultdict(Counter)
        self.trigram_counts: Dict[Tuple[str, str], Counter] = defaultdict(Counter)
        
        self.vocabulary: Set[str] = set()
        self.total_words: int = 0
        
        # Continuation counts for Kneser-Ney
        self.bigram_continuation: Counter = Counter()  # How many bigrams end with word
        self.trigram_continuation: Counter = Counter()  # How many trigrams end with word
        
        self._trained = False
    
    def train(self, corpus: List[List[str]]) -> None:
        """
        Train the model on a corpus of tokenized sentences.
        
        Args:
            corpus: List of sentences, each sentence is a list of tokens
        """
        for sentence in corpus:
            if len(sentence) < 1:
                continue
            
            words = [w.lower() for w in sentence if w.isalpha() or "'" in w]
            
            for i, word in enumerate(words):
                self.unigram_counts[word] += 1
                self.vocabulary.add(word)
                self.total_words += 1
                
                # Bigrams
                if i >= 1:
                    prev_word = words[i - 1]
                    self.bigram_counts[prev_word][word] += 1
                    self.bigram_continuation[word] += 1
                
                # Trigrams
                if i >= 2:
                    prev_prev = words[i - 2]
                    prev_word = words[i - 1]
                    self.trigram_counts[(prev_prev, prev_word)][word] += 1
                    self.trigram_continuation[word] += 1
        
        self._trained = True
    
    def train_from_text(self, text: str) -> None:
        """
        Train from raw text.
        
        Args:
            text: Raw text string
        """
        from app.utils.sentence_splitter import split_sentences
        from app.utils.tokenizer import tokenize
        
        sentences = split_sentences(text)
        corpus = [tokenize(s) for s in sentences]
        self.train(corpus)
    
    def unigram_probability(self, word: str) -> float:
        """
        Calculate unigram probability P(word).
        
        Args:
            word: Target word
            
        Returns:
            Probability
        """
        word = word.lower()
        if self.total_words == 0:
            return 1e-10
        
        count = self.unigram_counts.get(word, 0)
        if count == 0:
            # Smoothing for unknown words
            return 1.0 / (self.total_words + len(self.vocabulary))
        
        return count / self.total_words
    
    def bigram_probability(self, word: str, context: str) -> float:
        """
        Calculate bigram probability P(word | context) with Kneser-Ney.
        
        Args:
            word: Target word
            context: Previous word
            
        Returns:
            Probability
        """
        word = word.lower()
        context = context.lower()
        
        context_count = sum(self.bigram_counts[context].values())
        
        if context_count == 0:
            return self.unigram_probability(word)
        
        word_count = self.bigram_counts[context].get(word, 0)
        
        # Kneser-Ney smoothing
        discounted = max(word_count - self.DISCOUNT, 0) / context_count
        
        # Continuation probability
        unique_contexts = len(self.bigram_counts[context])
        lambda_weight = (self.DISCOUNT * unique_contexts) / context_count
        
        continuation = self.bigram_continuation.get(word, 0)
        total_bigram_types = sum(len(v) for v in self.bigram_counts.values())
        p_continuation = continuation / max(total_bigram_types, 1)
        
        return discounted + lambda_weight * max(p_continuation, 1e-10)
    
    def trigram_probability(self, word: str, context1: str, context2: str) -> float:
        """
        Calculate trigram probability P(word | context1, context2) with Kneser-Ney.
        
        Args:
            word: Target word
            context1: Word at position i-2
            context2: Word at position i-1
            
        Returns:
            Probability
        """
        word = word.lower()
        context1 = context1.lower()
        context2 = context2.lower()
        
        context = (context1, context2)
        context_count = sum(self.trigram_counts[context].values())
        
        if context_count == 0:
            return self.bigram_probability(word, context2)
        
        word_count = self.trigram_counts[context].get(word, 0)
        
        # Kneser-Ney smoothing
        discounted = max(word_count - self.DISCOUNT, 0) / context_count
        
        # Continuation probability
        unique_contexts = len(self.trigram_counts[context])
        lambda_weight = (self.DISCOUNT * unique_contexts) / context_count
        
        p_lower = self.bigram_probability(word, context2)
        
        return discounted + lambda_weight * p_lower
    
    def interpolated_probability(
        self, 
        word: str, 
        context: List[str],
        use_trigram: bool = True
    ) -> float:
        """
        Calculate interpolated probability using the formula:
        P = 0.5 * P_trigram + 0.3 * P_bigram + 0.2 * P_unigram
        
        Args:
            word: Target word
            context: List of context words (most recent last)
            use_trigram: If True, use trigram model; if False, use bigram only
            
        Returns:
            Interpolated probability
        """
        p_unigram = self.unigram_probability(word)
        
        if len(context) < 1:
            return p_unigram
        
        p_bigram = self.bigram_probability(word, context[-1])
        
        if not use_trigram or len(context) < 2:
            # Bigram interpolation
            return 0.7 * p_bigram + 0.3 * p_unigram
        
        p_trigram = self.trigram_probability(word, context[-2], context[-1])
        
        return (
            self.TRIGRAM_WEIGHT * p_trigram +
            self.BIGRAM_WEIGHT * p_bigram +
            self.UNIGRAM_WEIGHT * p_unigram
        )
    
    def sentence_probability(self, words: List[str], use_trigram: bool = True) -> float:
        """
        Calculate the probability of a sentence.
        
        Args:
            words: List of word tokens
            use_trigram: Whether to use trigram model
            
        Returns:
            Log probability of the sentence
        """
        if not words:
            return 0.0
        
        log_prob = 0.0
        
        for i, word in enumerate(words):
            context = words[max(0, i-2):i]
            prob = self.interpolated_probability(word, context, use_trigram)
            log_prob += math.log(max(prob, 1e-10))
        
        return log_prob
    
    def perplexity(self, words: List[str], use_trigram: bool = True) -> float:
        """
        Calculate perplexity of a sentence.
        
        Args:
            words: List of word tokens
            use_trigram: Whether to use trigram model
            
        Returns:
            Perplexity (lower is better)
        """
        if not words:
            return float('inf')
        
        log_prob = self.sentence_probability(words, use_trigram)
        return math.exp(-log_prob / len(words))
    
    def get_word_candidates(
        self, 
        word: str, 
        context: List[str],
        max_candidates: int = 5,
        use_trigram: bool = True
    ) -> List[Tuple[str, float]]:
        """
        Get candidate corrections for a word based on context.
        
        Args:
            word: Current word
            context: Context words
            max_candidates: Maximum candidates to return
            use_trigram: Whether to use trigram model
            
        Returns:
            List of (candidate, probability) tuples
        """
        from app.utils.edit_distance import generate_edits_1, generate_edits_2
        
        word = word.lower()
        
        # Generate candidates within edit distance 2
        candidates = set()
        candidates.add(word)
        
        edits1 = generate_edits_1(word)
        for edit in edits1:
            if edit in self.vocabulary:
                candidates.add(edit)
        
        edits2 = generate_edits_2(word)
        for edit in edits2:
            if edit in self.vocabulary:
                candidates.add(edit)
        
        # Score candidates
        scored = []
        for candidate in candidates:
            prob = self.interpolated_probability(candidate, context, use_trigram)
            scored.append((candidate, prob))
        
        # Sort by probability
        scored.sort(key=lambda x: x[1], reverse=True)
        
        return scored[:max_candidates]
    
    def is_word_likely(
        self, 
        word: str, 
        context: List[str],
        threshold: float = 0.5,
        use_trigram: bool = True
    ) -> bool:
        """
        Check if a word is likely given its context.
        
        Args:
            word: Word to check
            context: Context words
            threshold: Probability threshold (relative to best candidate)
            use_trigram: Whether to use trigram model
            
        Returns:
            True if the word is likely in context
        """
        candidates = self.get_word_candidates(word, context, max_candidates=3, use_trigram=use_trigram)
        
        if not candidates:
            return True
        
        word = word.lower()
        word_prob = self.interpolated_probability(word, context, use_trigram)
        best_prob = candidates[0][1]
        
        # Word is likely if its probability is at least threshold * best
        return word_prob >= threshold * best_prob
    
    def in_vocabulary(self, word: str) -> bool:
        """
        Check if a word is in the vocabulary.
        
        Args:
            word: Word to check
            
        Returns:
            True if word is in vocabulary
        """
        return word.lower() in self.vocabulary
    
    def save(self, filepath: str) -> None:
        """Save model to file."""
        import pickle
        with open(filepath, 'wb') as f:
            pickle.dump({
                'unigram_counts': dict(self.unigram_counts),
                'bigram_counts': {k: dict(v) for k, v in self.bigram_counts.items()},
                'trigram_counts': {k: dict(v) for k, v in self.trigram_counts.items()},
                'vocabulary': self.vocabulary,
                'total_words': self.total_words,
                'bigram_continuation': dict(self.bigram_continuation),
                'trigram_continuation': dict(self.trigram_continuation),
            }, f)
    
    def load(self, filepath: str) -> None:
        """Load model from file."""
        import pickle
        with open(filepath, 'rb') as f:
            data = pickle.load(f)
        
        self.unigram_counts = Counter(data['unigram_counts'])
        self.bigram_counts = defaultdict(Counter, {k: Counter(v) for k, v in data['bigram_counts'].items()})
        self.trigram_counts = defaultdict(Counter, {k: Counter(v) for k, v in data['trigram_counts'].items()})
        self.vocabulary = data['vocabulary']
        self.total_words = data['total_words']
        self.bigram_continuation = Counter(data['bigram_continuation'])
        self.trigram_continuation = Counter(data['trigram_continuation'])
        self._trained = True


# Global model instance
_model: Optional[NgramModel] = None


def get_model() -> NgramModel:
    """Get the global model instance."""
    global _model
    if _model is None:
        _model = NgramModel()
    return _model


def initialize_model() -> NgramModel:
    """
    Initialize and train the model on Brown and Gutenberg corpora.
    
    Returns:
        Trained NgramModel instance
    """
    global _model
    
    model = NgramModel()
    
    try:
        import nltk
        
        # Try to download required data
        try:
            nltk.data.find('corpora/brown')
        except LookupError:
            nltk.download('brown', quiet=True)
        
        try:
            nltk.data.find('corpora/gutenberg')
        except LookupError:
            nltk.download('gutenberg', quiet=True)
        
        try:
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            nltk.download('punkt', quiet=True)
        
        # Load Brown corpus
        from nltk.corpus import brown
        brown_sents = brown.sents()
        model.train(list(brown_sents))
        
        # Load Gutenberg corpus
        from nltk.corpus import gutenberg
        gutenberg_sents = gutenberg.sents()
        model.train(list(gutenberg_sents))
        
        print(f"Model trained on {model.total_words} words, {len(model.vocabulary)} unique words")

        # Load WikiText-2
        from pathlib import Path
        wiki_path = Path("app/data/wikitext-2.txt")
        if wiki_path.exists():
            print("Loading WikiText-2...")
            text = wiki_path.read_text(encoding="utf-8")
            model.train_from_text(text)
            print(f"Added WikiText-2: {model.total_words} total words")
            
        # Load additional NLTK corpora
        try:
            from nltk.corpus import webtext
            model.train(list(webtext.sents()))
            print(f"Added Webtext: {model.total_words} total words")
        except LookupError:
            pass
            
        try:
            from nltk.corpus import reuters
            # Reuters is large, let's use a safe subset or full if possible
            # But reuters.sents() might fail if not unzipped properly by nltk.download
            # Just try it
            model.train(list(reuters.sents()))
            print(f"Added Reuters: {model.total_words} total words")
        except LookupError:
            pass
            
        try:
            from nltk.corpus import inaugural
            model.train(list(inaugural.sents()))
            print(f"Added Inaugural: {model.total_words} total words")
        except LookupError:
            pass
        
    except Exception as e:
        print(f"Warning: Could not load NLTK corpora: {e}")
        print("Model will have limited vocabulary")
    
    _model = model
    return model
