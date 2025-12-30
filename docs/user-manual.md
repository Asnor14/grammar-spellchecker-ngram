# User Manual

## Getting Started

The Grammar Checker is a web application that analyzes your text for grammar, spelling, and punctuation errors using statistical language models.

## Input Methods

### Text Input

1. Click the **"Text Input"** tab (default)
2. Type or paste your text into the large text area
3. Character count is displayed at the bottom (max 10,000 characters)
4. Click **"Clear"** to reset the text

### File Upload

1. Click the **"File Upload"** tab
2. **Drag and drop** a file onto the upload zone, or **click** to browse
3. Supported formats: `.txt` and `.docx`
4. Maximum file size: 5MB
5. Click **"Remove File"** to clear the selection

## N-gram Model Selection

Choose between two analysis models:

| Mode | Context | Best For |
|------|---------|----------|
| **Bigram** | 2-word context | Faster, simpler analysis |
| **Trigram** | 3-word context | More accurate, recommended |

**Trigram** is selected by default and provides better accuracy for most texts.

## Running Analysis

1. Enter your text or upload a file
2. Select the n-gram model (optional, default: trigram)
3. Click **"Check Grammar"**
4. Wait for analysis (typically 1-5 seconds)

## Understanding Results

### Confidence Score

The circular meter at the top shows the grammar confidence score (0-100):

- **90-100%**: Excellent - Text is grammatically sound
- **70-89%**: Good - Minor issues detected
- **50-69%**: Fair - Several issues need attention
- **0-49%**: Needs Improvement - Significant errors found

### Highlighted Errors

Your text is displayed with underlined errors:

- **Red wavy underline**: Spelling error
- **Blue wavy underline**: Grammar error
- **Yellow wavy underline**: Punctuation error

**Click any underlined word** to see:
- Error type
- Original word
- Suggested correction
- Brief explanation

### Error Summary

The right sidebar shows:
- Error counts by type (badges)
- List of all detected errors
- Click any error to highlight it in the text

### Before & After Comparison

At the bottom, compare:
- **Original**: Your input with strikethrough on errors
- **Corrected**: Text with all suggestions applied

Click **"Copy Corrected"** to copy the corrected text to clipboard.

## Applying Fixes

### Individual Fixes

1. Click an underlined error in the text
2. In the tooltip, click **"Apply Fix"**
3. The correction is applied immediately
4. Other error positions update automatically

### Apply All Fixes

1. Click **"Apply All Fixes"** in the header
2. All suggested corrections are applied at once

### Reset

Click **"Reset"** to undo all applied fixes and return to the original text.

## Tips for Best Results

1. **Use complete sentences** - The model works best with proper sentence structure
2. **Check context** - Some suggestions depend on the surrounding words
3. **Review suggestions** - Not all suggestions may fit your intended meaning
4. **Use Trigram mode** - It provides more accurate contextual analysis

## Error Types Explained

### Spelling Errors

Words not found in the vocabulary dictionary. Suggestions are based on edit distance (similar letters).

**Example**: "recieve" → "receive"

### Grammar Errors

Words that exist in the dictionary but are contextually unlikely based on the n-gram model.

**Example**: "He go to school" → "He goes to school"

### Punctuation Errors

Rule-based detection of:
- Missing periods at sentence end
- Missing commas before conjunctions
- Double spaces
- Missing capitalization after periods
- Unmatched quotation marks

**Example**: "I like apples but I prefer oranges" → "I like apples, but I prefer oranges"

## Keyboard Shortcuts

- **Escape**: Close tooltip
- **Tab**: Navigate between input fields

## Limitations

- Maximum text length: 10,000 characters
- Maximum file size: 5MB
- Best accuracy with standard English prose
- May not handle specialized jargon well
- Corrections limited to 30% of words per sentence
