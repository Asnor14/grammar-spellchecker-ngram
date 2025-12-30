"""
Tokenizer module for text preprocessing.
Handles word tokenization while preserving punctuation and handling contractions.
"""

import re
from typing import List, Tuple


def tokenize(text: str, preserve_case: bool = False) -> List[str]:
    """
    Tokenize text into words, preserving punctuation as separate tokens.
    
    Args:
        text: Input text to tokenize
        preserve_case: If False, convert to lowercase
        
    Returns:
        List of tokens
    """
    if not text:
        return []
    
    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text.strip())
    
    # Handle contractions - keep them together
    # Pattern matches words, contractions, and punctuation
    pattern = r"(?:\w+(?:'\w+)?)|[.,!?;:\"]"
    tokens = re.findall(pattern, text)
    
    if not preserve_case:
        tokens = [t.lower() if not t in '.,!?;:"' else t for t in tokens]
    
    return tokens


def tokenize_with_positions(text: str) -> List[Tuple[str, int, int]]:
    """
    Tokenize text and return tokens with their start and end positions.
    
    Args:
        text: Input text to tokenize
        
    Returns:
        List of tuples (token, start_pos, end_pos)
    """
    if not text:
        return []
    
    result = []
    pattern = r"(?:\w+(?:'\w+)?)|[.,!?;:\"]"
    
    for match in re.finditer(pattern, text):
        token = match.group()
        start = match.start()
        end = match.end()
        result.append((token, start, end))
    
    return result


def get_word_tokens(text: str) -> List[str]:
    """
    Get only word tokens (exclude punctuation).
    
    Args:
        text: Input text
        
    Returns:
        List of word tokens (lowercase)
    """
    tokens = tokenize(text, preserve_case=False)
    return [t for t in tokens if t.isalpha() or "'" in t]


def get_word_tokens_with_positions(text: str) -> List[Tuple[str, int, int]]:
    """
    Get word tokens with their positions.
    
    Args:
        text: Input text
        
    Returns:
        List of tuples (word, start_pos, end_pos)
    """
    all_tokens = tokenize_with_positions(text)
    return [(t.lower(), s, e) for t, s, e in all_tokens if t.isalpha() or "'" in t]


def normalize_text(text: str) -> str:
    """
    Normalize text for comparison.
    
    Args:
        text: Input text
        
    Returns:
        Normalized text (lowercase, normalized whitespace)
    """
    text = text.lower()
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def is_word(token: str) -> bool:
    """
    Check if a token is a word (not punctuation).
    
    Args:
        token: Token to check
        
    Returns:
        True if the token is a word
    """
    return bool(token) and (token.isalpha() or "'" in token)


def is_punctuation(token: str) -> bool:
    """
    Check if a token is punctuation.
    
    Args:
        token: Token to check
        
    Returns:
        True if the token is punctuation
    """
    return token in '.,!?;:"'
