# Grammar Checker

An academic-grade Grammar, Spelling, and Punctuation Checker using statistical n-gram language models.

## Features

- ✅ **Text Analysis**: Check grammar, spelling, and punctuation errors
- ✅ **File Upload**: Support for TXT and DOCX files
- ✅ **N-gram Models**: Bigram and Trigram analysis modes
- ✅ **Kneser-Ney Smoothing**: Advanced probability estimation
- ✅ **Confidence Score**: 0-100 grammar confidence rating
- ✅ **Error Highlighting**: Inline visualization of errors
- ✅ **Before/After Comparison**: See corrections side-by-side
- ✅ **Responsive Design**: Works on mobile, tablet, and desktop
- ✅ **No LLMs**: Fully statistical, deterministic results

## Tech Stack

| Component | Technology |
|-----------|------------|
| Frontend | Next.js 16, TypeScript, Tailwind CSS |
| Backend | Python FastAPI |
| NLP | NLTK (Brown + Gutenberg corpora) |
| Icons | lucide-react |

## Quick Start

### Frontend

```bash
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000)

### Backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
python -c "import nltk; nltk.download('brown'); nltk.download('gutenberg'); nltk.download('punkt')"
uvicorn app.main:app --reload --port 8000
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/check-text` | Analyze text input |
| POST | `/check-file` | Analyze uploaded file |
| GET | `/health` | Health check |

## Example

**Input:**
```
my brother buy a new phone but it battery are drain very fast
```

**Output:**
```
My brother bought a new phone, but its battery is draining very fast.
```

## Model Details

The system uses an **Interpolated Trigram Language Model** with **Kneser-Ney smoothing**:

```
P(w_i | w_{i-2}, w_{i-1}) = 0.5 × P_trigram + 0.3 × P_bigram + 0.2 × P_unigram
```

Trained on:
- **Brown Corpus**: ~1M words of American English
- **Gutenberg Corpus**: ~2M words of classic literature

## Documentation

- [System Overview](docs/system-overview.md)
- [Installation Guide](docs/installation-guide.md)
- [User Manual](docs/user-manual.md)
- [Model Explanation](docs/model-explanation.md)
- [Troubleshooting](docs/troubleshooting.md)

## Project Structure

```
grammar-checker/
├── app/                    # Next.js frontend
│   ├── components/         # React components
│   ├── lib/               # API and utilities
│   ├── types/             # TypeScript types
│   └── result/            # Results page
├── backend/               # Python backend
│   ├── app/
│   │   ├── api/          # FastAPI endpoints
│   │   ├── models/       # NLP models
│   │   └── utils/        # Utilities
│   └── requirements.txt
└── docs/                  # Documentation
```

## License

MIT License
