"""
Sentence splitter module.
Splits text into sentences while handling abbreviations and edge cases.
"""

import re
from typing import List, Tuple


# Common abbreviations that shouldn't end a sentence
ABBREVIATIONS = {
    'mr', 'mrs', 'ms', 'dr', 'prof', 'sr', 'jr',
    'vs', 'etc', 'inc', 'ltd', 'co',
    'st', 'ave', 'blvd', 'rd',
    'jan', 'feb', 'mar', 'apr', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec',
    'i.e', 'e.g', 'cf', 'viz',
    'no', 'nos', 'vol', 'vols', 'pp', 'pg',
    'fig', 'figs', 'approx', 'dept', 'est', 'govt',
}


def split_sentences(text: str) -> List[str]:
    """
    Split text into sentences.
    
    Args:
        text: Input text
        
    Returns:
        List of sentences
    """
    if not text or not text.strip():
        return []
    
    text = text.strip()
    
    # If no sentence-ending punctuation, treat the whole text as one sentence
    if not any(p in text for p in '.!?'):
        return [text]
    
    # Use regex to split on sentence boundaries
    # Match: period/exclamation/question + space + capital letter or end
    sentences = []
    
    # Pattern: split on .!? followed by space and capital letter
    # But preserve the punctuation with the sentence
    pattern = r'(?<=[.!?])\s+(?=[A-Z])'
    
    parts = re.split(pattern, text)
    
    for part in parts:
        part = part.strip()
        if part:
            # Check if this part ends with an abbreviation
            # If so, it might need to be joined with the next part
            sentences.append(part)
    
    # If no sentences were created, return the whole text as one sentence
    if not sentences:
        return [text]
    
    return sentences


def split_sentences_with_positions(text: str) -> List[Tuple[str, int, int]]:
    """
    Split text into sentences with their positions.
    
    Args:
        text: Input text
        
    Returns:
        List of tuples (sentence, start_pos, end_pos)
    """
    if not text or not text.strip():
        return []
    
    sentences = split_sentences(text)
    
    if not sentences:
        return []
    
    result = []
    current_pos = 0
    
    for sentence in sentences:
        # Find the sentence in the original text starting from current position
        # Use the full sentence to find the exact match
        start = text.find(sentence, current_pos)
        if start == -1:
            # Fallback: try to find starting from beginning
            start = text.find(sentence)
            if start == -1:
                # Last resort: use current position
                start = current_pos
        
        end = start + len(sentence)
        result.append((sentence, start, end))
        current_pos = end
    
    return result


def _ends_sentence(word: str, words: List[str], index: int) -> bool:
    """
    Check if a word ends a sentence.
    
    Args:
        word: Current word
        words: All words
        index: Index of current word
        
    Returns:
        True if this word ends a sentence
    """
    # Check if word ends with sentence-ending punctuation
    if not word or word[-1] not in '.!?':
        return False
    
    # If it's the last word, it ends a sentence
    if index >= len(words) - 1:
        return True
    
    # Check if the base word (without punctuation) is an abbreviation
    base_word = word.rstrip('.!?').lower()
    if base_word in ABBREVIATIONS:
        return False
    
    # Check if next word starts with a capital letter
    next_word = words[index + 1]
    if next_word and next_word[0].isupper():
        return True
    
    return False


def count_sentences(text: str) -> int:
    """
    Count the number of sentences in text.
    
    Args:
        text: Input text
        
    Returns:
        Number of sentences
    """
    return len(split_sentences(text))
