# System Overview

## Architecture

The Grammar Checker is a full-stack application with a clear separation between the frontend (Next.js) and backend (Python FastAPI).

```
┌─────────────────────────────────────────────────────────────────────┐
│                         Frontend (Next.js)                           │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                  │
│  │ Text Input  │  │ File Upload │  │ Mode Toggle │                  │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘                  │
│         │                │                │                          │
│         └────────────────┼────────────────┘                          │
│                          ▼                                           │
│  ┌───────────────────────────────────────┐                          │
│  │          Analysis Results              │                          │
│  │  • Highlighted Errors                  │                          │
│  │  • Error Summary                       │                          │
│  │  • Confidence Score                    │                          │
│  │  • Before/After Comparison             │                          │
│  └───────────────────────────────────────┘                          │
└─────────────────────────────┬───────────────────────────────────────┘
                              │ HTTP/REST
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                       Backend (FastAPI)                              │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │                     API Layer                                │    │
│  │  POST /check-text  │  POST /check-file  │  GET /health       │    │
│  └─────────────────────────────────────────────────────────────┘    │
│                              │                                       │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │                   NLP Models                                 │    │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │    │
│  │  │ N-gram Model │  │Spell Checker │  │ Punctuation  │       │    │
│  │  │(Kneser-Ney)  │  │(Edit Dist.)  │  │  (Rules)     │       │    │
│  │  └──────────────┘  └──────────────┘  └──────────────┘       │    │
│  └─────────────────────────────────────────────────────────────┘    │
│                              │                                       │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │                    Corpus Data                               │    │
│  │           Brown Corpus  +  Gutenberg Corpus                  │    │
│  └─────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────┘
```

## Data Flow

1. **User Input**: User enters text or uploads a file (.txt or .docx)
2. **Request**: Frontend sends text + n-gram mode to backend API
3. **Sentence Splitting**: Text is split into sentences
4. **Analysis**: Each sentence is analyzed for:
   - Spelling errors (dictionary + edit distance)
   - Grammar errors (n-gram probability comparison)
   - Punctuation errors (rule-based pattern matching)
5. **Scoring**: Confidence score calculated based on error density
6. **Response**: JSON response with errors, corrections, and scores
7. **Display**: Frontend renders highlighted errors and comparison view

## Component Interactions

### Frontend Components

| Component | Purpose |
|-----------|---------|
| `TextInput` | Large textarea with character counter |
| `FileUpload` | Drag & drop file upload zone |
| `InputModeToggle` | Switch between text/file input |
| `ModeToggle` | Switch between bigram/trigram |
| `HighlightedText` | Renders text with error underlines |
| `ErrorTooltip` | Shows error details and suggestions |
| `ErrorSummary` | Lists all errors with counts |
| `ConfidenceMeter` | Circular progress confidence display |
| `ComparisonView` | Before/after comparison |

### Backend Models

| Model | Algorithm | Purpose |
|-------|-----------|---------|
| `NgramModel` | Kneser-Ney Smoothed Trigram | Grammar checking |
| `SpellChecker` | Levenshtein Distance | Spelling correction |
| `PunctuationChecker` | Rule-based | Punctuation validation |

## Technology Stack

### Frontend
- **Framework**: Next.js 16 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **Icons**: lucide-react
- **File Parsing**: mammoth (for DOCX)

### Backend
- **Framework**: FastAPI
- **Language**: Python 3.10+
- **NLP**: NLTK (corpora)
- **File Parsing**: python-docx
