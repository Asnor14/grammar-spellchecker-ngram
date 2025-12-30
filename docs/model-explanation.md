# Model Explanation

## Overview

The Grammar Checker uses a **statistical n-gram language model** with **Kneser-Ney smoothing** for grammar checking. This approach is:

- **Deterministic**: Same input always produces same output
- **Explainable**: Corrections are based on probability calculations
- **Corpus-based**: Trained on established English corpora
- **No neural networks**: Purely statistical methods

## N-gram Language Models

### What is an N-gram?

An n-gram is a contiguous sequence of n words from a text. For example, in the sentence "The cat sat":

| N-gram Type | Examples |
|-------------|----------|
| Unigram (1) | "The", "cat", "sat" |
| Bigram (2) | "The cat", "cat sat" |
| Trigram (3) | "The cat sat" |

### Probability Estimation

N-gram models estimate the probability of a word given its context:

- **Unigram**: P(word) = count(word) / total_words
- **Bigram**: P(word | prev) = count(prev, word) / count(prev)
- **Trigram**: P(word | prev2, prev1) = count(prev2, prev1, word) / count(prev2, prev1)

## Kneser-Ney Smoothing

### The Problem

Raw n-gram counts fail for:
- **Unseen n-grams**: Words that never appeared together in training
- **Sparse data**: Many valid word combinations are rare

### The Solution

Kneser-Ney smoothing:
1. **Discounts** observed counts by a fixed value (d = 0.75)
2. **Redistributes** probability mass to unseen events
3. Uses **continuation probability** for lower-order models

### Formula

For a bigram with Kneser-Ney smoothing:

```
P_KN(w_i | w_{i-1}) = max(count(w_{i-1}, w_i) - d, 0) / count(w_{i-1})
                     + λ(w_{i-1}) × P_continuation(w_i)
```

Where:
- `d` = discount (0.75)
- `λ(w_{i-1})` = interpolation weight
- `P_continuation(w_i)` = probability based on how many unique contexts precede w_i

## Interpolation

### Why Interpolate?

Each n-gram level has trade-offs:

| Level | Specificity | Coverage |
|-------|-------------|----------|
| Trigram | High | Low |
| Bigram | Medium | Medium |
| Unigram | Low | High |

Interpolation combines them for better robustness.

### Interpolation Formula

The final probability combines all levels:

```
P(w_i | w_{i-2}, w_{i-1}) = 0.5 × P_trigram + 0.3 × P_bigram + 0.2 × P_unigram
```

These weights (0.5, 0.3, 0.2) balance:
- Context sensitivity (trigram)
- Robustness (bigram)  
- Coverage (unigram)

## Training Corpora

### Brown Corpus

- **Size**: ~1 million words
- **Content**: 500 samples of American English
- **Genres**: News, fiction, academic, government
- **Source**: Brown University (1961)

### Gutenberg Corpus

- **Size**: ~2 million words
- **Content**: Classic literature
- **Authors**: Jane Austen, Shakespeare, etc.
- **Source**: Project Gutenberg

### Combined Vocabulary

- **Total words**: ~3 million
- **Unique words**: ~50,000+
- **Coverage**: General English prose

## Grammar Correction Process

### Step 1: Tokenization

Text is split into words while preserving punctuation.

```
Input: "He go to school."
Tokens: ["he", "go", "to", "school", "."]
```

### Step 2: Context Window

For each word, extract the context window:

```
Word: "go"
Context (trigram): ["he"]
```

### Step 3: Probability Calculation

Calculate the probability of each word in context:

```
P("go" | "he") = 0.001
P("goes" | "he") = 0.025
```

### Step 4: Candidate Generation

Generate candidate corrections within edit distance 2:

```
Candidates for "go": ["go", "goes", "got", "gone", ...]
```

### Step 5: Correction Decision

Suggest a correction only if:
1. Candidate probability > 2× original probability
2. Candidate is in vocabulary
3. Maximum 30% of words corrected per sentence

```
"goes" has 25× higher probability than "go" in this context → Suggest
```

## Perplexity

### Definition

Perplexity measures how "surprised" the model is by a sentence:

```
Perplexity = exp(-1/N × Σ log P(w_i | context))
```

### Interpretation

| Perplexity | Meaning |
|------------|---------|
| < 50 | Very fluent, expected text |
| 50-100 | Normal text |
| 100-500 | Some unusual constructions |
| > 500 | Very unusual or erroneous |

### Application

Lower perplexity → Higher fluency score → Higher confidence

## Limitations

### Model Limitations

1. **Fixed vocabulary**: Cannot handle words not in training data
2. **Context length**: Trigrams only see 2 previous words
3. **No semantics**: Cannot understand meaning, only patterns
4. **Corpus bias**: Reflects the style of training texts

### Correction Limitations

1. **Some valid sentences flagged**: Unusual but correct constructions
2. **Missing context**: Long-range dependencies not captured
3. **Proper nouns**: May flag names as misspellings

## Comparison with Neural Models

| Aspect | N-gram (This System) | Neural (BERT, GPT) |
|--------|---------------------|-------------------|
| Explainability | High | Low |
| Determinism | Yes | Often no |
| Training data | Megabytes | Gigabytes+ |
| Computation | CPU only | Often GPU |
| Accuracy | Good | Better |
| Hallucination | None | Possible |

## Academic Defense Statement

> "The system uses a **constrained interpolated trigram language model** for grammar correction, applying **Kneser-Ney smoothing** for probability estimation. The model is trained on the **Brown** and **Gutenberg** corpora, providing a robust vocabulary for general English text. Corrections are limited to **word-level substitutions** within vocabulary, ensuring no hallucinated words. The **30% correction limit** prevents over-correction while maintaining readability."
