# Troubleshooting Guide

## Common Issues

### Frontend Issues

#### 1. "Failed to fetch" Error

**Symptom**: Error message when clicking "Check Grammar"

**Causes**:
- Backend server not running
- CORS configuration issue
- Wrong API URL

**Solutions**:
1. Ensure backend is running: `uvicorn app.main:app --reload --port 8000`
2. Check if backend is accessible: `curl http://localhost:8000/health`
3. Verify `NEXT_PUBLIC_API_URL` in `.env.local` matches backend URL

#### 2. Blank Page / Component Not Rendering

**Symptom**: White screen or missing UI elements

**Solutions**:
1. Clear browser cache and refresh
2. Check browser console for JavaScript errors
3. Run `npm run build` to check for build errors
4. Delete `.next` folder and restart: `rm -rf .next && npm run dev`

#### 3. Styling Issues

**Symptom**: Colors or layouts look wrong

**Solutions**:
1. Ensure Tailwind is properly configured
2. Check `globals.css` has `@import "tailwindcss"`
3. Clear browser cache
4. Verify CSS variables are defined in `:root`

---

### Backend Issues

#### 1. NLTK Download Failures

**Symptom**: Error during model initialization

```
LookupError: Resource 'corpora/brown' not found.
```

**Solutions**:
1. Manual download in Python:
```python
import nltk
nltk.download('brown')
nltk.download('gutenberg')
nltk.download('punkt')
```

2. If behind firewall/proxy:
```python
import nltk
import ssl
ssl._create_default_https_context = ssl._create_unverified_context
nltk.download('brown')
```

3. Set NLTK data path:
```python
import nltk
nltk.data.path.append('/path/to/nltk_data')
```

#### 2. Import Errors

**Symptom**: `ModuleNotFoundError`

**Solutions**:
1. Ensure virtual environment is activated
2. Reinstall dependencies: `pip install -r requirements.txt`
3. Check Python version: `python --version` (need 3.10+)
4. Verify you're in the `backend` directory when running

#### 3. Model Loading Slow

**Symptom**: Server takes a long time to start

**Explanation**: First startup loads and trains on both corpora (~3 million words)

**Solutions**:
1. Wait for initial load (typically 30-60 seconds)
2. Use `--reload` for development (models persist between code changes)
3. For production, consider caching the trained model

#### 4. Memory Issues

**Symptom**: `MemoryError` or process killed

**Solutions**:
1. Ensure at least 2GB RAM available
2. Close other applications
3. Reduce corpus size by modifying `initialize_model()`

---

### Analysis Issues

#### 1. Too Many False Positives

**Symptom**: Correct words flagged as errors

**Solutions**:
1. Use trigram mode for better context
2. Add words to vocabulary in `spell_checker.py`
3. Adjust probability threshold in `grammar.py` (currently 0.3)

#### 2. Corrections Not Applied

**Symptom**: Click "Apply Fix" but nothing happens

**Solutions**:
1. Check browser console for errors
2. Ensure the error position is valid
3. Clear sessionStorage and try again

#### 3. File Upload Fails

**Symptom**: Error when uploading file

**Solutions**:
1. Check file size (max 5MB)
2. Ensure file is `.txt` or `.docx`
3. For DOCX, ensure `python-docx` is installed
4. Check file encoding (UTF-8 recommended for TXT)

---

### Performance Tuning

#### Slow Analysis

**Causes**:
- Long text
- Many sentences
- First request (model loading)

**Solutions**:
1. Split long texts into smaller chunks
2. Use bigram mode for faster (but less accurate) results
3. Consider caching frequent analyses

#### High Memory Usage

**Solutions**:
1. Limit vocabulary size
2. Use only Brown OR Gutenberg corpus (not both)
3. Reduce n-gram storage with pruning

---

### Development Issues

#### 1. Hot Reload Not Working

**Frontend**:
```bash
rm -rf .next
npm run dev
```

**Backend**:
```bash
uvicorn app.main:app --reload
```

#### 2. TypeScript Errors

**Solutions**:
1. Check type definitions in `types/analysis.ts`
2. Run `npm run lint` for detailed errors
3. Verify import paths use `@/app/...` syntax

#### 3. Python Type Hints

**If using type checking**:
```bash
pip install mypy
mypy app/
```

---

### Deployment Issues

#### CORS in Production

Update `main.py`:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-frontend-domain.com"],
    ...
)
```

#### Environment Variables

**Frontend (Vercel)**:
- Set `NEXT_PUBLIC_API_URL` in project settings

**Backend (Docker/Cloud)**:
- No special variables needed
- Ensure port 8000 is exposed

---

## Getting Help

If issues persist:

1. Check console/terminal for error messages
2. Review server logs for stack traces
3. Test API endpoints directly with curl
4. Verify all dependencies are installed
5. Check that both frontend and backend are running
