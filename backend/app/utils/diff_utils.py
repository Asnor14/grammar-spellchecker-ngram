
import difflib
from typing import List, Dict
import re

def generate_diff(original: str, corrected: str) -> List[Dict]:
    """
    Compare original and corrected text to generate a list of error objects.
    
    Args:
        original: The original input text
        corrected: The text corrected by the model
        
    Returns:
        List of error dictionaries with position, original, and suggestion.
    """
    matcher = difflib.SequenceMatcher(None, original, corrected)
    errors = []
    
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == 'equal':
            continue
            
        original_segment = original[i1:i2]
        corrected_segment = corrected[j1:j2]
        
        # Determine error type based on content
        error_type = 'grammar' # Default
        if tag == 'replace':
            # Check if it's just casing
            if original_segment.lower() == corrected_segment.lower():
                error_type = 'capitalization'
            # Check if it looks like punctuation
            elif re.match(r'^[^\w\s]+$', original_segment) or re.match(r'^[^\w\s]+$', corrected_segment):
                error_type = 'punctuation'
        elif tag == 'insert':
            if re.match(r'^[^\w\s]+$', corrected_segment):
                error_type = 'punctuation'
        
        explanation = "Grammar correction"
        if error_type == 'capitalization':
            explanation = "Fix capitalization"
        elif error_type == 'punctuation':
            explanation = "Fix punctuation"
            
        # Handle insertions (zero-width in original)
        # We need to attach them to something to be visible.
        # Strategy: If insert, try to grab the previous char (if space) or look at context.
        # But strictly, the API expects 'position' in original.
        # If we return start=end, the frontend might not render a red underline.
        # However, many "insert" cases are actually part of a "replace" in a larger block 
        # because Seq2Seq often rewrites phrases.
        
        # If pure insert (i1==i2)
        if i1 == i2:
            # It's an insertion. 
            # If it's at the end, i1 is len(original).
            # If it's a missing punctuation (like period), correct.
            # We can leave it as is, or try to expand to previous char.
            # Let's just output it. If the frontend can't handle 0-width, we might need to adjust.
            pass
            
        errors.append({
            'type': error_type,
            'position': {'start': i1, 'end': i2},
            'original': original_segment,
            'suggestion': corrected_segment,
            'explanation': explanation,
            'sentenceIndex': 0 # Simplification
        })
        
    return errors
