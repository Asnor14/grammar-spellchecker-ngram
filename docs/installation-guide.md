# Installation Guide

## Prerequisites

Before installing, ensure you have:

- **Node.js** 18+ (for frontend)
- **Python** 3.10+ (for backend)
- **npm** or **yarn** (for package management)
- **pip** (for Python packages)

## Quick Start

### 1. Clone/Navigate to Project

```bash
cd grammar-checker
```

### 2. Frontend Setup

```bash
# Install dependencies
npm install

# Start development server
npm run dev
```

The frontend will be available at `http://localhost:3000`

### 3. Backend Setup

Open a new terminal window:

```bash
# Navigate to backend
cd backend

# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Download NLTK data (first time only)
python -c "import nltk; nltk.download('brown'); nltk.download('gutenberg'); nltk.download('punkt')"

# Start the server
uvicorn app.main:app --reload --port 8000
```

The backend API will be available at `http://localhost:8000`

## Verifying Installation

### Check Frontend

Open `http://localhost:3000` in your browser. You should see the Grammar Checker interface.

### Check Backend

```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "model_loaded": true,
  "vocabulary_size": 56000,
  "total_words": 1200000
}
```

### Test the API

```bash
curl -X POST http://localhost:8000/check-text \
  -H "Content-Type: application/json" \
  -d '{"text": "He go to school yesterday.", "ngram": "trigram"}'
```

## Environment Variables

### Frontend (.env.local)

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Backend

No environment variables required for basic setup.

## Production Deployment

### Frontend (Vercel/Netlify)

```bash
npm run build
npm start
```

### Backend (Docker)

```dockerfile
FROM python:3.10-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Download NLTK data
RUN python -c "import nltk; nltk.download('brown'); nltk.download('gutenberg'); nltk.download('punkt')"

COPY app ./app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## Troubleshooting

### NLTK Download Fails

If NLTK data download fails behind a firewall:

```python
import nltk
import ssl
ssl._create_default_https_context = ssl._create_unverified_context
nltk.download('brown')
nltk.download('gutenberg')
nltk.download('punkt')
```

### CORS Issues

Ensure the backend CORS middleware includes your frontend URL:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    ...
)
```

### Port Conflicts

If ports 3000 or 8000 are in use:

```bash
# Frontend on different port
npm run dev -- -p 3001

# Backend on different port
uvicorn app.main:app --port 8001
```

Update `NEXT_PUBLIC_API_URL` accordingly.
