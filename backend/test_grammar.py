"""Test script to debug grammar checker."""

text = 'my brother buy a new phone but it battery are drain very fast'

# Test positions
print(f"Text: '{text}'")
print(f"Length: {len(text)}")
print()

# Check character positions
print("Character positions:")
print(f"  'it' should be at 31-33: '{text[31:33]}' (actual)")
print(f"  'battery' should be at 34-41: '{text[34:41]}' (actual)")
print(f"  'are' should be at 42-45: '{text[42:45]}' (actual)")
print(f"  'drain' should be at 46-51: '{text[46:51]}' (actual)")
print()

# Test grammar rules checker
from app.models.grammar_rules import GrammarRulesChecker
checker = GrammarRulesChecker()
errors = checker.check_text(text)

print("Errors from grammar rules checker:")
for e in errors:
    s = e['position']['start']
    end = e['position']['end']
    print(f"  Position {s}:{end} - '{text[s:end]}' -> '{e['suggestion']}'")
print()

# Test apply_corrections
def apply_corrections(text, errors):
    if not errors:
        return text
    
    # Sort errors by position (reverse order for safe replacement)
    sorted_errors = sorted(errors, key=lambda e: e['position']['start'], reverse=True)
    
    print("Applying corrections in order:")
    result = text
    for error in sorted_errors:
        start = error['position']['start']
        end = error['position']['end']
        suggestion = error['suggestion']
        
        before = result
        result = result[:start] + suggestion + result[end:]
        print(f"  Replace '{before[start:end]}' with '{suggestion}' at {start}:{end}")
        print(f"    Result: '{result}'")
    
    return result

corrected = apply_corrections(text, errors)
print()
print(f"Final result: '{corrected}'")
