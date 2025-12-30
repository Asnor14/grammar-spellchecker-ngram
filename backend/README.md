# Grammar Checker Backend

FastAPI backend for the Grammar Checker application using statistical n-gram language models.

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
```

2. Activate the virtual environment:
- Windows: `venv\Scripts\activate`
- Linux/Mac: `source venv/bin/activate`

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Download NLTK data (run once):
```bash
python -c "import nltk; nltk.download('brown'); nltk.download('gutenberg'); nltk.download('punkt')"
```

5. Run the server:
```bash
uvicorn app.main:app --reload --port 8000
```

## API Endpoints

- `POST /check-text` - Analyze text for grammar, spelling, and punctuation errors
- `POST /check-file` - Upload and analyze a text file (.txt or .docx)
- `GET /health` - Health check endpoint

## Model

The backend uses an interpolated trigram language model with Kneser-Ney smoothing, trained on the Brown and Gutenberg corpora.
