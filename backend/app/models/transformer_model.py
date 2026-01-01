
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

# Global instance
_transformer_checker: Optional[TransformerGrammarChecker] = None

def get_transformer_checker() -> TransformerGrammarChecker:
    """Get global instance."""
    global _transformer_checker
    if _transformer_checker is None:
        _transformer_checker = TransformerGrammarChecker()
    return _transformer_checker
