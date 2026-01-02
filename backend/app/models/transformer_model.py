
from typing import List, Dict, Optional
from app.utils.diff_utils import generate_diff

class TransformerGrammarChecker:
    """
    Grammar checker using a Transformer model (CoEdit by Grammarly).
    """
    
    MODEL_NAME = "grammarly/coedit-large"
    
    def __init__(self):
        """Initialize the model and tokenizer."""
        print(f"Loading Transformer model: {self.MODEL_NAME}...")
        self.pipe = None
        self.tokenizer = None
        self.model = None
        
        try:
            import torch
            from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, pipeline
            
            # Use GPU if available
            self.device = 0 if torch.cuda.is_available() else -1
            print(f"Model loaded. Using device: {'GPU' if self.device == 0 else 'CPU'}")
            
            self.tokenizer = AutoTokenizer.from_pretrained(self.MODEL_NAME)
            self.model = AutoModelForSeq2SeqLM.from_pretrained(self.MODEL_NAME)
            
            self.pipe = pipeline(
                "text2text-generation",
                model=self.model,
                tokenizer=self.tokenizer,
                device=self.device
            )
        except ImportError as e:
            print(f"Error: Transformers library not found. Please install requirements. {e}")
        except Exception as e:
            print(f"Error loading Transformer model: {e}")

    def check_text(self, text: str) -> List[Dict]:
        """
        Check text using the Transformer model.
        
        Args:
            text: Input text
            
        Returns:
            List of error dictionaries
        """
        if not self.pipe:
            print("Model not initialized (missing dependencies or download failed).")
            return []
            
        if not text.strip():
            return []

        # CoEdit uses a specific instruction format
        input_text = f"Fix grammatical errors in this sentence: {text}"
        
        try:
            # Generate correction
            results = self.pipe(input_text, max_length=512)
            corrected_text = results[0]['generated_text']
            
            # Post-process to fix common Transformer artifacts
            corrected_text = self._post_process_output(corrected_text, text)
            
            # Basic validation: if corrected text is drastically shorter, something went wrong
            if len(corrected_text) < len(text) * 0.5:
                 print("Warning: Model output dubious (too short). Skipping.")
                 return []

            print(f"Original: {text}")
            print(f"AI Correction: {corrected_text}")
            
            # Generate diffs
            errors = generate_diff(text, corrected_text)
            return errors
            
        except Exception as e:
            print(f"Error during inference: {e}")
            return []

    def _post_process_output(self, corrected: str, original: str) -> str:
        """
        Post-process Transformer output to fix common artifacts.
        """
        import re
        
        # 1. Fix duplicate characters at word endings (becausee -> because)
        duplicate_fixes = {
            'becausee': 'because', 'becausse': 'because',
            'aboutt': 'about', 'withh': 'with',
            'forr': 'for', 'thee': 'the',
            'wass': 'was', 'weree': 'were',
            'hass': 'has', 'hadd': 'had',
            'didd': 'did', 'doess': 'does',
            'goess': 'goes', 'sayss': 'says',
            'gett': 'get', 'putt': 'put',
            'cutt': 'cut', 'lett': 'let',
            'sett': 'set', 'runn': 'run',
        }
        
        for wrong, right in duplicate_fixes.items():
            corrected = re.sub(r'\b' + wrong + r'\b', right, corrected, flags=re.IGNORECASE)
        
        # 2. Generic fix: Remove duplicate trailing letters (3+ of same char)
        corrected = re.sub(r'([a-zA-Z])\1{2,}', r'\1\1', corrected)
        
        # 3. Fix double consonants at word end that are usually wrong
        # Pattern: word ending in double consonant where single is correct
        corrected = re.sub(r'\b(\w+)([bcdfghjklmnpqrstvwxz])\2\b', 
                          lambda m: m.group(1) + m.group(2) if m.group(0).lower() not in 
                          {'ill', 'all', 'bell', 'tell', 'well', 'sell', 'fall', 'call', 'ball', 
                           'will', 'still', 'full', 'pull', 'miss', 'pass', 'boss', 'less', 
                           'class', 'grass', 'glass', 'cross', 'press', 'stress', 'dress',
                           'add', 'odd', 'egg', 'off', 'buff', 'stuff', 'cliff', 'stiff',
                           'jazz', 'buzz', 'fizz', 'fuzz'} else m.group(0), 
                          corrected)
        
        # 4. Remove consecutive duplicate words
        corrected = re.sub(r'\b(\w+)\s+\1\b', r'\1', corrected, flags=re.IGNORECASE)
        
        return corrected

# Global instance
_transformer_checker: Optional[TransformerGrammarChecker] = None

def get_transformer_checker() -> TransformerGrammarChecker:
    """Get global instance."""
    global _transformer_checker
    if _transformer_checker is None:
        _transformer_checker = TransformerGrammarChecker()
    return _transformer_checker
