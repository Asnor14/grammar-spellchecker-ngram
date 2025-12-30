"""
Punctuation Checker module.
Rule-based detection of punctuation errors.
"""

import re
from typing import List, Dict


class PunctuationChecker:
    """
    Rule-based punctuation checker.
    
    Detects:
    - Missing periods at sentence end
    - Missing commas before conjunctions
    - Double spaces
    - Missing capitalization after period
    - Quotation mark pairing
    """
    
    # Conjunctions that often need a comma before them
    CONJUNCTIONS = {'but', 'and', 'or', 'so', 'yet', 'for', 'nor'}
    
    def __init__(self):
        pass
    
    def check_text(self, text: str) -> List[Dict]:
        """
        Check text for punctuation errors.
        
        Args:
            text: Text to check
            
        Returns:
            List of error dictionaries
        """
        errors = []
        
        # Check for double spaces
        errors.extend(self._check_double_spaces(text))
        
        # Check for missing commas before conjunctions
        errors.extend(self._check_conjunction_commas(text))
        
        # Check for missing capitalization after period
        errors.extend(self._check_capitalization(text))
        
        # Check for missing sentence-ending punctuation
        errors.extend(self._check_sentence_ending(text))
        
        # Check quotation mark pairing
        errors.extend(self._check_quotation_marks(text))
        
        # Check for comma after introductory words
        errors.extend(self._check_introductory_comma(text))
        
        # Check for lowercase 'i'
        errors.extend(self._check_lowercase_i(text))
        
        return errors
    
    def _check_double_spaces(self, text: str) -> List[Dict]:
        """Check for double spaces."""
        errors = []
        
        for match in re.finditer(r'  +', text):
            start = match.start()
            end = match.end()
            
            errors.append({
                'type': 'punctuation',
                'position': {'start': start, 'end': end},
                'original': match.group(),
                'suggestion': ' ',
                'explanation': 'Multiple spaces should be replaced with a single space.',
                'sentenceIndex': 0,
            })
        
        return errors
    
    def _check_conjunction_commas(self, text: str) -> List[Dict]:
        """Check for missing commas before 'but' in compound sentences."""
        errors = []
        
        # Pattern: word + space + 'but' + space + word (no comma)
        # Only for 'but' which almost always needs a comma
        pattern = r'(\w+)\s+(but)\s+(\w+)'
        
        for match in re.finditer(pattern, text, re.IGNORECASE):
            before_word = match.group(1)
            conjunction = match.group(2)
            
            # Only flag if before_word is not a determiner/preposition
            skip_words = {'a', 'an', 'the', 'to', 'of', 'in', 'on', 'at', 'by', 'for', 'with'}
            
            if before_word.lower() not in skip_words:
                # Check if there's no comma before the conjunction
                check_pos = match.start() + len(before_word)
                if check_pos > 0 and text[check_pos:check_pos+1] != ',':
                    # Get the position of the space before conjunction
                    space_pos = match.start() + len(before_word)
                    
                    errors.append({
                        'type': 'punctuation',
                        'position': {'start': space_pos, 'end': space_pos + 1},
                        'original': ' ',
                        'suggestion': ', ',
                        'explanation': f'Consider adding a comma before "{conjunction}" in a compound sentence.',
                        'sentenceIndex': 0,
                    })
        
        return errors
    
    def _check_introductory_comma(self, text: str) -> List[Dict]:
        """Check for missing comma after introductory words/phrases."""
        errors = []
        
        # A list of common introductory words/adverbs when at start of sentence
        introductory_words = {
            'yesterday', 'today', 'tomorrow', 'recently', 'lately', 'meanwhile',
            'however', 'furthermore', 'morover', 'nevertheless', 'consequently',
            'initially', 'finally', 'eventually', 'sadly', 'hopefully', 'luckily',
            'unfortunately', 'incidentally', 'basically', 'actually', 'apparently',
            'obviously', 'clearly'
        }
        
        # Split text into words to check the first one
        words = text.split()
        if not words:
            return errors
        
        first_word_raw = words[0]
        # Remove punctuation for matching
        first_word = re.sub(r'[^\w]', '', first_word_raw).lower()
        
        # If the first word is in our list
        if first_word in introductory_words:
            # Check if it has a comma after it in the text
            # We look for: Start of string + word + space (no comma)
            # Use regex to find purely the word followed by space
            pattern = r'^(' + re.escape(first_word_raw) + r')(\s+)'
            match = re.match(pattern, text)
            
            if match:
                word_group = match.group(1)
                space_group = match.group(2)
                end_pos = len(word_group)
                
                # Check that it's just the word and space, no punctuation
                if ',' not in word_group and text[end_pos:end_pos+1] != ',':
                    errors.append({
                        'type': 'punctuation',
                        'position': {'start': end_pos, 'end': end_pos + 1}, # Replaces first char of space
                        'original': ' ',
                        'suggestion': ', ',
                        'explanation': f'Introductory word "{first_word_raw}" should be followed by a comma.',
                        'sentenceIndex': 0,
                    })
                    
        return errors

    def _check_lowercase_i(self, text: str) -> List[Dict]:
        """Check for lowercase 'i' (subject pronoun) that should be capitalized."""
        errors = []
        
        # Pattern: standalone 'i' not surrounded by word characters
        # This handles "i", "i'm", "i've", etc.
        pattern = r'(?<!\w)i(?!\w)'
        
        for match in re.finditer(pattern, text):
            # Check if it's really the pronoun 'i' (or part of contraction)
            # We assume isolated 'i' is always the pronoun I in English text
            
            start = match.start()
            end = match.end()
            
            errors.append({
                'type': 'punctuation',
                'position': {'start': start, 'end': end},
                'original': 'i',
                'suggestion': 'I',
                'explanation': 'The pronoun "I" should always be capitalized.',
                'sentenceIndex': 0,
            })
            
        return errors

    def _check_capitalization(self, text: str) -> List[Dict]:
        """Check for missing capitalization after sentence-ending punctuation."""
        errors = []
        
        # Pattern: sentence-ending punctuation + space + lowercase letter
        pattern = r'([.!?])\s+([a-z])'
        
        for match in re.finditer(pattern, text):
            lowercase_char = match.group(2)
            char_pos = match.start() + len(match.group(1)) + 1
            
            # Find the full word
            word_match = re.match(r'[a-z]+', text[char_pos:])
            if word_match:
                word = word_match.group()
                end_pos = char_pos + len(word)
                
                errors.append({
                    'type': 'punctuation',
                    'position': {'start': char_pos, 'end': end_pos},
                    'original': word,
                    'suggestion': word.capitalize(),
                    'explanation': 'Sentences should start with a capital letter.',
                    'sentenceIndex': 0,
                })
        
        return errors
    
    def _check_sentence_ending(self, text: str) -> List[Dict]:
        """Check if text ends with proper punctuation."""
        errors = []
        
        text = text.strip()
        if not text:
            return errors
        
        # Check if text ends with sentence-ending punctuation
        if text[-1] not in '.!?':
            # Only flag if text looks like a complete sentence
            words = text.split()
            if len(words) >= 3:  # At least a basic sentence
                errors.append({
                    'type': 'punctuation',
                    'position': {'start': len(text), 'end': len(text)},
                    'original': '',
                    'suggestion': '.',
                    'explanation': 'Sentences should end with proper punctuation (period, exclamation mark, or question mark).',
                    'sentenceIndex': 0,
                })
        
        return errors
    
    def _check_quotation_marks(self, text: str) -> List[Dict]:
        """Check for unmatched quotation marks."""
        errors = []
        
        # Count quotation marks
        double_quotes = text.count('"')
        single_quotes = text.count("'")
        
        # Check for unmatched double quotes
        if double_quotes % 2 != 0:
            # Find the last unmatched quote
            # This is a simple heuristic
            last_quote = text.rfind('"')
            errors.append({
                'type': 'punctuation',
                'position': {'start': last_quote, 'end': last_quote + 1},
                'original': '"',
                'suggestion': '',
                'explanation': 'Unmatched quotation mark detected. Each opening quote should have a closing quote.',
                'sentenceIndex': 0,
            })
        
        return errors


# Global instance
_punctuation_checker: PunctuationChecker = None


def get_punctuation_checker() -> PunctuationChecker:
    """Get the global punctuation checker instance."""
    global _punctuation_checker
    if _punctuation_checker is None:
        _punctuation_checker = PunctuationChecker()
    return _punctuation_checker
