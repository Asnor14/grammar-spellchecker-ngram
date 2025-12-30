import sys
import os

# Add the current directory to sys.path so we can import backend
sys.path.append(os.getcwd())

print("Attempting to import grammar_rules...")
try:
    from backend.app.models import grammar_rules
    print("SUCCESS: grammar_rules imported.")
except Exception as e:
    print(f"FAILED: grammar_rules import failed: {e}")
    import traceback
    traceback.print_exc()

print("\nAttempting to import pos_ngram_model...")
try:
    from backend.app.models import pos_ngram_model
    print("SUCCESS: pos_ngram_model imported.")
except Exception as e:
    print(f"FAILED: pos_ngram_model import failed: {e}")
    import traceback
    traceback.print_exc()
