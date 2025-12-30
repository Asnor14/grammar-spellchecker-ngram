"""
POS Tag N-gram Model module.
Implements a Trigram model trained on Part-of-Speech tags
to detect unusual sentence structures.
"""

import re
import math
from collections import defaultdict
from typing import List, Dict, Tuple, Optional

try:
    import nltk
    from nltk import pos_tag, word_tokenize
    from nltk.corpus import brown, gutenberg
except ImportError:
    nltk = None


class POSNGramModel:
    """
    POS Tag-based Trigram Language Model.
    
    Instead of modeling word sequences, this models POS tag sequences
    to detect grammatically unusual sentence structures.
    
    Example:
        "The go home" -> [DT, VB, NN] -> Low probability (unusual pattern)
        "I go home" -> [PRP, VBP, NN] -> Higher probability (common pattern)
    """
    
    # Probability threshold for flagging unusual structures
    STRUCTURE_THRESHOLD = -15.0  # Log probability
    
    # Common valid POS patterns (trigrams)
    VALID_PATTERNS = {
        # Subject-Verb patterns
        ('PRP', 'VBP', 'DT'),    # I eat the
        ('PRP', 'VBZ', 'DT'),    # He eats the
        ('PRP', 'VBD', 'DT'),    # I ate the
        ('NN', 'VBZ', 'DT'),     # Dog eats the
        ('NNS', 'VBP', 'DT'),    # Dogs eat the
        
        # Determiner-Adjective-Noun
        ('DT', 'JJ', 'NN'),      # the big dog
        ('DT', 'JJ', 'NNS'),     # the big dogs
        
        # Determiner-Noun-Verb
        ('DT', 'NN', 'VBZ'),     # the dog runs
        ('DT', 'NNS', 'VBP'),    # the dogs run
        
        # Prep phrase patterns
        ('IN', 'DT', 'NN'),      # in the house
        ('IN', 'DT', 'NNS'),     # in the houses
        ('TO', 'DT', 'NN'),      # to the store
        
        # Verb-Object patterns
        ('VBP', 'DT', 'NN'),     # eat the food
        ('VBZ', 'DT', 'NN'),     # eats the food
        ('VBD', 'DT', 'NN'),     # ate the food
        
        # Common auxiliary patterns
        ('MD', 'VB', 'DT'),      # will eat the
        ('MD', 'VB', 'NN'),      # will eat food
        ('VBP', 'VBG', 'DT'),    # am eating the
        ('VBZ', 'VBG', 'DT'),    # is eating the
    }
    
    # Invalid patterns that indicate errors
    INVALID_PATTERNS = {
        ('DT', 'VB', 'NN'),      # the go home (article + base verb)
        ('DT', 'VBP', 'NN'),     # the eat food
        ('DT', 'VBZ', 'NN'),     # the eats food
        ('VBZ', 'VBZ', 'NN'),    # eats eats food
        ('VBP', 'VBP', 'NN'),    # eat eat food
        ('DT', 'DT', 'NN'),      # the the dog
        ('NN', 'NN', 'VB'),      # dog cat go (unusual)
        ('VB', 'VB', 'VB'),      # go go go (unusual)
    }
    
    def __init__(self):
        """Initialize the POS N-gram model."""
        self.trigram_counts = defaultdict(int)
        self.bigram_counts = defaultdict(int)
        self.unigram_counts = defaultdict(int)
        self.total_trigrams = 0
        self.total_bigrams = 0
        self.total_unigrams = 0
        self.vocabulary_size = 0
        self.is_trained = False
        
        self._ensure_nltk_resources()
        
        # Try training on Brown corpus first, fallback to builtin patterns
        if not self._train_on_brown_corpus():
            self._train_on_builtin_patterns()
    
    def _ensure_nltk_resources(self):
        """Ensure required NLTK resources are available."""
        if nltk:
            resources = [
                ('tokenizers/punkt', 'punkt'),
                ('taggers/averaged_perceptron_tagger', 'averaged_perceptron_tagger'),
                ('corpora/brown', 'brown'),
            ]
            for path, name in resources:
                try:
                    nltk.data.find(path)
                except LookupError:
                    try:
                        nltk.download(name, quiet=True)
                    except:
                        pass
    
    def _train_on_brown_corpus(self) -> bool:
        """
        Train on NLTK Brown Corpus for academic-grade accuracy.
        
        Returns:
            True if training succeeded, False if fallback is needed
        """
        if not nltk:
            return False
        
        try:
            # Load sentences from selected categories
            categories = ['news', 'editorial', 'reviews', 'government']
            formatted_sentences = []
            
            for category in categories:
                try:
                    sents = brown.sents(categories=category)
                    for sent in sents:
                        # Format as string
                        formatted_sentences.append(' '.join(sent))
                except:
                    continue
            
            if not formatted_sentences:
                return False
            
            # Limit to reasonable training size for performance
            max_sentences = 5000
            if len(formatted_sentences) > max_sentences:
                formatted_sentences = formatted_sentences[:max_sentences]
            
            print(f"Training POS N-gram model on {len(formatted_sentences)} Brown Corpus sentences...")
            self.train(formatted_sentences)
            print(f"POS N-gram model trained successfully!")
            return True
            
        except Exception as e:
            print(f"Brown Corpus training failed: {e}. Using fallback.")
            return False
    
    def _train_on_builtin_patterns(self):
        """Train on common English sentence patterns."""
        # Sample sentences representing common patterns
        training_sentences = [
            "I eat the food.",
            "He runs every day.",
            "She is very happy.",
            "The dog eats food.",
            "They are going home.",
            "We went to the store.",
            "The big dog runs fast.",
            "I am eating lunch.",
            "He has been working.",
            "The students study hard.",
            "She can speak English.",
            "They will come tomorrow.",
            "I have finished my work.",
            "The teacher explains clearly.",
            "We should leave now.",
            "He might be late.",
            "The children are playing.",
            "She writes beautiful poems.",
            "I enjoy reading books.",
            "They prefer watching movies.",
            "The cat sleeps peacefully.",
            "We need more time.",
            "He wants to help.",
            "She decided to stay.",
            "I forgot to bring it.",
        ]
        
        for sentence in training_sentences:
            self._train_sentence(sentence)
        
        self.is_trained = True
    
    def _tokenize_with_pos(self, sentence: str) -> List[Tuple[str, str]]:
        """Tokenize and POS tag a sentence."""
        if not nltk:
            # Very basic fallback - won't be accurate
            words = re.findall(r'\b\w+\b', sentence)
            return [(w, 'NN') for w in words]
        
        try:
            tokens = word_tokenize(sentence)
            return pos_tag(tokens)
        except:
            words = re.findall(r'\b\w+\b', sentence)
            return [(w, 'NN') for w in words]
    
    def _train_sentence(self, sentence: str):
        """Train on a single sentence."""
        tagged = self._tokenize_with_pos(sentence)
        tags = [tag for word, tag in tagged]
        
        # Add start/end markers
        tags = ['<S>', '<S>'] + tags + ['</S>']
        
        # Count unigrams
        for tag in tags[2:-1]:  # Skip start/end markers
            self.unigram_counts[tag] += 1
            self.total_unigrams += 1
        
        # Count bigrams
        for i in range(1, len(tags)):
            bigram = (tags[i-1], tags[i])
            self.bigram_counts[bigram] += 1
            self.total_bigrams += 1
        
        # Count trigrams
        for i in range(2, len(tags)):
            trigram = (tags[i-2], tags[i-1], tags[i])
            self.trigram_counts[trigram] += 1
            self.total_trigrams += 1
        
        self.vocabulary_size = len(self.unigram_counts)
    
    def train(self, corpus: List[str]):
        """
        Train the model on a corpus of sentences.
        
        Args:
            corpus: List of sentences to train on
        """
        for sentence in corpus:
            if sentence.strip():
                self._train_sentence(sentence)
        
        self.is_trained = True
    
    def _get_trigram_probability(self, trigram: Tuple[str, str, str]) -> float:
        """
        Calculate smoothed trigram probability using Kneser-Ney interpolation.
        
        Returns log probability.
        """
        tag1, tag2, tag3 = trigram
        
        # Check if known invalid pattern
        if trigram in self.INVALID_PATTERNS:
            return -20.0  # Very low probability
        
        # Check if known valid pattern
        if trigram in self.VALID_PATTERNS:
            return -3.0  # Reasonable probability
        
        # Trigram count
        trigram_count = self.trigram_counts.get(trigram, 0)
        bigram_context = (tag1, tag2)
        bigram_count = self.bigram_counts.get(bigram_context, 0)
        
        # Discount parameter (for Kneser-Ney)
        d = 0.75
        
        if bigram_count > 0:
            # Trigram probability with discounting
            trigram_prob = max(trigram_count - d, 0) / bigram_count
            
            # Interpolation weight
            lambda_weight = (d / bigram_count) * len([t for t in self.trigram_counts if t[:2] == bigram_context])
            
            # Backoff to bigram
            unigram_count = self.unigram_counts.get(tag3, 0)
            backoff_prob = (unigram_count + 1) / (self.total_unigrams + self.vocabulary_size + 1)
            
            prob = trigram_prob + lambda_weight * backoff_prob
        else:
            # Pure backoff
            unigram_count = self.unigram_counts.get(tag3, 0)
            prob = (unigram_count + 1) / (self.total_unigrams + self.vocabulary_size + 1)
        
        # Return log probability
        return math.log(prob) if prob > 0 else -20.0
    
    def get_sentence_probability(self, sentence: str) -> float:
        """
        Calculate the log probability of a sentence's POS tag sequence.
        
        Args:
            sentence: Input sentence
            
        Returns:
            Log probability of the tag sequence
        """
        tagged = self._tokenize_with_pos(sentence)
        tags = [tag for word, tag in tagged]
        
        if len(tags) < 3:
            return -5.0  # Short sentences get neutral score
        
        # Add markers
        tags = ['<S>', '<S>'] + tags + ['</S>']
        
        # Calculate total log probability
        log_prob = 0.0
        for i in range(2, len(tags)):
            trigram = (tags[i-2], tags[i-1], tags[i])
            log_prob += self._get_trigram_probability(trigram)
        
        # Normalize by length
        log_prob_normalized = log_prob / (len(tags) - 2)
        
        return log_prob_normalized
    
    def check_sentence(self, sentence: str) -> List[Dict]:
        """
        Check if a sentence has unusual grammatical structure.
        
        Args:
            sentence: Input sentence to check
            
        Returns:
            List of error dictionaries for structural issues
        """
        errors = []
        
        tagged = self._tokenize_with_pos(sentence)
        tags = [tag for word, tag in tagged]
        
        if len(tags) < 3:
            return errors
        
        # Check for known invalid patterns
        tags_with_markers = ['<S>', '<S>'] + tags + ['</S>']
        
        for i in range(2, len(tags_with_markers)):
            trigram = (tags_with_markers[i-2], tags_with_markers[i-1], tags_with_markers[i])
            
            if trigram in self.INVALID_PATTERNS:
                # Find the words corresponding to this pattern
                word_idx = i - 2  # Account for start markers
                if 0 <= word_idx < len(tagged) and word_idx + 2 < len(tagged):
                    words = [tagged[word_idx + j][0] for j in range(3) if word_idx + j < len(tagged)]
                    phrase = ' '.join(words)
                    
                    # Find position in original sentence
                    pos = sentence.lower().find(phrase.lower())
                    if pos >= 0:
                        errors.append({
                            'type': 'structure',
                            'position': {'start': pos, 'end': pos + len(phrase)},
                            'original': sentence[pos:pos + len(phrase)],
                            'suggestion': '[Check sentence structure]',
                            'explanation': f'Unusual sentence structure detected: '
                                          f'"{phrase}" has pattern [{" → ".join(trigram)}]',
                            'sentenceIndex': 0,
                            'pattern': trigram,
                        })
        
        # Check overall sentence probability
        log_prob = self.get_sentence_probability(sentence)
        
        if log_prob < self.STRUCTURE_THRESHOLD:
            # Only add if we haven't already flagged specific patterns
            if not errors:
                errors.append({
                    'type': 'structure',
                    'position': {'start': 0, 'end': len(sentence)},
                    'original': sentence,
                    'suggestion': '[Review sentence structure]',
                    'explanation': f'Grammar Error: Unusual sentence structure. '
                                  f'(Structure score: {log_prob:.2f})',
                    'sentenceIndex': 0,
                    'probability': log_prob,
                })
        
        return errors
    
    def check_text(self, text: str) -> List[Dict]:
        """
        Check entire text for structural errors.
        
        Args:
            text: Input text to check
            
        Returns:
            List of error dictionaries
        """
        errors = []
        
        # Split into sentences
        sentences = re.split(r'[.!?]+', text)
        
        offset = 0
        for i, sentence in enumerate(sentences):
            if sentence.strip():
                sentence_errors = self.check_sentence(sentence.strip())
                
                # Adjust positions for full text
                for error in sentence_errors:
                    start_in_text = text.find(sentence.strip(), offset)
                    if start_in_text >= 0:
                        error['position']['start'] += start_in_text
                        error['position']['end'] = min(
                            error['position']['start'] + len(error['original']),
                            len(text)
                        )
                    error['sentenceIndex'] = i
                
                errors.extend(sentence_errors)
            
            offset += len(sentence) + 1
        
        return errors


# Global instance
_pos_ngram_model = None


def get_pos_ngram_model() -> POSNGramModel:
    """Get the global POS N-gram model instance."""
    global _pos_ngram_model
    if _pos_ngram_model is None:
        _pos_ngram_model = POSNGramModel()
    return _pos_ngram_model
