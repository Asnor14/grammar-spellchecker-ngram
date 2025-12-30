"""
Semantic Checker module.
"""
import re
from typing import List, Dict, Tuple

try:
    import nltk
    from nltk import pos_tag, word_tokenize
except ImportError:
    nltk = None

class SemanticChecker:
    # Universal Compatibility Matrix
    VERB_OBJECT_COMPATIBILITY = {
        'drink': {'compatible': {'water', 'coffee', 'tea', 'juice', 'milk', 'liquid', 'soda', 'wine', 'beer'}, 'incompatible': {'table', 'chair', 'book', 'phone', 'car', 'computer', 'tree', 'house'}},
        'eat': {'compatible': {'food', 'meal', 'lunch', 'dinner', 'apple', 'bread', 'pizza', 'meat', 'rice'}, 'incompatible': {'table', 'chair', 'car', 'computer', 'house', 'metal', 'glass', 'sky'}},
        'drive': {'compatible': {'car', 'bus', 'truck', 'van', 'vehicle'}, 'incompatible': {'book', 'water', 'food', 'ocean', 'sea', 'river', 'sky', 'cloud', 'house'}},
        'fly': {'compatible': {'plane', 'kite', 'drone', 'helicopter'}, 'incompatible': {'house', 'car', 'road', 'ocean', 'desk', 'book'}},
        'read': {'compatible': {'book', 'paper', 'email', 'story', 'article', 'news', 'text'}, 'incompatible': {'water', 'food', 'car', 'sky', 'chair'}},
        'write': {'compatible': {'letter', 'email', 'book', 'story', 'code', 'essay', 'report'}, 'incompatible': {'water', 'food', 'car', 'sky', 'air'}},
        'wear': {'compatible': {'clothes', 'shirt', 'dress', 'pants', 'shoes', 'hat', 'glasses'}, 'incompatible': {'car', 'house', 'food', 'water', 'book'}},
        'solve': {'compatible': {'problem', 'puzzle', 'mystery', 'question', 'issue'}, 'incompatible': {'water', 'food', 'car', 'dog', 'cat', 'tree'}},
    }
    
    def __init__(self):
        if nltk: 
            try: nltk.data.find('tokenizers/punkt')
            except: nltk.download('punkt', quiet=True)
            try: nltk.data.find('taggers/averaged_perceptron_tagger')
            except: nltk.download('averaged_perceptron_tagger', quiet=True)

    def check_text(self, text: str) -> List[Dict]:
        errors = []
        if not nltk: return []
        
        try: tags = pos_tag(word_tokenize(text))
        except: return []
        
        priority_verbs = set(self.VERB_OBJECT_COMPATIBILITY.keys())
        
        for i, (word, tag) in enumerate(tags):
            verb = word.lower()
            is_verb = tag.startswith('VB')
            
            # Universal Fallback: If it's a known verb, check it regardless of tag
            if not is_verb and verb in priority_verbs:
                is_verb = True
            
            if is_verb:
                # Normalize verb
                if verb.endswith('ing'): base = verb[:-3]
                elif verb.endswith('ed'): base = verb[:-2]
                elif verb in {'drove', 'driven'}: base = 'drive'
                elif verb in {'ate', 'eaten'}: base = 'eat'
                elif verb in {'drank', 'drunk'}: base = 'drink'
                elif verb in {'wrote', 'written'}: base = 'write'
                elif verb in {'ran', 'run'}: base = 'run'
                else: base = verb
                
                if base in self.VERB_OBJECT_COMPATIBILITY:
                    for j in range(i+1, min(i+6, len(tags))):
                        obj, obj_tag = tags[j]
                        if obj_tag.startswith('NN') or obj_tag.startswith('PRP'):
                            data = self.VERB_OBJECT_COMPATIBILITY[base]
                            if obj.lower() in data['incompatible']:
                                errors.append({
                                    'type': 'semantic',
                                    'position': {'start': 0, 'end': len(text)}, 
                                    'original': obj,
                                    'suggestion': f'[Check logic: can you {base} {obj}?]'.replace('  ', ' '),
                                    'explanation': f'Semantic Error: "{obj}" is incompatible with "{base}".',
                                    'sentenceIndex': 0
                                })
                            break
        return errors

_semantic_checker = None
def get_semantic_checker():
    global _semantic_checker
    if _semantic_checker is None: _semantic_checker = SemanticChecker()
    return _semantic_checker
