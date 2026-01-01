"""
Spell Checker module.
Uses dictionary-based matching with edit distance for suggestions.
"""

from typing import List, Dict, Set, Tuple, Optional
from collections import Counter
import os
from pathlib import Path

class SpellChecker:
    """
    Spell checker using dictionary and edit distance.
    """
    
    def __init__(self, vocabulary: Set[str] = None, word_frequencies: Counter = None):
        """
        Initialize the spell checker.
        """
        self.vocabulary = vocabulary or set()
        self.word_frequencies = word_frequencies or Counter()
        
        # Common words that should not be flagged (Expanded Fallback)
        self.common_words = {
            # Articles and determiners
            'a', 'an', 'the', 'this', 'that', 'these', 'those',
            # Basic Nouns (Expanded for testing)
            'hello', 'world', 'test', 'text', 'sentence', 'example', 'word',
            'computer', 'system', 'program', 'app', 'user', 'data', 'file',
            'phone', 'battery', 'screen', 'keyboard', 'mouse', 'code',
            'time', 'year', 'people', 'way', 'day', 'man', 'woman', 'child',
            'school', 'student', 'teacher', 'class', 'group', 'college',
            'problem', 'issue', 'result', 'service', 'site', 'web',
            'coffee', 'water', 'food', 'money', 'email', 'message', 'letter',
            # Verbs (Expanded)
            'is', 'are', 'was', 'were', 'be', 'been', 'being', 'am',
            'have', 'has', 'had', 'having',
            'do', 'does', 'did', 'doing', 'done',
            'go', 'goes', 'went', 'gone', 'going',
            'get', 'gets', 'got', 'getting', 'gotten',
            'make', 'makes', 'made', 'making',
            'know', 'knows', 'knew', 'known', 'knowing',
            'think', 'thinks', 'thought', 'thinking',
            'take', 'takes', 'took', 'taken', 'taking',
            'see', 'sees', 'saw', 'seen', 'seeing',
            'come', 'comes', 'came', 'coming',
            'want', 'wants', 'wanted', 'wanting',
            'look', 'looks', 'looked', 'looking',
            'use', 'uses', 'used', 'using',
            'find', 'finds', 'found', 'finding',
            'give', 'gives', 'gave', 'given', 'giving',
            'tell', 'tells', 'told', 'telling',
            'work', 'works', 'worked', 'working',
            'call', 'calls', 'called', 'calling',
            'try', 'tries', 'tried', 'trying',
            'ask', 'asks', 'asked', 'asking',
            'need', 'needs', 'needed', 'needing',
            'feel', 'feels', 'felt', 'feeling',
            'become', 'becomes', 'became', 'becoming',
            'leave', 'leaves', 'left', 'leaving',
            'put', 'puts', 'putting',
            'mean', 'means', 'meant', 'meaning',
            'keep', 'keeps', 'kept', 'keeping',
            'let', 'lets', 'letting',
            'begin', 'begins', 'began', 'begun', 'beginning',
            'seem', 'seems', 'seemed', 'seeming',
            'help', 'helps', 'helped', 'helping',
            'talk', 'talks', 'talked', 'talking',
            'turn', 'turns', 'turned', 'turning',
            'start', 'starts', 'started', 'starting',
            'show', 'shows', 'showed', 'shown', 'showing',
            'hear', 'hears', 'heard', 'hearing',
            'play', 'plays', 'played', 'playing',
            'run', 'runs', 'ran', 'running',
            'move', 'moves', 'moved', 'moving',
            'like', 'likes', 'liked', 'liking',
            'live', 'lives', 'lived', 'living',
            'believe', 'believes', 'believed', 'believing',
            'hold', 'holds', 'held', 'holding',
            'bring', 'brings', 'brought', 'bringing',
            'happen', 'happens', 'happened', 'happening',
            'write', 'writes', 'wrote', 'written', 'writing',
            'provide', 'provides', 'provided', 'providing',
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
            'buy', 'buys', 'bought', 'buying',
            'wait', 'waits', 'waited', 'waiting',
            'serve', 'serves', 'served', 'serving',
            'die', 'dies', 'died', 'dying',
            'send', 'sends', 'sent', 'sending',
            'receive', 'receives', 'received', 'receiving',
            'expect', 'expects', 'expected', 'expecting',
            'build', 'builds', 'built', 'building',
            'stay', 'stays', 'stayed', 'staying',
            'fall', 'falls', 'fell', 'fallen', 'falling',
            'cut', 'cuts', 'cutting',
            'reach', 'reaches', 'reached', 'reaching',
            'kill', 'kills', 'killed', 'killing',
            'remain', 'remains', 'remained', 'remaining',
            # Pronouns
            'i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'us',
            'you', 'your', 'yours', 'yourself', 'yourselves',
            'he', 'him', 'his', 'himself', 'she', 'her', 'hers', 'herself',
            'it', 'its', 'itself', 'they', 'them', 'their', 'theirs', 'themselves',
            # Prepositions & Conjunctions
            'to', 'of', 'in', 'for', 'on', 'with', 'at', 'by', 'from', 'up', 'about',
            'into', 'over', 'after', 'and', 'but', 'or', 'so', 'if', 'because', 'when',
            # Adjectives/Adverbs
            'good', 'bad', 'new', 'old', 'great', 'small', 'big', 'large', 'high', 'low',
            'very', 'really', 'just', 'too', 'quite', 'not', 'no', 'yes', 'maybe',
            'fast', 'slow', 'quick', 'easy', 'hard', 'soft', 'able', 'same', 'different',
        }
        
        # Add common words to vocabulary immediately
        self.vocabulary.update(self.common_words)
    
    def is_valid_word(self, word: str) -> bool:
        """Check if a word is valid."""
        if not word: return True
        word_lower = word.lower()
        if word_lower in self.vocabulary: return True
        # Allow numbers/contractions/single chars
        if any(c.isdigit() for c in word) or "'" in word or len(word) == 1: return True
        return False
    
    def get_suggestions(self, word: str, max_suggestions: int = 5, max_distance: int = 2) -> List[Tuple[str, int, int]]:
        """Get spelling suggestions."""
        from app.utils.edit_distance import get_candidates_within_distance
        candidates = get_candidates_within_distance(word.lower(), self.vocabulary, max_distance)
        scored = []
        for candidate, distance in candidates:
            freq = self.word_frequencies.get(candidate, 1)
            # Boost matches that are in common_words
            if candidate in self.common_words:
                freq += 100000 
            scored.append((candidate, distance, freq))
        
        scored.sort(key=lambda x: (x[1], -x[2]))
        return scored[:max_suggestions]
    
    def get_best_suggestion(self, word: str) -> Optional[str]:
        suggestions = self.get_suggestions(word, max_suggestions=1)
        return suggestions[0][0] if suggestions else None
    
    def check_text(self, text: str) -> List[Dict]:
        from app.utils.tokenizer import get_word_tokens_with_positions
        errors = []
        tokens = get_word_tokens_with_positions(text)
        
        for word, start, end in tokens:
            original_word = text[start:end]
            if not self.is_valid_word(original_word):
                suggestion = self.get_best_suggestion(word)
                if suggestion and suggestion != word.lower():
                    # Preserve Case
                    if original_word[0].isupper():
                        suggestion = suggestion.capitalize()
                    elif original_word.isupper():
                        suggestion = suggestion.upper()
                        
                    errors.append({
                        'type': 'spelling',
                        'position': {'start': start, 'end': end},
                        'original': original_word,
                        'suggestion': suggestion,
                        'explanation': f'Spelling error: "{original_word}". Did you mean "{suggestion}"?',
                        'sentenceIndex': 0,
                    })
        return errors

# Global instance
_spell_checker: Optional[SpellChecker] = None

def get_spell_checker() -> SpellChecker:
    global _spell_checker
    if _spell_checker is None:
        _spell_checker = SpellChecker()
    return _spell_checker

def initialize_spell_checker(vocabulary: Set[str], frequencies: Counter) -> SpellChecker:
    global _spell_checker
    # Try loading external dictionary
    dict_path = Path("app/data/words_alpha.txt")
    if not dict_path.exists():
        # Fallback check for different working directory
        dict_path = Path("backend/app/data/words_alpha.txt")
        
    if dict_path.exists():
        try:
            print(f"Loading dictionary from {dict_path}...")
            with open(dict_path, "r", encoding="utf-8") as f:
                words = set(line.strip().lower() for line in f)
            vocabulary.update(words)
            print(f"Loaded {len(words)} words.")
        except Exception as e:
            print(f"Failed to load dictionary: {e}")
    else:
        print(f"Warning: Dictionary file not found at {dict_path}. Using limited fallback vocabulary.")
            
    _spell_checker = SpellChecker(vocabulary, frequencies)
    return _spell_checker
