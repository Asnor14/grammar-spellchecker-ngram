"""
Semantic Checker module.
Uses lightweight word vector similarity to detect semantic errors like
"drink table" (impossible verb-object combinations).
"""

import re
import math
from typing import List, Dict, Tuple, Optional

try:
    import nltk
    from nltk import pos_tag, word_tokenize
except ImportError:
    nltk = None


class SemanticChecker:
    """
    Semantic checker using pre-computed word similarity scores.
    
    Uses a lightweight approach with a pre-built dictionary of common
    verb-object compatibility scores instead of loading large vector files.
    """
    
    # Pre-computed verb-object compatibility matrix
    # Format: verb -> {compatible_nouns: high_score, incompatible_nouns: low_score}
    # Scores range from 0.0 (incompatible) to 1.0 (highly compatible)
    VERB_OBJECT_COMPATIBILITY = {
        # -- MOTION --
        'drive': {
            'compatible': {'car', 'truck', 'bus', 'vehicle', 'motorcycle', 'taxi', 'van', 'tractor'},
            'incompatible': {'water', 'food', 'book', 'paper', 'wall', 'rock', 'tree', 'cat'}
        },
        'fly': {
            'compatible': {'plane', 'airplane', 'jet', 'helicopter', 'kite', 'drone', 'flag'},
            'incompatible': {'car', 'truck', 'house', 'road', 'ocean', 'desk'}
        },
        'ride': {
            'compatible': {'bike', 'bicycle', 'horse', 'pony', 'motorcycle', 'bus', 'train'},
            'incompatible': {'house', 'computer', 'book', 'ocean', 'cloud'}
        },
        
        # -- CONSUMPTION --
        'drink': {
            'compatible': {'water', 'coffee', 'tea', 'juice', 'milk', 'beer', 'wine', 'soda', 'liquid'},
            'incompatible': {'table', 'chair', 'book', 'paper', 'wall', 'floor', 'car', 'phone'}
        },
        'eat': {
            'compatible': {'food', 'meal', 'breakfast', 'lunch', 'dinner', 'bread', 'rice', 'meat', 'fruit', 'vegetable', 'pizza', 'sandwich', 'burger', 'cake'},
            'incompatible': {'table', 'chair', 'car', 'house', 'computer', 'phone', 'book', 'metal', 'glass'}
        },
        'cook': {
            'compatible': {'food', 'meal', 'dinner', 'breakfast', 'lunch', 'rice', 'meat', 'chicken', 'vegetable', 'soup', 'egg', 'pasta'},
            'incompatible': {'book', 'computer', 'car', 'phone', 'rock', 'metal'}
        },

        # -- INTERACTION --
        'read': {
            'compatible': {'book', 'article', 'paper', 'document', 'text', 'message', 'email', 'novel', 'magazine', 'newspaper', 'story', 'poem', 'sign'},
            'incompatible': {'water', 'food', 'car', 'wall', 'floor', 'chair', 'rock', 'air'}
        },
        'write': {
            'compatible': {'book', 'letter', 'email', 'message', 'paper', 'article', 'essay', 'report', 'story', 'code', 'text', 'poem'},
            'incompatible': {'water', 'food', 'car', 'wall', 'rock', 'air', 'sun'}
        },
        'wear': {
            'compatible': {'clothes', 'shirt', 'pants', 'dress', 'shoes', 'hat', 'jacket', 'coat', 'suit', 'glasses', 'watch', 'jewelry'},
            'incompatible': {'food', 'water', 'car', 'house', 'book', 'computer'}
        },
        'play': {
            'compatible': {'game', 'sport', 'music', 'guitar', 'piano', 'football', 'soccer', 'basketball', 'cards', 'chess', 'role'},
            'incompatible': {'food', 'water', 'house', 'car', 'work', 'job'}
        },
        
        # -- ABSTRACT --
        'solve': {
            'compatible': {'problem', 'puzzle', 'mystery', 'crime', 'equation', 'issue', 'case'},
            'incompatible': {'water', 'food', 'car', 'dog', 'cat', 'tree'}
        },
        'waste': {
            'compatible': {'time', 'money', 'resource', 'energy', 'opportunity', 'food', 'water'},
            'incompatible': {'problem', 'solution', 'answer', 'question'}
        },
        
        # -- CREATION/DESTRUCTION --
        'break': {
            'compatible': {'glass', 'window', 'plate', 'cup', 'rule', 'law', 'record', 'bone', 'ice', 'promise'},
            'incompatible': {'water', 'air', 'light', 'sound', 'thought'}
        },
        'build': {
            'compatible': {'house', 'building', 'bridge', 'wall', 'structure', 'tower', 'road'},
            'incompatible': {'water', 'air', 'sound', 'thought', 'idea'}
        },
        'open': {
            'compatible': {'door', 'window', 'book', 'box', 'letter', 'email', 'file', 'account', 'bottle'},
            'incompatible': {'water', 'air', 'light', 'sound'}
        },
        'close': {
            'compatible': {'door', 'window', 'book', 'box', 'account', 'deal', 'file', 'eyes'},
            'incompatible': {'water', 'air', 'light', 'rock'}
        },
        
        # -- LEARNING --
        'teach': {
            'compatible': {'student', 'class', 'subject', 'lesson', 'course', 'skill', 'language', 'math'},
            'incompatible': {'water', 'car', 'rock', 'wall', 'table'}
        },
        'learn': {
            'compatible': {'skill', 'language', 'lesson', 'subject', 'word', 'concept', 'method'},
            'incompatible': {'water', 'rock', 'wall', 'car', 'table'}
        },
        'study': {
            'compatible': {'subject', 'lesson', 'book', 'course', 'language', 'science', 'history', 'math'},
            'incompatible': {'water', 'rock', 'car', 'wall', 'food'}
        },
    }
    
    # Semantic category mappings for nouns
    NOUN_CATEGORIES = {
        'liquid': {'water', 'coffee', 'tea', 'juice', 'milk', 'beer', 'wine', 'soda', 'oil', 'soup'},
        'food': {'bread', 'rice', 'meat', 'fish', 'fruit', 'vegetable', 'pizza', 'cake', 'apple'},
        'furniture': {'table', 'chair', 'desk', 'bed', 'sofa', 'couch', 'shelf'},
        'vehicle': {'car', 'truck', 'bus', 'motorcycle', 'bicycle', 'van', 'taxi'},
        'document': {'book', 'paper', 'article', 'letter', 'report', 'document', 'text'},
        'clothing': {'shirt', 'pants', 'dress', 'shoes', 'hat', 'jacket', 'coat', 'suit'},
        'building': {'house', 'building', 'school', 'hospital', 'store', 'mall', 'office'},
    }
    
    # Similarity threshold
    SIMILARITY_THRESHOLD = 0.15
    
    def __init__(self):
        """Initialize the semantic checker."""
        self._ensure_nltk_resources()
    
    def _ensure_nltk_resources(self):
        """Ensure required NLTK resources are available."""
        if nltk:
            try:
                nltk.data.find('tokenizers/punkt')
            except LookupError:
                try:
                    nltk.download('punkt', quiet=True)
                except:
                    pass
            try:
                nltk.data.find('taggers/averaged_perceptron_tagger')
            except LookupError:
                try:
                    nltk.download('averaged_perceptron_tagger', quiet=True)
                except:
                    pass
    
    def _tokenize_with_pos(self, sentence: str) -> List[Tuple[str, str]]:
        """Tokenize and POS tag a sentence."""
        if not nltk:
            # Fallback basic tokenization
            words = re.findall(r'\b\w+\b', sentence.lower())
            return [(w, 'NN') for w in words]  # Assume all nouns
        
        try:
            tokens = word_tokenize(sentence)
            return pos_tag(tokens)
        except:
            words = re.findall(r'\b\w+\b', sentence.lower())
            return [(w, 'NN') for w in words]
    
    def _get_verb_object_pairs(self, tagged: List[Tuple[str, str]]) -> List[Tuple[str, str, int, int]]:
        """
        Extract verb-object pairs from tagged sentence.
        Returns: List of (verb, object, verb_idx, object_idx)
        """
        pairs = []
        verb_tags = {'VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ'}
        noun_tags = {'NN', 'NNS', 'NNP', 'NNPS'}
        
        for i, (word, tag) in enumerate(tagged):
            if tag in verb_tags:
                # Look for noun after verb (within next 3 words)
                for j in range(i + 1, min(i + 4, len(tagged))):
                    next_word, next_tag = tagged[j]
                    if next_tag in noun_tags:
                        pairs.append((word.lower(), next_word.lower(), i, j))
                        break
                    # Skip determiners, adjectives
                    elif next_tag not in {'DT', 'JJ', 'JJR', 'JJS', 'RB', 'RBR', 'RBS'}:
                        break
        
        return pairs
    
    def _calculate_similarity(self, verb: str, noun: str) -> float:
        """
        Calculate semantic similarity between verb and noun.
        Uses pre-computed compatibility matrix.
        """
        # Normalize verb to base form (simple heuristic)
        base_verb = verb
        if verb.endswith('ing'):
            base_verb = verb[:-3]
            if base_verb.endswith('k'):  # drinking -> drink
                pass
            elif len(base_verb) > 2 and base_verb[-1] == base_verb[-2]:
                base_verb = base_verb[:-1]  # running -> run
        elif verb.endswith('ed'):
            base_verb = verb[:-2]
        elif verb.endswith('s') and not verb.endswith('ss'):
            base_verb = verb[:-1]
        
        # Check compatibility matrix
        if base_verb in self.VERB_OBJECT_COMPATIBILITY:
            compat = self.VERB_OBJECT_COMPATIBILITY[base_verb]
            if noun in compat.get('compatible', set()):
                return 0.85  # High compatibility
            elif noun in compat.get('incompatible', set()):
                return 0.05  # Very low compatibility
        
        # Check noun categories for related nouns
        for verb_key, compat in self.VERB_OBJECT_COMPATIBILITY.items():
            if base_verb == verb_key or verb.startswith(verb_key):
                # Check if noun is in a category of known incompatible nouns
                for cat_name, cat_nouns in self.NOUN_CATEGORIES.items():
                    if noun in cat_nouns:
                        # Check if category is typically incompatible
                        incomp_set = compat.get('incompatible', set())
                        if any(n in cat_nouns for n in incomp_set):
                            return 0.10  # Low compatibility
                        comp_set = compat.get('compatible', set())
                        if any(n in cat_nouns for n in comp_set):
                            return 0.75  # High compatibility
        
        # Default: assume neutral compatibility
        return 0.50
    
    def check_sentence(self, sentence: str) -> List[Dict]:
        """
        Check sentence for semantic errors.
        
        Args:
            sentence: Input sentence to check
            
        Returns:
            List of error dictionaries with semantic violations
        """
        errors = []
        
        # Get POS tagged tokens
        tagged = self._tokenize_with_pos(sentence)
        
        # Extract verb-object pairs
        pairs = self._get_verb_object_pairs(tagged)
        
        # Check each pair for semantic compatibility
        for verb, noun, verb_idx, noun_idx in pairs:
            similarity = self._calculate_similarity(verb, noun)
            
            if similarity < self.SIMILARITY_THRESHOLD:
                # Find position in original sentence
                noun_pattern = re.compile(r'\b' + re.escape(noun) + r'\b', re.IGNORECASE)
                match = noun_pattern.search(sentence)
                
                if match:
                    errors.append({
                        'type': 'semantic',
                        'position': {'start': match.start(), 'end': match.end()},
                        'original': sentence[match.start():match.end()],
                        'suggestion': f'[Check: is "{noun}" correct with "{verb}"?]',
                        'explanation': f'Semantic Error: "{noun}" is not a typical object for "{verb}". '
                                      f'Similarity score: {similarity:.2f}',
                        'sentenceIndex': 0,
                        'similarity': similarity,
                    })
        
        return errors
    
    def check_text(self, text: str) -> List[Dict]:
        """
        Check entire text for semantic errors.
        
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
                    # Find actual position in original text
                    start_in_text = text.find(sentence.strip(), offset)
                    if start_in_text >= 0:
                        error['position']['start'] += start_in_text
                        error['position']['end'] += start_in_text
                    error['sentenceIndex'] = i
                
                errors.extend(sentence_errors)
            
            offset += len(sentence) + 1  # +1 for punctuation
        
        return errors


# Global instance
_semantic_checker = None


def get_semantic_checker() -> SemanticChecker:
    """Get the global semantic checker instance."""
    global _semantic_checker
    if _semantic_checker is None:
        _semantic_checker = SemanticChecker()
    return _semantic_checker
