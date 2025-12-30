"""
Grammar confidence scoring module.
Calculates a 0-100 confidence score based on error density and severity.
"""

from typing import List, Dict, Any


# Error severity weights
ERROR_WEIGHTS = {
    'spelling': 3.0,
    'grammar': 4.0,
    'punctuation': 1.5,
}


def calculate_confidence_score(
    text: str,
    errors: List[Dict[str, Any]],
    sentence_fluency_scores: List[float] = None
) -> float:
    """
    Calculate an overall grammar confidence score from 0-100.
    
    Args:
        text: Original text
        errors: List of error dictionaries
        sentence_fluency_scores: Optional list of per-sentence fluency scores
        
    Returns:
        Confidence score (0-100)
    """
    if not text:
        return 100.0
    
    # Start with base score of 100
    score = 100.0
    
    # Count words in text
    words = text.split()
    word_count = len(words)
    
    if word_count == 0:
        return 100.0
    
    # Deduct points based on error count and severity
    error_penalty = 0.0
    for error in errors:
        error_type = error.get('type', 'grammar')
        weight = ERROR_WEIGHTS.get(error_type, 2.0)
        error_penalty += weight
    
    # Calculate error density penalty (errors per 100 words)
    error_density = (error_penalty / word_count) * 100
    
    # Cap the penalty at 70 points (minimum score of 30)
    density_penalty = min(error_density * 2, 70)
    score -= density_penalty
    
    # Factor in sentence fluency if available
    if sentence_fluency_scores:
        avg_fluency = sum(sentence_fluency_scores) / len(sentence_fluency_scores)
        # Fluency contributes up to 20 points
        fluency_bonus = (avg_fluency / 100) * 20
        score = score * 0.8 + fluency_bonus
    
    # Ensure score is within bounds
    return max(0.0, min(100.0, score))


def calculate_sentence_fluency(
    sentence: str,
    perplexity: float = None,
    error_count: int = 0
) -> float:
    """
    Calculate fluency score for a single sentence.
    
    Args:
        sentence: The sentence text
        perplexity: Language model perplexity (lower is better)
        error_count: Number of errors in the sentence
        
    Returns:
        Fluency score (0-100)
    """
    words = sentence.split()
    word_count = len(words)
    
    if word_count == 0:
        return 100.0
    
    # Start with base score
    score = 100.0
    
    # Penalize based on error count
    error_penalty = (error_count / word_count) * 50
    score -= min(error_penalty, 40)
    
    # Penalize based on perplexity if available
    if perplexity is not None:
        # Higher perplexity = less fluent
        # Typical good perplexity: 20-100
        # Bad perplexity: >500
        if perplexity < 50:
            perp_penalty = 0
        elif perplexity < 100:
            perp_penalty = 5
        elif perplexity < 200:
            perp_penalty = 15
        elif perplexity < 500:
            perp_penalty = 25
        else:
            perp_penalty = 40
        
        score -= perp_penalty
    
    return max(0.0, min(100.0, score))


def get_score_label(score: float) -> str:
    """
    Get a human-readable label for a confidence score.
    
    Args:
        score: Confidence score (0-100)
        
    Returns:
        Label string
    """
    if score >= 90:
        return "Excellent"
    elif score >= 70:
        return "Good"
    elif score >= 50:
        return "Fair"
    else:
        return "Needs Improvement"
