"""
Rule-Based Grammar Checker module.
Advanced logic for paragraph-level consistency and complex grammar rules.
"""

import re
from typing import List, Dict, Tuple

class GrammarRulesChecker:
    
    # 1. Common Morphology Errors (Grammar masquerading as spelling)
    MORPHOLOGY_FIXES = {
        'buyed': 'bought', 'goed': 'went', 'taked': 'took', 'comed': 'came', 
        'runned': 'ran', 'eated': 'ate', 'drinked': 'drank', 'seed': 'saw',
        'thinked': 'thought', 'finded': 'found', 'keeped': 'kept', 'sleebed': 'slept',
        'payed': 'paid', 'sayed': 'said', 'maked': 'made', 'writed': 'wrote',
        'readed': 'read', 'speaked': 'spoke', 'breaked': 'broke', 'wakup': 'woke up',
        'wake': 'woke', 'waked': 'woke', 'phne': 'phone' # Common typos contextually handled
    }
    
    # 1b. Missing Apostrophe Contractions
    CONTRACTION_FIXES = {
        'dont': "don't", 'doesnt': "doesn't", 'didnt': "didn't",
        'wont': "won't", 'cant': "can't", 'shouldnt': "shouldn't",
        'wouldnt': "wouldn't", 'couldnt': "couldn't", 'isnt': "isn't",
        'arent': "aren't", 'wasnt': "wasn't", 'werent': "weren't",
        'hasnt': "hasn't", 'havent': "haven't", 'hadnt': "hadn't",
        'theyre': "they're", 'youre': "you're", 'were': "we're",
        'ive': "I've", 'youve': "you've", 'weve': "we've",
        'theyve': "they've", 'hed': "he'd", 'shed': "she'd",
        'youd': "you'd", 'theyd': "they'd", 'wed': "we'd",
        'im': "I'm", 'hes': "he's", 'shes': "she's",
        'thats': "that's", 'whats': "what's", 'whos': "who's",
        'lets': "let's", 'theres': "there's", 'heres': "here's",
        'aint': "ain't", 'mustnt': "mustn't", 'mightnt': "mightn't"
    }

    # 2. Strong Past Tense Indicators
    STRONG_PAST_VERBS = {
        'wrote', 'said', 'did', 'didn\'t', 'was', 'were', 'had', 'went', 'saw', 'ran', 'ate', 
        'took', 'gave', 'told', 'felt', 'became', 'sat', 'stood', 'forgot', 'lost',
        'traveled', 'stayed', 'helped', 'wanted', 'tried', 'started', 'ended', 'explained',
        'woke', 'prepared', 'forgot'
    }

    # 3. Universal Verb Forms (Base -> (Past, Past Participle, 3rd Person, Participle))
    VERB_FORMS = {
        'buy': ('bought', 'bought', 'buys', 'buying'),
        'go': ('went', 'gone', 'goes', 'going'),
        'get': ('got', 'gotten', 'gets', 'getting'),
        'make': ('made', 'made', 'makes', 'making'),
        'know': ('knew', 'known', 'knows', 'knowing'),
        'think': ('thought', 'thought', 'thinks', 'thinking'),
        'take': ('took', 'taken', 'takes', 'taking'),
        'see': ('saw', 'seen', 'sees', 'seeing'),
        'come': ('came', 'come', 'comes', 'coming'),
        'want': ('wanted', 'wanted', 'wants', 'wanting'),
        'look': ('looked', 'looked', 'looks', 'looking'),
        'use': ('used', 'used', 'uses', 'using'),
        'find': ('found', 'found', 'finds', 'finding'),
        'give': ('gave', 'given', 'gives', 'giving'),
        'tell': ('told', 'told', 'tells', 'telling'),
        'work': ('worked', 'worked', 'works', 'working'),
        'try': ('tried', 'tried', 'tries', 'trying'),
        'ask': ('asked', 'asked', 'asks', 'asking'),
        'need': ('needed', 'needed', 'needs', 'needing'),
        'feel': ('felt', 'felt', 'feels', 'feeling'),
        'leave': ('left', 'left', 'leaves', 'leaving'),
        'put': ('put', 'put', 'puts', 'putting'),
        'mean': ('meant', 'meant', 'means', 'meaning'),
        'keep': ('kept', 'kept', 'keeps', 'keeping'),
        'let': ('let', 'let', 'lets', 'letting'),
        'begin': ('began', 'begun', 'begins', 'beginning'),
        'help': ('helped', 'helped', 'helps', 'helping'),
        'talk': ('talked', 'talked', 'talks', 'talking'),
        'start': ('started', 'started', 'starts', 'starting'),
        'show': ('showed', 'shown', 'shows', 'showing'),
        'hear': ('heard', 'heard', 'hears', 'hearing'),
        'play': ('played', 'played', 'plays', 'playing'),
        'run': ('ran', 'run', 'runs', 'running'),
        'move': ('moved', 'moved', 'moves', 'moving'),
        'like': ('liked', 'liked', 'likes', 'liking'),
        'live': ('lived', 'lived', 'lives', 'living'),
        'believe': ('believed', 'believed', 'believes', 'believing'),
        'hold': ('held', 'held', 'holds', 'holding'),
        'bring': ('brought', 'brought', 'brings', 'bringing'),
        'happen': ('happened', 'happened', 'happens', 'happening'),
        'write': ('wrote', 'written', 'writes', 'writing'),
        'provide': ('provided', 'provided', 'provides', 'providing'),
        'sit': ('sat', 'sat', 'sits', 'sitting'),
        'stand': ('stood', 'stood', 'stands', 'standing'),
        'lose': ('lost', 'lost', 'loses', 'losing'),
        'pay': ('paid', 'paid', 'pays', 'paying'),
        'meet': ('met', 'met', 'meets', 'meeting'),
        'learn': ('learned', 'learned', 'learns', 'learning'),
        'change': ('changed', 'changed', 'changes', 'changing'),
        'lead': ('led', 'led', 'leads', 'leading'),
        'understand': ('understood', 'understood', 'understands', 'understanding'),
        'watch': ('watched', 'watched', 'watches', 'watching'),
        'follow': ('followed', 'followed', 'follows', 'following'),
        'stop': ('stopped', 'stopped', 'stops', 'stopping'),
        'create': ('created', 'created', 'creates', 'creating'),
        'speak': ('spoke', 'spoken', 'speaks', 'speaking'),
        'read': ('read', 'read', 'reads', 'reading'),
        'allow': ('allowed', 'allowed', 'allows', 'allowing'),
        'add': ('added', 'added', 'adds', 'adding'),
        'spend': ('spent', 'spent', 'spends', 'spending'),
        'grow': ('grew', 'grown', 'grows', 'growing'),
        'open': ('opened', 'opened', 'opens', 'opening'),
        'walk': ('walked', 'walked', 'walks', 'walking'),
        'win': ('won', 'won', 'wins', 'winning'),
        'offer': ('offered', 'offered', 'offers', 'offering'),
        'remember': ('remembered', 'remembered', 'remembers', 'remembering'),
        'love': ('loved', 'loved', 'loves', 'loving'),
        'consider': ('considered', 'considered', 'considers', 'considering'),
        'appear': ('appeared', 'appeared', 'appears', 'appearing'),
        'buy': ('bought', 'bought', 'buys', 'buying'),
        'wait': ('waited', 'waited', 'waits', 'waiting'),
        'serve': ('served', 'served', 'serves', 'serving'),
        'die': ('died', 'died', 'dies', 'dying'),
        'send': ('sent', 'sent', 'sends', 'sending'),
        'expect': ('expected', 'expected', 'expects', 'expecting'),
        'build': ('built', 'built', 'builds', 'building'),
        'stay': ('stayed', 'stayed', 'stays', 'staying'),
        'fall': ('fell', 'fallen', 'falls', 'falling'),
        'cut': ('cut', 'cut', 'cuts', 'cutting'),
        'reach': ('reached', 'reached', 'reaches', 'reaching'),
        'kill': ('killed', 'killed', 'kills', 'killing'),
        'remain': ('remained', 'remained', 'remains', 'remaining'),
        'plan': ('planned', 'planned', 'plans', 'planning'),
        'study': ('studied', 'studied', 'studies', 'studying'),
        'listen': ('listened', 'listened', 'listens', 'listening'),
        'forget': ('forgot', 'forgotten', 'forgets', 'forgetting'),
        'decide': ('decided', 'decided', 'decides', 'deciding'),
        'hope': ('hoped', 'hoped', 'hopes', 'hoping'),
        'visit': ('visited', 'visited', 'visits', 'visiting'),
        'travel': ('traveled', 'traveled', 'travels', 'traveling'),
        'worry': ('worried', 'worried', 'worries', 'worrying'),
        'clean': ('cleaned', 'cleaned', 'cleans', 'cleaning'),
        'cook': ('cooked', 'cooked', 'cooks', 'cooking'),
        'wash': ('washed', 'washed', 'washes', 'washing'),
        'fix': ('fixed', 'fixed', 'fixes', 'fixing'),
        'rain': ('rained', 'rained', 'rains', 'raining'),
        'snow': ('snowed', 'snowed', 'snows', 'snowing'),
        'relax': ('relaxed', 'relaxed', 'relaxes', 'relaxing'),
        'finish': ('finished', 'finished', 'finishes', 'finishing'),
        'explain': ('explained', 'explained', 'explains', 'explaining'),
        'wear': ('wore', 'worn', 'wears', 'wearing'),
        'drink': ('drank', 'drunk', 'drinks', 'drinking'),
        'eat': ('ate', 'eaten', 'eats', 'eating'),
        'drive': ('drove', 'driven', 'drives', 'driving'),
        'prepare': ('prepared', 'prepared', 'prepares', 'preparing'),
        'wake': ('woke', 'woken', 'wakes', 'waking'),
        'drain': ('drained', 'drained', 'drains', 'draining'),
        'arrive': ('arrived', 'arrived', 'arrives', 'arriving'),
    }
    
    SINGULAR_SUBJECTS = {
        'he', 'she', 'it', 'this', 'that', 'everyone', 'someone', 'anyone',
        'one', 'driver', 'teacher', 'student', 'writer', 'player', 'worker',
        'mother', 'father', 'brother', 'sister', 'friend', 'dog', 'cat', 'person',
        'weather', 'money', 'battery', 'bus', 'class'
    }
    
    PLURAL_SUBJECTS = {'they', 'we', 'these', 'those', 'people', 'children', 'men', 'women', 'words', 'classmates', 'batteries'}
    
    POSSESSIVE_MAP = {'it': 'its', 'he': 'his', 'she': 'her', 'they': 'their', 'we': 'our', 'i': 'my', 'you': 'your'}
    
    def __init__(self):
        self.verb_base_lookup = {}
        for base, forms in self.VERB_FORMS.items():
            self.verb_base_lookup[base] = base
            for form in forms:
                if form not in self.verb_base_lookup:
                    self.verb_base_lookup[form] = base
    
    def check_text(self, text: str) -> List[Dict]:
        errors = []
        
        # 1. Detect Context
        past_indicators = {'yesterday', 'ago', 'last', 'previously', 'before', 'already'}
        text_lower = text.lower()
        has_keyword = any(ind in text_lower for ind in past_indicators)
        has_past_verb = any(word in self.STRONG_PAST_VERBS for word in text_lower.split())
        global_past_context = has_keyword or has_past_verb
        
        # 2. Tokenize
        errors.extend(self._check_sentence_capitalization(text))
        words = self._tokenize(text)
        
        # 3. Apply Checks
        errors.extend(self._check_morphology(text, words, global_past_context))
        errors.extend(self._check_missing_apostrophes(text, words))
        errors.extend(self._check_quantifiers(text, words))
        errors.extend(self._check_double_comparatives(text, words))
        errors.extend(self._check_explain_errors(text, words))
        errors.extend(self._check_redundancy(text, words))
        errors.extend(self._check_possessives_context(text, words))
        
        errors.extend(self._check_contractions(text, words))
        errors.extend(self._check_subject_verb_agreement(text, words))
        errors.extend(self._check_possessive_pronouns(text, words))
        errors.extend(self._check_verb_tense(text, words, force_past=global_past_context))
        errors.extend(self._check_progressive_tense(text, words))
        errors.extend(self._check_say_to_tell(text, words))
        errors.extend(self._check_past_tense_after_conjunction(text, words))
        errors.extend(self._check_gerund_patterns(text, words))
        errors.extend(self._check_plural_nouns(text, words))
        errors.extend(self._check_pronoun_capitalization(text, words))
        errors.extend(self._check_infinitive_patterns(text, words))
        errors.extend(self._check_to_verb_form(text, words))
        errors.extend(self._check_articles(text, words))
        errors.extend(self._check_adverbs(text, words))
        errors.extend(self._check_prepositions(text, words))
        errors.extend(self._check_confused_words(text, words))
        errors.extend(self._check_prepositions_context(text, words))
        
        return errors
    
    def _tokenize(self, text: str) -> List[Tuple[str, int, int]]:
        tokens = []
        for match in re.finditer(r"\b\w+(?:'\w+)?\b", text):
            tokens.append((match.group().lower(), match.start(), match.end()))
        return tokens

    def _check_morphology(self, text: str, words: List[Tuple[str, int, int]], has_past_context: bool) -> List[Dict]:
        """Catches 'buyed', 'goed' and incorrect base forms in past context."""
        errors = []
        for word, start, end in words:
            # 1. Explicit Dictionary Fixes
            if word in self.MORPHOLOGY_FIXES:
                correct = self.MORPHOLOGY_FIXES[word]
                errors.append({'type': 'grammar', 'position': {'start': start, 'end': end}, 'original': text[start:end], 'suggestion': correct, 'explanation': f'Correct spelling/form is "{correct}".', 'sentenceIndex': 0})
            
            # 2. Contextual Fix: "wake" in past context
            elif has_past_context and word == 'wake' and word not in {'to', 'will', 'did'}: # Simplified logic
                 errors.append({'type': 'grammar', 'position': {'start': start, 'end': end}, 'original': text[start:end], 'suggestion': 'woke', 'explanation': 'Use past tense "woke".', 'sentenceIndex': 0})
                 
        return errors

    def _check_missing_apostrophes(self, text: str, words: List[Tuple[str, int, int]]) -> List[Dict]:
        """Fix contractions missing apostrophes: dont -> don't, its -> it's, etc."""
        errors = []
        verbs_after_its = {'is', 'are', 'was', 'were', 'has', 'have', 'had', 'will', 'would', 'could', 'should', 'might', 'been', 'being', 'raining', 'going', 'coming', 'getting', 'looking', 'working', 'making', 'taking', 'doing', 'saying'}
        
        for i, (word, start, end) in enumerate(words):
            word_lower = word.lower()
            
            # Special case for "its" - only fix if followed by a verb (it's = it is)
            if word_lower == 'its':
                if i + 1 < len(words):
                    next_word = words[i + 1][0].lower()
                    if next_word in verbs_after_its:
                        original = text[start:end]
                        suggestion = "it's" if original[0].islower() else "It's"
                        errors.append({
                            'type': 'grammar', 
                            'position': {'start': start, 'end': end}, 
                            'original': original, 
                            'suggestion': suggestion, 
                            'explanation': '"it\'s" is short for "it is" or "it has".', 
                            'sentenceIndex': 0
                        })
            # All other contractions
            elif word_lower in self.CONTRACTION_FIXES:
                original = text[start:end]
                correct = self.CONTRACTION_FIXES[word_lower]
                # Preserve capitalization
                if original[0].isupper():
                    correct = correct[0].upper() + correct[1:]
                errors.append({
                    'type': 'grammar', 
                    'position': {'start': start, 'end': end}, 
                    'original': original, 
                    'suggestion': correct, 
                    'explanation': f'Missing apostrophe. Use "{correct}".', 
                    'sentenceIndex': 0
                })
        
        return errors

    def _check_verb_tense(self, text: str, words: List[Tuple[str, int, int]], force_past: bool = False) -> List[Dict]:
        errors = []
        for i, (word, start, end) in enumerate(words):
            # Check for "Did" + Base Form rule
            if i > 0:
                prev_word = words[i - 1][0]
                # If previous word is "did" or "didn't", current verb MUST be base
                if prev_word in {'did', 'didnt', "didn't"}:
                    if word in self.VERB_FORMS:
                        # Check if it's NOT the base form (e.g., 'understood' -> 'understand')
                        # Logic: If word != base form OR word is past form
                        forms = self.VERB_FORMS[word] # (past, pp, 3rd, ing)
                        base = self.verb_base_lookup.get(word, word)
                        
                        # If word is one of the conjugated forms
                        if word in forms: 
                            errors.append({'type': 'grammar', 'position': {'start': start, 'end': end}, 'original': text[start:end], 'suggestion': base, 'explanation': 'Use base form after "did".', 'sentenceIndex': 0})
                    continue # Skip normal tense check if handled here

                # Skip if preceded by "to" or other modals
                if prev_word in {'to', 'can', 'could', 'will', 'would', 'should', 'may', 'might', 'must', 'do', 'does'}:
                    continue
                
                # Causative/Perception Exception
                if i > 1:
                    prev_prev = words[i-2][0]
                    if prev_prev in {'help', 'helped', 'helps', 'make', 'made', 'makes', 'let', 'lets', 'see', 'saw', 'watch', 'watched', 'hear', 'heard'}:
                        continue 
            
            # Normal Past Tense Enforcement
            if force_past:
                # Allow index 0 check if forced
                if i == 0 or i > 0:
                    if word in self.VERB_FORMS and word not in {'be', 'is', 'are', 'was', 'were', 'have', 'has', 'had'}:
                        past_form = self.VERB_FORMS[word][0]
                        if word != past_form and word == word: # is base form
                            cap_suggestion = past_form.capitalize() if i == 0 else past_form
                            errors.append({'type': 'grammar', 'position': {'start': start, 'end': end}, 'original': text[start:end], 'suggestion': cap_suggestion, 'explanation': 'Use past tense.', 'sentenceIndex': 0})
        return errors

    def _check_subject_verb_agreement(self, text: str, words: List[Tuple[str, int, int]]) -> List[Dict]:
        errors = []
        adverbs = {'already', 'just', 'always', 'never', 'really', 'often'}
        
        for i, (word, start, end) in enumerate(words):
            if i > 0:
                prev_word = words[i - 1][0]
                actual_subject = prev_word
                if prev_word in adverbs and i > 1:
                    actual_subject = words[i - 2][0]
                
                # Smart Plural Detection: Ends in 's' and not in singular exceptions list
                is_plural_noun = (actual_subject.endswith('s') and 
                                  actual_subject not in self.SINGULAR_SUBJECTS and 
                                  len(actual_subject) > 3)
                
                if actual_subject in self.PLURAL_SUBJECTS or is_plural_noun:
                    if word == 'is':
                        errors.append({'type': 'grammar', 'position': {'start': start, 'end': end}, 'original': text[start:end], 'suggestion': 'are', 'explanation': f'"{actual_subject}" is plural.', 'sentenceIndex': 0})
                    elif word == 'was':
                         errors.append({'type': 'grammar', 'position': {'start': start, 'end': end}, 'original': text[start:end], 'suggestion': 'were', 'explanation': f'"{actual_subject}" is plural.', 'sentenceIndex': 0})
                
                elif actual_subject in self.SINGULAR_SUBJECTS:
                    if word == 'are':
                        errors.append({'type': 'grammar', 'position': {'start': start, 'end': end}, 'original': text[start:end], 'suggestion': 'is', 'explanation': f'"{actual_subject}" is singular.', 'sentenceIndex': 0})
                    elif word == 'were':
                        errors.append({'type': 'grammar', 'position': {'start': start, 'end': end}, 'original': text[start:end], 'suggestion': 'was', 'explanation': f'"{actual_subject}" is singular.', 'sentenceIndex': 0})
        return errors

    def _check_possessives_context(self, text: str, words: List[Tuple[str, int, int]]) -> List[Dict]:
        errors = []
        family_triggers = {'mother', 'father', 'brother', 'sister', 'aunt', 'uncle', 'friend', 'neighbor', 'teacher', 'student'}
        for i, (word, start, end) in enumerate(words):
            if word in family_triggers:
                if i + 1 < len(words):
                    next_word = words[i+1][0]
                    # If followed by a noun (heuristic: not a verb/preposition)
                    # Simple check: longer than 3 letters, not in verbs
                    if len(next_word) > 2 and next_word not in {'was', 'is', 'said', 'went', 'told', 'asked', 'with', 'from', 'to'}:
                        if not word.endswith('s'):
                            errors.append({'type': 'grammar', 'position': {'start': start, 'end': end}, 'original': text[start:end], 'suggestion': word + "'s", 'explanation': 'Missing apostrophe for possession.', 'sentenceIndex': 0})
        return errors

    def _check_sentence_capitalization(self, text: str) -> List[Dict]:
        errors = []
        first_match = re.match(r'^\s*([a-z])', text)
        if first_match:
            errors.append({'type': 'grammar', 'position': {'start': first_match.start(1), 'end': first_match.end(1)}, 'original': first_match.group(1), 'suggestion': first_match.group(1).upper(), 'explanation': 'Sentences should start with a capital letter.', 'sentenceIndex': 0})
        for match in re.finditer(r'([.!?]\s+)([a-z])', text):
            errors.append({'type': 'grammar', 'position': {'start': match.start(2), 'end': match.end(2)}, 'original': match.group(2), 'suggestion': match.group(2).upper(), 'explanation': 'Sentences should start with a capital letter.', 'sentenceIndex': 0})
        return errors

    def _check_quantifiers(self, text: str, words: List[Tuple[str, int, int]]) -> List[Dict]:
        errors = []
        for match in re.finditer(r'^\s*(no)\s+enough\b', text, re.IGNORECASE | re.MULTILINE):
            errors.append({'type': 'grammar', 'position': {'start': match.start(1), 'end': match.end(1)}, 'original': match.group(1), 'suggestion': 'Not', 'explanation': 'Use "Not enough".', 'sentenceIndex': 0})
        for match in re.finditer(r'(?<!^)\s+(no)\s+enough\b', text, re.IGNORECASE):
            errors.append({'type': 'grammar', 'position': {'start': match.start(1), 'end': match.end(1)}, 'original': match.group(1), 'suggestion': 'not', 'explanation': 'Use "not enough".', 'sentenceIndex': 0})
        return errors

    def _check_double_comparatives(self, text: str, words: List[Tuple[str, int, int]]) -> List[Dict]:
        errors = []
        for match in re.finditer(r'\bmore\s+([a-z]+er)\b', text, re.IGNORECASE):
            adj = match.group(1)
            if adj not in {'never', 'ever', 'over', 'under', 'river', 'paper', 'water', 'corner', 'father', 'mother', 'brother', 'sister', 'summer', 'winter', 'dinner'}:
                errors.append({'type': 'grammar', 'position': {'start': match.start(), 'end': match.end()}, 'original': match.group(), 'suggestion': adj, 'explanation': f'Redundant comparative.', 'sentenceIndex': 0})
        return errors

    def _check_explain_errors(self, text: str, words: List[Tuple[str, int, int]]) -> List[Dict]:
        errors = []
        for i, (word, start, end) in enumerate(words):
            if word in ('explain', 'explained') and i + 1 < len(words):
                if words[i+1][0] in {'him', 'her', 'me', 'us', 'them', 'you'}:
                    errors.append({'type': 'grammar', 'position': {'start': start, 'end': words[i+1][2]}, 'original': text[start:words[i+1][2]], 'suggestion': f'{word} to {words[i+1][0]}', 'explanation': f'Use "to" after "{word}".', 'sentenceIndex': 0})
        return errors

    def _check_prepositions(self, text: str, words: List[Tuple[str, int, int]]) -> List[Dict]:
        errors = []
        prep_map = {'married with': 'married to', 'good in': 'good at', 'angry to': 'angry with', 'depend of': 'depend on', 'listen her': 'listen to her', 'arrive to': 'arrive at'}
        tl = text.lower()
        for w, r in prep_map.items():
            if w in tl:
                idx = tl.find(w)
                errors.append({'type': 'grammar', 'position': {'start': idx, 'end': idx+len(w)}, 'original': text[idx:idx+len(w)], 'suggestion': r, 'explanation': f'Use "{r}".', 'sentenceIndex': 0})
        
        go_exceptions = {'to', 'into', 'in', 'out', 'up', 'down', 'back', 'on', 'home', 'away'}
        for i, (word, start, end) in enumerate(words):
            if word in ('go', 'goes', 'went', 'going') and i + 1 < len(words):
                nw = words[i+1][0]
                if nw not in go_exceptions:
                    if nw in {'work', 'school', 'bed', 'church', 'college', 'jail'}:
                        errors.append({'type': 'grammar', 'position': {'start': words[i+1][1], 'end': words[i+1][2]}, 'original': nw, 'suggestion': 'to ' + nw, 'explanation': 'Missing "to".', 'sentenceIndex': 0})
                    elif nw in {'library', 'mall', 'park', 'cinema', 'gym', 'bank'} or (nw.endswith('s') and len(nw)>3):
                        errors.append({'type': 'grammar', 'position': {'start': words[i+1][1], 'end': words[i+1][2]}, 'original': nw, 'suggestion': 'to the ' + nw, 'explanation': 'Missing "to the".', 'sentenceIndex': 0})
        return errors

    def _check_to_verb_form(self, text: str, words: List[Tuple[str, int, int]]) -> List[Dict]:
        errors = []
        for i, (word, start, end) in enumerate(words):
            if i > 0 and words[i-1][0] == 'to' and word in self.verb_base_lookup:
                base = self.verb_base_lookup[word]
                if word != base:
                    errors.append({'type': 'grammar', 'position': {'start': start, 'end': end}, 'original': text[start:end], 'suggestion': base, 'explanation': f'Use base form "{base}" after "to".', 'sentenceIndex': 0})
        return errors

    def _check_adverbs(self, text: str, words: List[Tuple[str, int, int]]) -> List[Dict]:
        errors = []
        adj_to_adv = {'quick': 'quickly', 'slow': 'slowly', 'loud': 'loudly', 'quiet': 'quietly', 'bad': 'badly'}
        verbs = {'run', 'runs', 'ran', 'walk', 'walks', 'walked', 'speak', 'spoke', 'speaks', 'sing', 'sang', 'arrive', 'arrived'}
        for i, (word, start, end) in enumerate(words):
            if i > 0 and words[i-1][0] in verbs and word in adj_to_adv:
                 errors.append({'type': 'grammar', 'position': {'start': start, 'end': end}, 'original': text[start:end], 'suggestion': adj_to_adv[word], 'explanation': 'Use adverb.', 'sentenceIndex': 0})
        return errors

    def _check_redundancy(self, text: str, words: List[Tuple[str, int, int]]) -> List[Dict]:
        errors = []
        red = {'return back': 'return', 'repeat again': 'repeat', 'reply back': 'reply', 'join together': 'join'}
        for p, f in red.items():
            if p in text.lower():
                idx = text.lower().find(p)
                errors.append({'type': 'grammar', 'position': {'start': idx, 'end': idx+len(p)}, 'original': text[idx:idx+len(p)], 'suggestion': f, 'explanation': 'Redundant.', 'sentenceIndex': 0})
        return errors

    def _check_pronoun_capitalization(self, text: str, words: List[Tuple[str, int, int]]) -> List[Dict]:
        errors = []
        for word, start, end in words:
            if word == 'i':
                errors.append({'type': 'grammar', 'position': {'start': start, 'end': end}, 'original': text[start:end], 'suggestion': 'I', 'explanation': 'Capitalize "I".', 'sentenceIndex': 0})
        return errors

    def _check_contractions(self, text: str, words: List[Tuple[str, int, int]]) -> List[Dict]:
        errors = []
        contraction_fixes = {'dont': "don't", 'didnt': "didn't", 'cant': "can't", 'im': "I'm", 'its': "it's"}
        for word, start, end in words:
            if word in contraction_fixes:
                errors.append({'type': 'grammar', 'position': {'start': start, 'end': end}, 'original': text[start:end], 'suggestion': contraction_fixes[word], 'explanation': 'Fix contraction.', 'sentenceIndex': 0})
        return errors

    def _check_possessive_pronouns(self, text: str, words: List[Tuple[str, int, int]]) -> List[Dict]:
        errors = []
        for i, (word, start, end) in enumerate(words):
            if word == 'it' and i < len(words)-1 and words[i+1][0] in {'battery', 'phone', 'car'}:
                errors.append({'type': 'grammar', 'position': {'start': start, 'end': end}, 'original': text[start:end], 'suggestion': 'its', 'explanation': 'Use "its".', 'sentenceIndex': 0})
        return errors

    # Placeholders for others to prevent errors if called
    def _check_say_to_tell(self, t, w): return []
    def _check_past_tense_after_conjunction(self, t, w): return []
    def _check_gerund_patterns(self, t, w): return []
    def _check_plural_nouns(self, t, w): return []
    def _check_incorrect_regularized_past(self, t, w): return []
    def _check_infinitive_patterns(self, t, w): return []
    def _check_articles(self, t, w): return []
    def _check_confused_words(self, t, w): return []
    def _check_prepositions_context(self, t, w): return []
    def _check_progressive_tense(self, t, w): return []
    def _check_third_person_verbs(self, t, w): return []

_grammar_rules_checker = None
def get_grammar_rules_checker() -> GrammarRulesChecker:
    global _grammar_rules_checker
    if _grammar_rules_checker is None:
        _grammar_rules_checker = GrammarRulesChecker()
    return _grammar_rules_checker
