"""
Spell Checker module.
Uses dictionary-based matching with edit distance for suggestions.
"""

from typing import List, Dict, Set, Tuple, Optional
from collections import Counter


class SpellChecker:
    """
    Spell checker using dictionary and edit distance.
    """
    
    def __init__(self, vocabulary: Set[str] = None, word_frequencies: Counter = None):
        """
        Initialize the spell checker.
        
        Args:
            vocabulary: Set of valid words
            word_frequencies: Counter of word frequencies for ranking
        """
        self.vocabulary = vocabulary or set()
        self.word_frequencies = word_frequencies or Counter()
        
        # Common words that should not be flagged
        self.common_words = {
            # Articles and determiners
            'a', 'an', 'the', 'this', 'that', 'these', 'those',
            # Be verbs
            'is', 'are', 'was', 'were', 'be', 'been', 'being', 'am',
            # Have verbs
            'have', 'has', 'had', 'having',
            # Do verbs
            'do', 'does', 'did', 'doing', 'done',
            # Modal verbs
            'will', 'would', 'could', 'should', 'may', 'might', 'must',
            'shall', 'can', 'need', 'dare', 'ought',
            # Common verbs
            'go', 'goes', 'went', 'gone', 'going',
            'get', 'gets', 'got', 'getting', 'gotten',
            'make', 'makes', 'made', 'making',
            'take', 'takes', 'took', 'taken', 'taking',
            'see', 'sees', 'saw', 'seen', 'seeing',
            'come', 'comes', 'came', 'coming',
            'know', 'knows', 'knew', 'known', 'knowing',
            'think', 'thinks', 'thought', 'thinking',
            'say', 'says', 'said', 'saying',
            'give', 'gives', 'gave', 'given', 'giving',
            'find', 'finds', 'found', 'finding',
            'tell', 'tells', 'told', 'telling',
            'put', 'puts', 'putting',
            'use', 'uses', 'used', 'using',
            'want', 'wants', 'wanted', 'wanting',
            'look', 'looks', 'looked', 'looking',
            'ask', 'asks', 'asked', 'asking',
            'work', 'works', 'worked', 'working',
            'seem', 'seems', 'seemed', 'seeming',
            'feel', 'feels', 'felt', 'feeling',
            'try', 'tries', 'tried', 'trying',
            'leave', 'leaves', 'left', 'leaving',
            'call', 'calls', 'called', 'calling',
            'keep', 'keeps', 'kept', 'keeping',
            'let', 'lets', 'letting',
            'begin', 'begins', 'began', 'begun', 'beginning',
            'help', 'helps', 'helped', 'helping',
            'show', 'shows', 'showed', 'shown', 'showing',
            'hear', 'hears', 'heard', 'hearing',
            'play', 'plays', 'played', 'playing',
            'run', 'runs', 'ran', 'running',
            'move', 'moves', 'moved', 'moving',
            'live', 'lives', 'lived', 'living',
            'buy', 'buys', 'bought', 'buying',
            'bring', 'brings', 'brought', 'bringing',
            'happen', 'happens', 'happened', 'happening',
            'write', 'writes', 'wrote', 'written', 'writing',
            'sit', 'sits', 'sat', 'sitting',
            'stand', 'stands', 'stood', 'standing',
            'lose', 'loses', 'lost', 'losing',
            'pay', 'pays', 'paid', 'paying',
            'meet', 'meets', 'met', 'meeting',
            'include', 'includes', 'included', 'including',
            'continue', 'continues', 'continued', 'continuing',
            'set', 'sets', 'setting',
            'learn', 'learns', 'learned', 'learning',
            'change', 'changes', 'changed', 'changing',
            'lead', 'leads', 'led', 'leading',
            'understand', 'understands', 'understood', 'understanding',
            'watch', 'watches', 'watched', 'watching',
            'follow', 'follows', 'followed', 'following',
            'stop', 'stops', 'stopped', 'stopping',
            'create', 'creates', 'created', 'creating',
            'speak', 'speaks', 'spoke', 'spoken', 'speaking',
            'read', 'reads', 'reading',
            'allow', 'allows', 'allowed', 'allowing',
            'add', 'adds', 'added', 'adding',
            'spend', 'spends', 'spent', 'spending',
            'grow', 'grows', 'grew', 'grown', 'growing',
            'open', 'opens', 'opened', 'opening',
            'walk', 'walks', 'walked', 'walking',
            'win', 'wins', 'won', 'winning',
            'offer', 'offers', 'offered', 'offering',
            'remember', 'remembers', 'remembered', 'remembering',
            'love', 'loves', 'loved', 'loving',
            'consider', 'considers', 'considered', 'considering',
            'appear', 'appears', 'appeared', 'appearing',
            'wait', 'waits', 'waited', 'waiting',
            'serve', 'serves', 'served', 'serving',
            'die', 'dies', 'died', 'dying',
            'send', 'sends', 'sent', 'sending',
            'expect', 'expects', 'expected', 'expecting',
            'build', 'builds', 'built', 'building',
            'stay', 'stays', 'stayed', 'staying',
            'fall', 'falls', 'fell', 'fallen', 'falling',
            'cut', 'cuts', 'cutting',
            'reach', 'reaches', 'reached', 'reaching',
            'kill', 'kills', 'killed', 'killing',
            'remain', 'remains', 'remained', 'remaining',
            'drain', 'drains', 'drained', 'draining',
            # Prepositions
            'to', 'of', 'in', 'for', 'on', 'with', 'at', 'by', 'from',
            'up', 'about', 'into', 'over', 'after', 'beneath', 'under',
            'above', 'between', 'through', 'during', 'before', 'behind',
            'below', 'without', 'within', 'along', 'around', 'against',
            # Conjunctions
            'and', 'but', 'or', 'nor', 'so', 'yet', 'both', 'either',
            'neither', 'because', 'although', 'while', 'if', 'unless',
            'until', 'when', 'where', 'whether', 'however', 'therefore',
            # Adverbs
            'not', 'only', 'very', 'just', 'also', 'now', 'here', 'there',
            'then', 'still', 'already', 'always', 'never', 'ever', 'often',
            'sometimes', 'usually', 'really', 'actually', 'probably',
            'perhaps', 'maybe', 'certainly', 'definitely', 'quickly',
            'slowly', 'fast', 'well', 'much', 'even', 'too', 'quite',
            # Adjectives
            'good', 'new', 'first', 'last', 'long', 'great', 'little',
            'own', 'other', 'old', 'right', 'big', 'high', 'different',
            'small', 'large', 'next', 'early', 'young', 'important',
            'few', 'public', 'bad', 'same', 'able',
            # Pronouns
            'i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'us',
            'you', 'your', 'yours', 'yourself', 'yourselves',
            'he', 'him', 'his', 'himself', 'she', 'her', 'hers', 'herself',
            'it', 'its', 'itself', 'they', 'them', 'their', 'theirs', 'themselves',
            'what', 'which', 'who', 'whom', 'whose',
            # Question words
            'how', 'why', 'when', 'where',
            # Numbers
            'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight',
            'nine', 'ten', 'hundred', 'thousand', 'million',
            # Common nouns
            'time', 'year', 'people', 'way', 'day', 'man', 'woman', 'child',
            'world', 'life', 'hand', 'part', 'place', 'case', 'week', 'company',
            'system', 'program', 'question', 'work', 'government', 'number',
            'night', 'point', 'home', 'water', 'room', 'mother', 'area', 'money',
            'story', 'fact', 'month', 'lot', 'right', 'study', 'book', 'eye',
            'job', 'word', 'business', 'issue', 'side', 'kind', 'head', 'house',
            'service', 'friend', 'father', 'power', 'hour', 'game', 'line',
            'end', 'member', 'law', 'car', 'city', 'community', 'name', 'phone',
            'battery', 'brother', 'sister', 'family', 'school', 'student', 'teacher',
            'class', 'group', 'college', 'exam', 'test', 'quiz', 'problem',
            # Time words
            'morning', 'afternoon', 'evening', 'today', 'tomorrow', 'yesterday',
            'minute', 'second', 'moment',
            # Contractions (common parts)
            'isn', 'aren', 'wasn', 'weren', 'haven', 'hasn', 'hadn',
            'doesn', 'don', 'didn', 'won', 'wouldn', 'couldn', 'shouldn',
            'mightn', 'mustn', 'll', 've', 're', 'd', 's', 't',
            # Other common words
            'each', 'every', 'all', 'some', 'any', 'no', 'more', 'most',
            'than', 'such', 'as', 'like', 'just', 'only',
        }
        
        # Add common words to vocabulary
        self.vocabulary.update(self.common_words)
    
    def is_valid_word(self, word: str) -> bool:
        """
        Check if a word is valid (in vocabulary or common).
        
        Args:
            word: Word to check
            
        Returns:
            True if the word is valid
        """
        if not word:
            return True
        
        word_lower = word.lower()
        
        # Check vocabulary
        if word_lower in self.vocabulary:
            return True
        
        # Check common words
        if word_lower in self.common_words:
            return True
        
        # Allow proper nouns (capitalized words)
        if len(word) > 1 and word[0].isupper():
            return True
        
        # Allow numbers and words with numbers
        if any(c.isdigit() for c in word):
            return True
        
        # Allow contractions
        if "'" in word:
            return True
        
        # Allow single letters
        if len(word) == 1:
            return True
        
        return False
    
    def get_suggestions(
        self, 
        word: str, 
        max_suggestions: int = 5,
        max_distance: int = 2
    ) -> List[Tuple[str, int, int]]:
        """
        Get spelling suggestions for a word.
        
        Args:
            word: Misspelled word
            max_suggestions: Maximum number of suggestions
            max_distance: Maximum edit distance
            
        Returns:
            List of (suggestion, edit_distance, frequency) tuples
        """
        from app.utils.edit_distance import get_candidates_within_distance
        
        word_lower = word.lower()
        
        # Get candidates from vocabulary
        candidates = get_candidates_within_distance(
            word_lower, 
            self.vocabulary, 
            max_distance
        )
        
        # Score by frequency and distance
        scored = []
        for candidate, distance in candidates:
            freq = self.word_frequencies.get(candidate, 1)
            scored.append((candidate, distance, freq))
        
        # Sort by distance first, then by frequency (descending)
        scored.sort(key=lambda x: (x[1], -x[2]))
        
        return scored[:max_suggestions]
    
    def get_best_suggestion(self, word: str) -> Optional[str]:
        """
        Get the best spelling suggestion for a word.
        
        Args:
            word: Misspelled word
            
        Returns:
            Best suggestion or None
        """
        suggestions = self.get_suggestions(word, max_suggestions=1)
        if suggestions:
            return suggestions[0][0]
        return None
    
    def check_text(
        self, 
        text: str
    ) -> List[Dict]:
        """
        Check text for spelling errors.
        
        Args:
            text: Text to check
            
        Returns:
            List of error dictionaries
        """
        from app.utils.tokenizer import get_word_tokens_with_positions
        
        errors = []
        tokens = get_word_tokens_with_positions(text)
        
        for word, start, end in tokens:
            original_word = text[start:end]
            
            if not self.is_valid_word(original_word):
                suggestion = self.get_best_suggestion(word)
                
                if suggestion and suggestion != word.lower():
                    # Preserve original case
                    if original_word[0].isupper():
                        suggestion = suggestion.capitalize()
                    
                    errors.append({
                        'type': 'spelling',
                        'position': {'start': start, 'end': end},
                        'original': original_word,
                        'suggestion': suggestion,
                        'explanation': f'"{original_word}" may be misspelled. Did you mean "{suggestion}"?',
                        'sentenceIndex': 0,
                    })
        
        return errors


# Global spell checker instance
_spell_checker: Optional[SpellChecker] = None


def get_spell_checker() -> SpellChecker:
    """Get the global spell checker instance."""
    global _spell_checker
    if _spell_checker is None:
        _spell_checker = SpellChecker()
    return _spell_checker

def initialize_spell_checker(vocabulary: Set[str], frequencies: Counter) -> SpellChecker:
    """
    Initialize the spell checker with vocabulary.
    
    Args:
        vocabulary: Set of valid words
        frequencies: Word frequency counter
        
    Returns:
        Initialized SpellChecker
    """
    global _spell_checker
    
    # Try to load external dictionary
    import os
    from pathlib import Path
    
    dict_path = Path("app/data/words_alpha.txt")
    if dict_path.exists():
        try:
            print(f"Loading dictionary from {dict_path}...")
            with open(dict_path, "r", encoding="utf-8") as f:
                words = set(line.strip().lower() for line in f)
            vocabulary.update(words)
            print(f"Added {len(words)} words from dictionary.")
        except Exception as e:
            print(f"Error loading dictionary: {e}")
            
    _spell_checker = SpellChecker(vocabulary, frequencies)
    return _spell_checker
