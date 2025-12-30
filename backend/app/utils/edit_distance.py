"""
Edit distance algorithms for spelling correction.
Implements Levenshtein and Damerau-Levenshtein distance.
"""

from typing import List, Set, Tuple


def levenshtein_distance(s1: str, s2: str) -> int:
    """
    Calculate the Levenshtein distance between two strings.
    
    Args:
        s1: First string
        s2: Second string
        
    Returns:
        Edit distance (number of insertions, deletions, substitutions)
    """
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)
    
    if len(s2) == 0:
        return len(s1)
    
    previous_row = range(len(s2) + 1)
    
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
    
    return previous_row[-1]


def damerau_levenshtein_distance(s1: str, s2: str) -> int:
    """
    Calculate the Damerau-Levenshtein distance between two strings.
    Includes transpositions as a single edit operation.
    
    Args:
        s1: First string
        s2: Second string
        
    Returns:
        Edit distance
    """
    len1, len2 = len(s1), len(s2)
    
    # Create distance matrix
    d = [[0] * (len2 + 1) for _ in range(len1 + 1)]
    
    for i in range(len1 + 1):
        d[i][0] = i
    for j in range(len2 + 1):
        d[0][j] = j
    
    for i in range(1, len1 + 1):
        for j in range(1, len2 + 1):
            cost = 0 if s1[i-1] == s2[j-1] else 1
            
            d[i][j] = min(
                d[i-1][j] + 1,      # deletion
                d[i][j-1] + 1,      # insertion
                d[i-1][j-1] + cost  # substitution
            )
            
            # Transposition
            if i > 1 and j > 1 and s1[i-1] == s2[j-2] and s1[i-2] == s2[j-1]:
                d[i][j] = min(d[i][j], d[i-2][j-2] + cost)
    
    return d[len1][len2]


def generate_edits_1(word: str, alphabet: str = 'abcdefghijklmnopqrstuvwxyz') -> Set[str]:
    """
    Generate all strings that are one edit away from the input word.
    
    Args:
        word: Input word
        alphabet: Valid characters
        
    Returns:
        Set of all possible one-edit variations
    """
    word = word.lower()
    splits = [(word[:i], word[i:]) for i in range(len(word) + 1)]
    
    # Deletions
    deletes = [L + R[1:] for L, R in splits if R]
    
    # Transpositions
    transposes = [L + R[1] + R[0] + R[2:] for L, R in splits if len(R) > 1]
    
    # Replacements
    replaces = [L + c + R[1:] for L, R in splits if R for c in alphabet]
    
    # Insertions
    inserts = [L + c + R for L, R in splits for c in alphabet]
    
    return set(deletes + transposes + replaces + inserts)


def generate_edits_2(word: str, alphabet: str = 'abcdefghijklmnopqrstuvwxyz') -> Set[str]:
    """
    Generate all strings that are two edits away from the input word.
    
    Args:
        word: Input word
        alphabet: Valid characters
        
    Returns:
        Set of all possible two-edit variations
    """
    return set(e2 for e1 in generate_edits_1(word, alphabet) for e2 in generate_edits_1(e1, alphabet))


def get_candidates_within_distance(
    word: str,
    vocabulary: Set[str],
    max_distance: int = 2
) -> List[Tuple[str, int]]:
    """
    Get candidate corrections from vocabulary within max edit distance.
    
    Args:
        word: Misspelled word
        vocabulary: Set of valid words
        max_distance: Maximum edit distance to consider
        
    Returns:
        List of (candidate, distance) tuples sorted by distance
    """
    word = word.lower()
    candidates = []
    
    # Check exact match first
    if word in vocabulary:
        return [(word, 0)]
    
    # Check edit distance 1
    edits1 = generate_edits_1(word)
    for edit in edits1:
        if edit in vocabulary:
            candidates.append((edit, 1))
    
    # If we found candidates at distance 1, return them
    if candidates:
        return sorted(candidates, key=lambda x: x[1])
    
    # Check edit distance 2 if needed
    if max_distance >= 2:
        edits2 = generate_edits_2(word)
        for edit in edits2:
            if edit in vocabulary:
                candidates.append((edit, 2))
    
    return sorted(candidates, key=lambda x: x[1])
