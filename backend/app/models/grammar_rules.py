"""
Rule-Based Grammar Checker module.
Handles specific grammar rules that statistical models can't reliably detect.
"""

import re
from typing import List, Dict, Tuple, Set


class GrammarRulesChecker:
    """
    Rule-based grammar checker for common grammar errors.
    
    Handles:
    - Subject-verb agreement
    - Verb tense consistency
    - Pronoun forms (it vs its)
    - Capitalization rules
    - Common grammar patterns
    """
    
    # Verb conjugations for common irregular verbs
    VERB_FORMS = {
        # base: (past, past_participle, present_3rd, present_participle)
        'buy': ('bought', 'bought', 'buys', 'buying'),
        'go': ('went', 'gone', 'goes', 'going'),
        'get': ('got', 'gotten', 'gets', 'getting'),
        'make': ('made', 'made', 'makes', 'making'),
        'take': ('took', 'taken', 'takes', 'taking'),
        'see': ('saw', 'seen', 'sees', 'seeing'),
        'come': ('came', 'come', 'comes', 'coming'),
        'know': ('knew', 'known', 'knows', 'knowing'),
        'think': ('thought', 'thought', 'thinks', 'thinking'),
        'say': ('said', 'said', 'says', 'saying'),
        'give': ('gave', 'given', 'gives', 'giving'),
        'find': ('found', 'found', 'finds', 'finding'),
        'tell': ('told', 'told', 'tells', 'telling'),
        'put': ('put', 'put', 'puts', 'putting'),
        'leave': ('left', 'left', 'leaves', 'leaving'),
        'do': ('did', 'done', 'does', 'doing'),
        'have': ('had', 'had', 'has', 'having'),
        'be': ('was', 'been', 'is', 'being'),
        'write': ('wrote', 'written', 'writes', 'writing'),
        'read': ('read', 'read', 'reads', 'reading'),
        'run': ('ran', 'run', 'runs', 'running'),
        'eat': ('ate', 'eaten', 'eats', 'eating'),
        'drink': ('drank', 'drunk', 'drinks', 'drinking'),
        'speak': ('spoke', 'spoken', 'speaks', 'speaking'),
        'drive': ('drove', 'driven', 'drives', 'driving'),
        'grow': ('grew', 'grown', 'grows', 'growing'),
        'throw': ('threw', 'thrown', 'throws', 'throwing'),
        'begin': ('began', 'begun', 'begins', 'beginning'),
        'sing': ('sang', 'sung', 'sings', 'singing'),
        'swim': ('swam', 'swum', 'swims', 'swimming'),
        'ring': ('rang', 'rung', 'rings', 'ringing'),
        'sit': ('sat', 'sat', 'sits', 'sitting'),
        'stand': ('stood', 'stood', 'stands', 'standing'),
        'lose': ('lost', 'lost', 'loses', 'losing'),
        'win': ('won', 'won', 'wins', 'winning'),
        'pay': ('paid', 'paid', 'pays', 'paying'),
        'meet': ('met', 'met', 'meets', 'meeting'),
        'send': ('sent', 'sent', 'sends', 'sending'),
        'build': ('built', 'built', 'builds', 'building'),
        'fall': ('fell', 'fallen', 'falls', 'falling'),
        'cut': ('cut', 'cut', 'cuts', 'cutting'),
        'keep': ('kept', 'kept', 'keeps', 'keeping'),
        'feel': ('felt', 'felt', 'feels', 'feeling'),
        'bring': ('brought', 'brought', 'brings', 'bringing'),
        'hold': ('held', 'held', 'holds', 'holding'),
        'catch': ('caught', 'caught', 'catches', 'catching'),
        'teach': ('taught', 'taught', 'teaches', 'teaching'),
        'understand': ('understood', 'understood', 'understands', 'understanding'),
        'break': ('broke', 'broken', 'breaks', 'breaking'),
        'spend': ('spent', 'spent', 'spends', 'spending'),
        'sleep': ('slept', 'slept', 'sleeps', 'sleeping'),
        'hear': ('heard', 'heard', 'hears', 'hearing'),
        'lead': ('led', 'led', 'leads', 'leading'),
        'fly': ('flew', 'flown', 'flies', 'flying'),
        'wear': ('wore', 'worn', 'wears', 'wearing'),
        'show': ('showed', 'shown', 'shows', 'showing'),
        'steal': ('stole', 'stolen', 'steals', 'stealing'),
        'hide': ('hid', 'hidden', 'hides', 'hiding'),
        'choose': ('chose', 'chosen', 'chooses', 'choosing'),
        'forget': ('forgot', 'forgotten', 'forgets', 'forgetting'),
        'rise': ('rose', 'risen', 'rises', 'rising'),
        'wake': ('woke', 'woken', 'wakes', 'waking'),
        'freeze': ('froze', 'frozen', 'freezes', 'freezing'),
        'shake': ('shook', 'shaken', 'shakes', 'shaking'),
        'draw': ('drew', 'drawn', 'draws', 'drawing'),
        'bite': ('bit', 'bitten', 'bites', 'biting'),
        'blow': ('blew', 'blown', 'blows', 'blowing'),
        # Regular verbs (add -ed for past)
        'drain': ('drained', 'drained', 'drains', 'draining'),
        'walk': ('walked', 'walked', 'walks', 'walking'),
        'talk': ('talked', 'talked', 'talks', 'talking'),
        'play': ('played', 'played', 'plays', 'playing'),
        'work': ('worked', 'worked', 'works', 'working'),
        'look': ('looked', 'looked', 'looks', 'looking'),
        'use': ('used', 'used', 'uses', 'using'),
        'try': ('tried', 'tried', 'tries', 'trying'),
        'ask': ('asked', 'asked', 'asks', 'asking'),
        'need': ('needed', 'needed', 'needs', 'needing'),
        'want': ('wanted', 'wanted', 'wants', 'wanting'),
        'move': ('moved', 'moved', 'moves', 'moving'),
        'live': ('lived', 'lived', 'lives', 'living'),
        'believe': ('believed', 'believed', 'believes', 'believing'),
        'happen': ('happened', 'happened', 'happens', 'happening'),
        'allow': ('allowed', 'allowed', 'allows', 'allowing'),
        'help': ('helped', 'helped', 'helps', 'helping'),
        'start': ('started', 'started', 'starts', 'starting'),
        'stop': ('stopped', 'stopped', 'stops', 'stopping'),
        'change': ('changed', 'changed', 'changes', 'changing'),
        'follow': ('followed', 'followed', 'follows', 'following'),
        'create': ('created', 'created', 'creates', 'creating'),
        'open': ('opened', 'opened', 'opens', 'opening'),
        'close': ('closed', 'closed', 'closes', 'closing'),
        'call': ('called', 'called', 'calls', 'calling'),
        'wait': ('waited', 'waited', 'waits', 'waiting'),
        'remain': ('remained', 'remained', 'remains', 'remaining'),
        # Additional common verbs
        'like': ('liked', 'liked', 'likes', 'liking'),
        'prefer': ('preferred', 'preferred', 'prefers', 'preferring'),
        'watch': ('watched', 'watched', 'watches', 'watching'),
        'enjoy': ('enjoyed', 'enjoyed', 'enjoys', 'enjoying'),
        'hate': ('hated', 'hated', 'hates', 'hating'),
        'love': ('loved', 'loved', 'loves', 'loving'),
        'finish': ('finished', 'finished', 'finishes', 'finishing'),
        'avoid': ('avoided', 'avoided', 'avoids', 'avoiding'),
        'consider': ('considered', 'considered', 'considers', 'considering'),
        'suggest': ('suggested', 'suggested', 'suggests', 'suggesting'),
        'recommend': ('recommended', 'recommended', 'recommends', 'recommending'),
        'decide': ('decided', 'decided', 'decides', 'deciding'),
        'agree': ('agreed', 'agreed', 'agrees', 'agreeing'),
        'refuse': ('refused', 'refused', 'refuses', 'refusing'),
        'promise': ('promised', 'promised', 'promises', 'promising'),
        'manage': ('managed', 'managed', 'manages', 'managing'),
        'hope': ('hoped', 'hoped', 'hopes', 'hoping'),
        'expect': ('expected', 'expected', 'expects', 'expecting'),
        'prepare': ('prepared', 'prepared', 'prepares', 'preparing'),
        'receive': ('received', 'received', 'receives', 'receiving'),
        'suppose': ('supposed', 'supposed', 'supposes', 'supposing'),
    }
    
    # Singular subjects that require singular verbs
    SINGULAR_SUBJECTS = {
        'he', 'she', 'it', 'this', 'that', 'everyone', 'someone', 'anyone',
        'no one', 'nobody', 'everybody', 'somebody', 'anybody', 'each',
        'either', 'neither', 'one', 'battery', 'phone', 'brother', 'sister',
        'mother', 'father', 'car', 'computer', 'person', 'man', 'woman',
        'child', 'boy', 'girl', 'friend', 'teacher', 'student', 'dog', 'cat',
    }
    
    # Plural subjects that require plural verbs
    PLURAL_SUBJECTS = {
        'they', 'we', 'these', 'those', 'people', 'children', 'men', 'women',
        'friends', 'students', 'teachers', 'boys', 'girls', 'dogs', 'cats',
    }
    
    # be verb forms
    BE_SINGULAR = {'is', 'was'}
    BE_PLURAL = {'are', 'were'}
    
    # Possessive pronouns mapping
    POSSESSIVE_MAP = {
        'it': 'its',
        'he': 'his', 
        'she': 'her',
        'they': 'their',
        'we': 'our',
        'i': 'my',
        'you': 'your',
    }
    
    def __init__(self):
        # Build reverse lookup for verb forms
        self.verb_base_lookup = {}
        for base, forms in self.VERB_FORMS.items():
            self.verb_base_lookup[base] = base
            for form in forms:
                if form not in self.verb_base_lookup:
                    self.verb_base_lookup[form] = base
    
    def check_text(self, text: str) -> List[Dict]:
        """
        Check text for grammar errors using rules.
        
        Args:
            text: Text to check
            
        Returns:
            List of error dictionaries
        """
        errors = []
        
        # Check capitalization at sentence start
        errors.extend(self._check_sentence_capitalization(text))
        
        # Tokenize for word-level checking
        words = self._tokenize(text)
        
        # Check contractions (dont -> doesn't, etc.)
        errors.extend(self._check_contractions(text, words))
        
        # Check subject-verb agreement
        errors.extend(self._check_subject_verb_agreement(text, words))
        
        # Check possessive pronouns
        errors.extend(self._check_possessive_pronouns(text, words))
        
        # Check verb tense after past tense markers
        errors.extend(self._check_verb_tense(text, words))
        
        # Check present participle with be verbs
        errors.extend(self._check_progressive_tense(text, words))
        
        # Check for 'say us' -> 'tell us' patterns
        errors.extend(self._check_say_to_tell(text, words))
        
        # Check for past tense verbs after conjunctions with past context
        errors.extend(self._check_past_tense_after_conjunction(text, words))
        
        # Check prefer/enjoy + gerund pattern
        errors.extend(self._check_gerund_patterns(text, words))
        
        # Check third person singular verb forms
        errors.extend(self._check_third_person_verbs(text, words))
        
        # Check plural nouns
        errors.extend(self._check_plural_nouns(text, words))
        
        # Check for past tense indicators after verbs (e.g., "win ... last week" -> "won")
        errors.extend(self._check_past_tense_indicator_after_verb(text, words))
        
        # Check for incorrect regularized past tense (e.g., "buyed" -> "bought")
        errors.extend(self._check_incorrect_regularized_past(text, words))
        
        return errors
    
    def _tokenize(self, text: str) -> List[Tuple[str, int, int]]:
        """Tokenize text into words with positions."""
        tokens = []
        for match in re.finditer(r"\b\w+(?:'\w+)?\b", text):
            tokens.append((match.group().lower(), match.start(), match.end()))
        return tokens
    
    def _check_sentence_capitalization(self, text: str) -> List[Dict]:
        """Check if sentences start with capital letters."""
        errors = []
        
        # Check first word
        first_word = re.match(r'^\s*([a-z]+)', text)
        if first_word:
            word = first_word.group(1)
            start = first_word.start(1)
            end = first_word.end(1)
            errors.append({
                'type': 'grammar',
                'position': {'start': start, 'end': end},
                'original': word,
                'suggestion': word.capitalize(),
                'explanation': 'Sentences should start with a capital letter.',
                'sentenceIndex': 0,
            })
        
        # Check after sentence-ending punctuation
        for match in re.finditer(r'[.!?]\s+([a-z])', text):
            char = match.group(1)
            pos = match.start(1)
            errors.append({
                'type': 'grammar',
                'position': {'start': pos, 'end': pos + 1},
                'original': char,
                'suggestion': char.upper(),
                'explanation': 'Sentences should start with a capital letter.',
                'sentenceIndex': 0,
            })
        
        return errors
    
    def _check_subject_verb_agreement(self, text: str, words: List[Tuple[str, int, int]]) -> List[Dict]:
        """Check subject-verb agreement."""
        errors = []
        
        for i, (word, start, end) in enumerate(words):
            # Check "it/battery/etc + are" → should be "is"
            if i > 0:
                prev_word = words[i - 1][0]
                
                # Singular subject + are → is
                if prev_word in self.SINGULAR_SUBJECTS and word == 'are':
                    errors.append({
                        'type': 'grammar',
                        'position': {'start': start, 'end': end},
                        'original': text[start:end],
                        'suggestion': 'is',
                        'explanation': f'Subject-verb agreement: "{prev_word}" is singular and requires "is" not "are".',
                        'sentenceIndex': 0,
                    })
                
                # Singular subject + were → was
                elif prev_word in self.SINGULAR_SUBJECTS and word == 'were':
                    errors.append({
                        'type': 'grammar',
                        'position': {'start': start, 'end': end},
                        'original': text[start:end],
                        'suggestion': 'was',
                        'explanation': f'Subject-verb agreement: "{prev_word}" is singular and requires "was" not "were".',
                        'sentenceIndex': 0,
                    })
                
                # Plural subject + is → are
                elif prev_word in self.PLURAL_SUBJECTS and word == 'is':
                    errors.append({
                        'type': 'grammar',
                        'position': {'start': start, 'end': end},
                        'original': text[start:end],
                        'suggestion': 'are',
                        'explanation': f'Subject-verb agreement: "{prev_word}" is plural and requires "are" not "is".',
                        'sentenceIndex': 0,
                    })
                
                # Plural subject + was → were
                # BUT skip if next word is a verb (will be handled by past tense check)
                elif prev_word in self.PLURAL_SUBJECTS and word == 'was':
                    # Check if next word is a verb - if so, skip (past tense check will handle)
                    next_word = words[i + 1][0] if i + 1 < len(words) else ""
                    past_indicators = {'yesterday', 'ago', 'last', 'before', 'earlier', 'previously', 'already'}
                    has_past_context = any(w[0] in past_indicators for w in words)
                    
                    # Only apply was→were if next word is NOT a verb in past context
                    if not (has_past_context and next_word in self.VERB_FORMS):
                        errors.append({
                            'type': 'grammar',
                            'position': {'start': start, 'end': end},
                            'original': text[start:end],
                            'suggestion': 'were',
                            'explanation': f'Subject-verb agreement: "{prev_word}" is plural and requires "were" not "was".',
                            'sentenceIndex': 0,
                        })
        
        return errors
    
    def _check_possessive_pronouns(self, text: str, words: List[Tuple[str, int, int]]) -> List[Dict]:
        """Check possessive pronoun usage."""
        errors = []
        
        # Common nouns that follow possessive pronouns
        possession_indicators = {
            'battery', 'phone', 'car', 'house', 'name', 'book', 'life',
            'work', 'job', 'friend', 'family', 'mother', 'father', 'brother',
            'sister', 'hand', 'head', 'eye', 'heart', 'mind', 'way',
            'time', 'place', 'home', 'room', 'door', 'window', 'color',
        }
        
        for i, (word, start, end) in enumerate(words):
            if i < len(words) - 1:
                next_word = words[i + 1][0]
                
                # Check for "it battery" → "its battery"
                if word == 'it' and next_word in possession_indicators:
                    errors.append({
                        'type': 'grammar',
                        'position': {'start': start, 'end': end},
                        'original': text[start:end],
                        'suggestion': 'its',
                        'explanation': 'Use "its" (possessive) to show ownership, not "it".',
                        'sentenceIndex': 0,
                    })
                
                # Check for other pronouns before nouns
                elif word in self.POSSESSIVE_MAP and next_word in possession_indicators:
                    possessive = self.POSSESSIVE_MAP[word]
                    # Only flag if it's clearly wrong (not already possessive)
                    if word != possessive and not word.endswith('s') and word not in {'my', 'your', 'his', 'her', 'its', 'our', 'their'}:
                        errors.append({
                            'type': 'grammar',
                            'position': {'start': start, 'end': end},
                            'original': text[start:end],
                            'suggestion': possessive,
                            'explanation': f'Use "{possessive}" (possessive) to show ownership.',
                            'sentenceIndex': 0,
                        })
        
        return errors
    
    def _check_verb_tense(self, text: str, words: List[Tuple[str, int, int]]) -> List[Dict]:
        """Check verb tense consistency after past tense contexts."""
        errors = []
        
        # Past tense indicators
        past_indicators = {'yesterday', 'ago', 'last', 'before', 'earlier', 'previously', 'already'}
        
        # Words that indicate a completed action with ongoing result (use past tense)
        # e.g., "bought a new phone but..." suggests the buying happened in the past
        result_context = {'but', 'however', 'unfortunately', 'sadly', 'yet', 'still', 'now'}
        
        has_past_context = any(w[0] in past_indicators for w in words)
        has_result_context = any(w[0] in result_context for w in words)
        
        # Check for third person singular subject + base verb
        for i, (word, start, end) in enumerate(words):
            if i > 0:
                prev_word = words[i - 1][0]
                
                # Check if there's result context after this word
                has_result_after = any(w[0] in result_context for w in words[i:])
                
                # "brother/sister/he/she + buy" → "bought" if past context or result context
                if prev_word in {'brother', 'sister', 'he', 'she', 'it', 'mother', 'father', 'friend'}:
                    if word in self.VERB_FORMS:
                        forms = self.VERB_FORMS[word]
                        
                        # Determine tense based on context
                        if has_past_context or has_result_after:
                            # Use past tense for completed actions
                            correct = forms[0]  # past tense
                            errors.append({
                                'type': 'grammar',
                                'position': {'start': start, 'end': end},
                                'original': text[start:end],
                                'suggestion': correct,
                                'explanation': f'Verb tense: Use "{correct}" (past tense) for completed actions.',
                                'sentenceIndex': 0,
                            })
                        else:
                            # Use present 3rd person for habitual/general statements
                            correct = forms[2]  # present 3rd person
                            errors.append({
                                'type': 'grammar',
                                'position': {'start': start, 'end': end},
                                'original': text[start:end],
                                'suggestion': correct,
                                'explanation': f'Subject-verb agreement: Use "{correct}" with third-person singular subject.',
                                'sentenceIndex': 0,
                            })
        
        return errors
    
    def _check_say_to_tell(self, text: str, words: List[Tuple[str, int, int]]) -> List[Dict]:
        """Check for incorrect usage of 'say' with object pronouns (should be 'tell')."""
        errors = []
        
        # say/said/says + object pronoun -> tell/told/tells + object pronoun
        say_forms = {
            'say': 'tell',
            'says': 'tells',
            'said': 'told',
            'saying': 'telling'
        }
        
        # Object pronouns that usually require 'tell' instead of 'say'
        object_pronouns = {'me', 'us', 'him', 'them', 'you', 'her'}
        
        for i, (word, start, end) in enumerate(words):
            # Check if current word is a form of 'say'
            if word in say_forms:
                # Check next word
                if i + 1 < len(words):
                    next_word = words[i + 1][0]
                    next_start = words[i + 1][1]
                    next_end = words[i + 1][2]
                    
                    if next_word in object_pronouns:
                        # Determine correct form (tell vs tells vs told)
                        suggestion = say_forms[word]
                        
                        # If suggesting 'tell', check if subject is singular (needs 'tells')
                        # Only if original word was 'say' (present)
                        if suggestion == 'tell':
                            # Look back for subject
                            prev_word = words[i - 1][0] if i > 0 else ""
                            # Simple check for known singular subjects
                            if prev_word in self.SINGULAR_SUBJECTS or prev_word in {'he', 'she', 'it'}:
                                suggestion = 'tells'
                        
                        errors.append({
                            'type': 'grammar',
                            'position': {'start': start, 'end': end},
                            'original': text[start:end],
                            'suggestion': suggestion,
                            'explanation': f'Use "{suggestion}" instead of "{word}" when followed by an object pronoun like "{next_word}".',
                            'sentenceIndex': 0,
                        })
        
        return errors

    def _check_progressive_tense(self, text: str, words: List[Tuple[str, int, int]]) -> List[Dict]:
        """Check for be + base verb patterns that should be progressive or past tense."""
        errors = []
        
        be_verbs = {'is', 'are', 'was', 'were', 'am'}
        past_be_verbs = {'was', 'were'}
        
        # Past tense indicators
        past_indicators = {'yesterday', 'ago', 'last', 'before', 'earlier', 'previously', 'already'}
        has_past_context = any(w[0] in past_indicators for w in words)
        
        for i, (word, start, end) in enumerate(words):
            if i > 0:
                prev_word = words[i - 1][0]
                
                if prev_word in be_verbs and word in self.VERB_FORMS:
                    forms = self.VERB_FORMS[word]
                    
                    # Skip certain verbs
                    if word in {'be', 'have', 'been'}:
                        continue
                    
                    # If we have past context and past be verb (was/were + go),
                    # suggest just the past tense verb (went) and remove was/were
                    if has_past_context and prev_word in past_be_verbs:
                        past_tense = forms[0]  # past tense
                        # Get the position of "was/were" to include it in the replacement
                        prev_start = words[i - 1][1]
                        errors.append({
                            'type': 'grammar',
                            'position': {'start': prev_start, 'end': end},  # Include was/were
                            'original': text[prev_start:end],  # "was go"
                            'suggestion': past_tense,  # "went"
                            'explanation': f'Use past tense "{past_tense}" instead of "{prev_word} {word}".',
                            'sentenceIndex': 0,
                        })
                    else:
                        # Normal progressive suggestion
                        progressive = forms[3]  # present participle (-ing form)
                        errors.append({
                            'type': 'grammar',
                            'position': {'start': start, 'end': end},
                            'original': text[start:end],
                            'suggestion': progressive,
                            'explanation': f'Use "{progressive}" (present participle) with "{prev_word}" for ongoing action.',
                            'sentenceIndex': 0,
                        })
        
        return errors
    
    def _check_past_tense_after_conjunction(self, text: str, words: List[Tuple[str, int, int]]) -> List[Dict]:
        """Check for verbs after conjunctions that should be past tense."""
        errors = []
        
        # Past tense indicators
        past_indicators = {'yesterday', 'ago', 'last', 'before', 'earlier', 'previously', 'already'}
        has_past_context = any(w[0] in past_indicators for w in words)
        
        if not has_past_context:
            return errors
        
        conjunctions = {'and', 'then'}
        
        for i, (word, start, end) in enumerate(words):
            if i > 0:
                prev_word = words[i - 1][0]
                
                # Check if previous word is a conjunction
                if prev_word in conjunctions and word in self.VERB_FORMS:
                    forms = self.VERB_FORMS[word]
                    past_tense = forms[0]  # past tense
                    
                    # Only suggest if current word is the base form
                    if word != past_tense:
                        errors.append({
                            'type': 'grammar',
                            'position': {'start': start, 'end': end},
                            'original': text[start:end],
                            'suggestion': past_tense,
                            'explanation': f'Use past tense "{past_tense}" to match the sentence context.',
                            'sentenceIndex': 0,
                        })
        
        return errors
    
    def _check_contractions(self, text: str, words: List[Tuple[str, int, int]]) -> List[Dict]:
        """Check for incorrect contractions and missing apostrophes."""
        errors = []
        
        # Common misspelled contractions with context
        # Format: misspelling -> {singular_subject: correction, plural_subject: correction}
        contraction_fixes = {
            'dont': {'default': "don't", 'third_singular': "doesn't"},
            'doesnt': {'default': "doesn't", 'third_singular': "doesn't"},
            'didnt': {'default': "didn't", 'third_singular': "didn't"},
            'wont': {'default': "won't", 'third_singular': "won't"},
            'cant': {'default': "can't", 'third_singular': "can't"},
            'couldnt': {'default': "couldn't", 'third_singular': "couldn't"},
            'wouldnt': {'default': "wouldn't", 'third_singular': "wouldn't"},
            'shouldnt': {'default': "shouldn't", 'third_singular': "shouldn't"},
            'isnt': {'default': "isn't", 'third_singular': "isn't"},
            'arent': {'default': "aren't", 'third_singular': "aren't"},
            'wasnt': {'default': "wasn't", 'third_singular': "wasn't"},
            'werent': {'default': "weren't", 'third_singular': "weren't"},
            'hasnt': {'default': "hasn't", 'third_singular': "hasn't"},
            'havent': {'default': "haven't", 'third_singular': "haven't"},
            'hadnt': {'default': "hadn't", 'third_singular': "hadn't"},
            'ive': {'default': "I've", 'third_singular': "I've"},
            'youve': {'default': "you've", 'third_singular': "you've"},
            'theyve': {'default': "they've", 'third_singular': "they've"},
            'weve': {'default': "we've", 'third_singular': "we've"},
            'hes': {'default': "he's", 'third_singular': "he's"},
            'shes': {'default': "she's", 'third_singular': "she's"},
            'its': {'default': "it's", 'third_singular': "it's"},  # Note: context matters for its vs it's
            'thats': {'default': "that's", 'third_singular': "that's"},
            'whats': {'default': "what's", 'third_singular': "what's"},
            'heres': {'default': "here's", 'third_singular': "here's"},
            'theres': {'default': "there's", 'third_singular': "there's"},
            'im': {'default': "I'm", 'third_singular': "I'm"},
            'youre': {'default': "you're", 'third_singular': "you're"},
            'theyre': {'default': "they're", 'third_singular': "they're"},
            'were': {'default': "we're", 'third_singular': "we're"},
            'ill': {'default': "I'll", 'third_singular': "I'll"},
            'youll': {'default': "you'll", 'third_singular': "you'll"},
            'theyll': {'default': "they'll", 'third_singular': "they'll"},
            'well': {'default': "we'll", 'third_singular': "we'll"},
            'hell': {'default': "he'll", 'third_singular': "he'll"},
            'shell': {'default': "she'll", 'third_singular': "she'll"},
            'itll': {'default': "it'll", 'third_singular': "it'll"},
        }
        
        for i, (word, start, end) in enumerate(words):
            if word in contraction_fixes:
                fixes = contraction_fixes[word]
                
                # Check previous word for subject
                prev_word = words[i - 1][0] if i > 0 else ""
                
                # Use third person singular form if subject is he/she/it or singular noun
                if prev_word in self.SINGULAR_SUBJECTS:
                    suggestion = fixes.get('third_singular', fixes['default'])
                else:
                    suggestion = fixes['default']
                
                # Special case: "dont" after "she/he/it" -> "doesn't"
                if word == 'dont' and prev_word in {'she', 'he', 'it'} | self.SINGULAR_SUBJECTS:
                    suggestion = "doesn't"
                
                errors.append({
                    'type': 'grammar',
                    'position': {'start': start, 'end': end},
                    'original': text[start:end],
                    'suggestion': suggestion,
                    'explanation': f'Use "{suggestion}" with proper apostrophe.',
                    'sentenceIndex': 0,
                })
        
        return errors
    
    def _check_gerund_patterns(self, text: str, words: List[Tuple[str, int, int]]) -> List[Dict]:
        """Check for verbs that require gerund (-ing) forms after them."""
        errors = []
        
        # Verbs that take gerund (verb + -ing)
        gerund_verbs = {'prefer', 'prefers', 'preferred', 'enjoy', 'enjoys', 'enjoyed',
                        'like', 'likes', 'liked', 'love', 'loves', 'loved',
                        'hate', 'hates', 'hated', 'start', 'starts', 'started',
                        'begin', 'begins', 'began', 'stop', 'stops', 'stopped',
                        'keep', 'keeps', 'kept', 'finish', 'finishes', 'finished',
                        'avoid', 'avoids', 'avoided', 'consider', 'considers', 'considered',
                        'suggest', 'suggests', 'suggested', 'recommend', 'recommends', 'recommended'}
        
        for i, (word, start, end) in enumerate(words):
            if i > 0:
                prev_word = words[i - 1][0]
                
                # If previous word is a gerund verb and current word is a base verb
                if prev_word in gerund_verbs and word in self.VERB_FORMS:
                    forms = self.VERB_FORMS[word]
                    gerund = forms[3]  # present participle (-ing form)
                    
                    errors.append({
                        'type': 'grammar',
                        'position': {'start': start, 'end': end},
                        'original': text[start:end],
                        'suggestion': gerund,
                        'explanation': f'Use "{gerund}" (gerund) after "{prev_word}".',
                        'sentenceIndex': 0,
                    })
        
        return errors
    
    def _check_third_person_verbs(self, text: str, words: List[Tuple[str, int, int]]) -> List[Dict]:
        """Check for missing -s on third person singular verbs."""
        errors = []
        
        # Third person singular subjects
        third_person_singular = {'she', 'he', 'it'} | self.SINGULAR_SUBJECTS
        
        # Conjunctions that continue the subject
        conjunctions = {'and', 'or', 'but'}
        
        # Skip these verbs as they're handled elsewhere or are correct as-is
        skip_verbs = {'be', 'is', 'are', 'was', 'were', 'have', 'has', 'had',
                      'do', 'does', 'did', 'can', 'could', 'will', 'would',
                      'shall', 'should', 'may', 'might', 'must'}
        
        # Find the sentence subject (first third person singular word)
        sentence_subject = None
        for word, _, _ in words:
            if word in third_person_singular:
                sentence_subject = word
                break
        
        for i, (word, start, end) in enumerate(words):
            if i > 0:
                prev_word = words[i - 1][0]
                
                # Check if word is a base verb
                if word in self.VERB_FORMS and word not in skip_verbs:
                    should_conjugate = False
                    subject = None
                    
                    # Check if previous word is third person singular subject
                    if prev_word in third_person_singular:
                        should_conjugate = True
                        subject = prev_word
                    # Check if previous word is conjunction and sentence has 3rd person subject
                    elif prev_word in conjunctions and sentence_subject:
                        should_conjugate = True  
                        subject = sentence_subject
                    # Check if word before conjunction is a verb (parallel structure)
                    elif prev_word in conjunctions:
                        # Look back to see if we're in a "she verbs and verb" pattern
                        for j in range(i - 2, -1, -1):
                            check_word = words[j][0]
                            if check_word in third_person_singular:
                                should_conjugate = True
                                subject = check_word
                            elif check_word in skip_verbs:
                                break
                    
                    if should_conjugate:
                        # Skip 'say' if followed by object pronoun (handled by _check_say_to_tell)
                        if word == 'say':
                            idx = i + 1
                            if idx < len(words):
                                next_word = words[idx][0]
                                # Check if next word is object pronoun
                                if next_word in {'me', 'us', 'him', 'them', 'her'}:
                                    continue

                        forms = self.VERB_FORMS[word]
                        third_person_form = forms[2]  # present 3rd person singular
                        
                        # Only suggest if it's different from current word
                        if third_person_form != word:
                            errors.append({
                                'type': 'grammar',
                                'position': {'start': start, 'end': end},
                                'original': text[start:end],
                                'suggestion': third_person_form,
                                'explanation': f'Use "{third_person_form}" with third-person singular subject.',
                                'sentenceIndex': 0,
                            })
        
        return errors
    
    def _check_plural_nouns(self, text: str, words: List[Tuple[str, int, int]]) -> List[Dict]:
        """Check for nouns that should be plural after certain patterns."""
        errors = []
        
        # Singular nouns that often should be plural in context
        countable_nouns = {
            'book': 'books', 'movie': 'movies', 'song': 'songs', 'game': 'games',
            'car': 'cars', 'house': 'houses', 'dog': 'dogs', 'cat': 'cats',
            'friend': 'friends', 'student': 'students', 'teacher': 'teachers',
            'child': 'children', 'person': 'people', 'man': 'men', 'woman': 'women',
            'day': 'days', 'year': 'years', 'hour': 'hours', 'minute': 'minutes',
            'thing': 'things', 'place': 'places', 'idea': 'ideas', 'problem': 'problems',
            'question': 'questions', 'answer': 'answers', 'story': 'stories',
            'picture': 'pictures', 'photo': 'photos', 'video': 'videos',
            'computer': 'computers', 'phone': 'phones', 'word': 'words',
            'vegetable': 'vegetables', 'fruit': 'fruits', 'animal': 'animals',
            'flower': 'flowers', 'tree': 'trees', 'city': 'cities', 'country': 'countries',
        }
        
        # Patterns that suggest plural is needed
        plural_triggers = {'reading', 'watching', 'playing', 'buying', 'selling',
                           'making', 'taking', 'writing', 'many', 'several', 'some',
                           'few', 'all', 'these', 'those', 'various', 'different',
                           'multiple', 'numerous'}
        
        for i, (word, start, end) in enumerate(words):
            if word in countable_nouns:
                plural = countable_nouns[word]
                
                # Check previous word for plural triggers
                prev_word = words[i - 1][0] if i > 0 else ""
                prev_prev_word = words[i - 2][0] if i > 1 else ""
                
                # Check if previous word is a gerund (ends in -ing) or a known plural trigger
                is_gerund = prev_word.endswith('ing') and len(prev_word) > 4
                
                # Also check for pattern like "prefers watch movie" -> "prefers watching movies"
                # where the verb before noun will become gerund
                is_verb_after_gerund_verb = (prev_word in self.VERB_FORMS and 
                                             prev_prev_word in {'prefer', 'prefers', 'preferred', 
                                                                'enjoy', 'enjoys', 'enjoyed',
                                                                'like', 'likes', 'liked',
                                                                'love', 'loves', 'loved',
                                                                'hate', 'hates', 'hated'})
                
                if prev_word in plural_triggers or is_gerund or is_verb_after_gerund_verb:
                    errors.append({
                        'type': 'grammar',
                        'position': {'start': start, 'end': end},
                        'original': text[start:end],
                        'suggestion': plural,
                        'explanation': f'Use plural "{plural}" in this context.',
                        'sentenceIndex': 0,
                    })
        
        return errors
    
    def _check_past_tense_indicator_after_verb(self, text: str, words: List[Tuple[str, int, int]]) -> List[Dict]:
        """
        Check for past-tense indicators after verbs and convert to past tense.
        Example: "they win the competition last week" -> "they won the competition last week"
        """
        errors = []
        
        # Past tense indicator phrases (multi-word and single-word)
        past_indicators_multi = [
            'last week', 'last month', 'last year', 'last night', 'last time',
            'last summer', 'last winter', 'last spring', 'last fall',
            'the other day', 'a few days ago', 'a week ago', 'a month ago',
            'a year ago', 'years ago', 'months ago', 'weeks ago', 'days ago',
            'hours ago', 'minutes ago', 'in the past', 'back then',
            'when i was', 'when we were', 'when they were',
        ]
        
        past_indicators_single = ['ago', 'yesterday']
        
        text_lower = text.lower()
        
        # Check for multi-word indicators
        for indicator in past_indicators_multi:
            if indicator in text_lower:
                indicator_pos = text_lower.find(indicator)
                
                # Look for verbs BEFORE this indicator
                for i, (word, start, end) in enumerate(words):
                    # Only check words before the indicator
                    if start >= indicator_pos:
                        break
                    
                    # Check if this word is a base form verb that should be past
                    if word in self.VERB_FORMS:
                        forms = self.VERB_FORMS[word]
                        past_form = forms[0]  # past tense
                        
                        # Only flag if current word is NOT already past tense
                        if word != past_form and word == word:  # base form
                            # Check that we're not already past tense
                            # and that the word comes after a subject (not at start)
                            if i > 0:
                                errors.append({
                                    'type': 'grammar',
                                    'position': {'start': start, 'end': end},
                                    'original': text[start:end],
                                    'suggestion': past_form,
                                    'explanation': f'Use past tense "{past_form}" because of "{indicator}".',
                                    'sentenceIndex': 0,
                                })
        
        # Check for single-word indicators like "yesterday" at end or "ago"
        for i, (word, start, end) in enumerate(words):
            if word in past_indicators_single:
                # Look backwards for verbs in base form
                for j in range(i - 1, -1, -1):
                    prev_word, prev_start, prev_end = words[j]
                    
                    if prev_word in self.VERB_FORMS:
                        forms = self.VERB_FORMS[prev_word]
                        past_form = forms[0]
                        
                        if prev_word != past_form:
                            errors.append({
                                'type': 'grammar',
                                'position': {'start': prev_start, 'end': prev_end},
                                'original': text[prev_start:prev_end],
                                'suggestion': past_form,
                                'explanation': f'Use past tense "{past_form}" because of "{word}".',
                                'sentenceIndex': 0,
                            })
                    # Only check up to 5 words back
                    if i - j > 5:
                        break
        
        return errors
    
    def _check_incorrect_regularized_past(self, text: str, words: List[Tuple[str, int, int]]) -> List[Dict]:
        """
        Check for incorrect regularized past tense of irregular verbs.
        Example: "buyed" -> "bought", "goed" -> "went", "taked" -> "took"
        
        Common mistake for ESL learners who apply regular -ed rule to irregular verbs.
        """
        errors = []
        
        # Build a mapping of incorrect forms to correct forms
        # Pattern: base + "ed" or base + "d" (for verbs ending in e)
        incorrect_to_correct = {}
        
        for base, forms in self.VERB_FORMS.items():
            past_form = forms[0]
            
            # Skip if the verb is regular (past already ends in -ed)
            if past_form == base + 'ed' or past_form == base + 'd':
                continue
            
            # Generate incorrect forms
            # buyed, goed, taked, comed, etc.
            if base.endswith('e'):
                incorrect = base + 'd'  # take -> taked
            else:
                incorrect = base + 'ed'  # buy -> buyed, go -> goed
            
            # Also handle doubling consonant (runed instead of ran)
            if len(base) > 2 and base[-1] in 'bdgmnprt' and base[-2] in 'aeiou':
                incorrect_doubled = base + base[-1] + 'ed'  # run -> runned
                incorrect_to_correct[incorrect_doubled] = past_form
            
            incorrect_to_correct[incorrect] = past_form
        
        # Check each word
        for word, start, end in words:
            if word in incorrect_to_correct:
                correct = incorrect_to_correct[word]
                
                errors.append({
                    'type': 'grammar',
                    'position': {'start': start, 'end': end},
                    'original': text[start:end],
                    'suggestion': correct,
                    'explanation': f'Irregular verb: use "{correct}" instead of "{word}".',
                    'sentenceIndex': 0,
                })
        
        return errors


# Global instance
_grammar_rules_checker = None


def get_grammar_rules_checker() -> GrammarRulesChecker:
    """Get the global grammar rules checker instance."""
    global _grammar_rules_checker
    if _grammar_rules_checker is None:
        _grammar_rules_checker = GrammarRulesChecker()
    return _grammar_rules_checker

