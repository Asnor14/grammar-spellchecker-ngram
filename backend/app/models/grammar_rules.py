"""
Rule-Based Grammar Checker module.
Uses pattern recognition and universal dictionaries for generalized grammar checking.
"""

import re
from typing import List, Dict, Tuple

class GrammarRulesChecker:
    
    # 1. Strong Past Tense Indicators (Triggers Global Past Context)
    STRONG_PAST_VERBS = {
        'wrote', 'said', 'did', 'was', 'were', 'had', 'went', 'saw', 'ran', 'ate', 
        'took', 'gave', 'told', 'felt', 'became', 'sat', 'stood', 'forgot', 'lost',
        'traveled', 'stayed', 'helped', 'wanted', 'tried', 'started', 'ended', 'explained'
    }

    # 2. Universal Verb Forms Dictionary
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
    }
    
    # 3. Universal Singular Subjects
    SINGULAR_SUBJECTS = {
        'he', 'she', 'it', 'this', 'that', 'everyone', 'someone', 'anyone',
        'no one', 'nobody', 'everybody', 'somebody', 'anybody', 'each',
        'one', 'driver', 'teacher', 'student', 'writer', 'player', 'worker',
        'manager', 'user', 'owner', 'mother', 'father', 'brother', 'sister',
        'friend', 'dog', 'cat', 'person', 'man', 'woman', 'child',
        'weather', 'news', 'traffic', 'information', 'advice', 'homework',
        'knowledge', 'furniture', 'equipment', 'money', 'software'
    }
    
    PLURAL_SUBJECTS = {'they', 'we', 'these', 'those', 'people', 'children', 'men', 'women', 'friends', 'students', 'teachers'}
    
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
        
        # 1. Detect Context (Used for consistency)
        past_indicators = {'yesterday', 'ago', 'last', 'previously', 'before', 'already'}
        text_lower = text.lower()
        has_keyword = any(ind in text_lower for ind in past_indicators)
        has_past_verb = any(word in self.STRONG_PAST_VERBS for word in text_lower.split())
        global_past_context = has_keyword or has_past_verb
        
        # 2. Pre-Processing
        errors.extend(self._check_sentence_capitalization(text))
        words = self._tokenize(text)
        
        # 3. Apply Checks
        errors.extend(self._check_quantifiers(text, words))
        errors.extend(self._check_double_comparatives(text, words))
        errors.extend(self._check_explain_errors(text, words))
        errors.extend(self._check_redundancy(text, words))
        
        errors.extend(self._check_contractions(text, words))
        errors.extend(self._check_subject_verb_agreement(text, words))
        errors.extend(self._check_possessive_pronouns(text, words))
        errors.extend(self._check_verb_tense(text, words, force_past=global_past_context))
        errors.extend(self._check_progressive_tense(text, words))
        errors.extend(self._check_say_to_tell(text, words))
        errors.extend(self._check_past_tense_after_conjunction(text, words))
        errors.extend(self._check_gerund_patterns(text, words))
        errors.extend(self._check_third_person_verbs(text, words))
        errors.extend(self._check_plural_nouns(text, words))
        errors.extend(self._check_incorrect_regularized_past(text, words))
        errors.extend(self._check_pronoun_capitalization(text, words))
        errors.extend(self._check_infinitive_patterns(text, words))
        errors.extend(self._check_to_verb_form(text, words))
        errors.extend(self._check_articles(text, words))
        errors.extend(self._check_adverbs(text, words))
        errors.extend(self._check_prepositions(text, words))
        errors.extend(self._check_confused_words(text, words))
        errors.extend(self._check_prepositions_context(text, words))
        errors.extend(self._check_possessives_context(text, words))
        
        return errors
    
    def _tokenize(self, text: str) -> List[Tuple[str, int, int]]:
        tokens = []
        for match in re.finditer(r"\b\w+(?:'\w+)?\b", text):
            tokens.append((match.group().lower(), match.start(), match.end()))
        return tokens

    def _check_sentence_capitalization(self, text: str) -> List[Dict]:
        errors = []
        # Rule 1: First letter of the entire text (ignoring whitespace)
        first_match = re.match(r'^\s*([a-z])', text)
        if first_match:
            char = first_match.group(1)
            start = first_match.start(1)
            end = first_match.end(1)
            errors.append({
                'type': 'grammar',
                'position': {'start': start, 'end': end},
                'original': char,
                'suggestion': char.upper(),
                'explanation': 'Sentences should start with a capital letter.',
                'sentenceIndex': 0,
            })
        
        # Rule 2: First letter after sentence punctuation (. ? !)
        for match in re.finditer(r'([.!?]\s+)([a-z])', text):
            char = match.group(2)
            start = match.start(2)
            end = match.end(2)
            errors.append({
                'type': 'grammar',
                'position': {'start': start, 'end': end},
                'original': char,
                'suggestion': char.upper(),
                'explanation': 'Sentences should start with a capital letter.',
                'sentenceIndex': 0,
            })
        return errors

    def _check_pronoun_capitalization(self, text: str, words: List[Tuple[str, int, int]]) -> List[Dict]:
        errors = []
        for word, start, end in words:
            if word == 'i':
                errors.append({
                    'type': 'grammar',
                    'position': {'start': start, 'end': end},
                    'original': text[start:end],
                    'suggestion': 'I',
                    'explanation': 'Capitalize "I".',
                    'sentenceIndex': 0,
                })
        return errors

    def _check_contractions(self, text: str, words: List[Tuple[str, int, int]]) -> List[Dict]:
        errors = []
        contraction_fixes = {
            'dont': "don't", 'doesnt': "doesn't", 'didnt': "didn't", 'wont': "won't",
            'cant': "can't", 'couldnt': "couldn't", 'wouldnt': "wouldn't", 'shouldnt': "shouldn't",
            'isnt': "isn't", 'arent': "aren't", 'wasnt': "wasn't", 'werent': "weren't",
            'hasnt': "hasn't", 'havent': "haven't", 'hadnt': "hadn't",
            'ive': "I've", 'youve': "you've", 'theyve': "they've", 'weve': "we've",
            'hes': "he's", 'shes': "she's", 'its': "it's", 'thats': "that's", 'whats': "what's",
            'heres': "here's", 'theres': "there's", 'im': "I'm", 'youre': "you're",
            'theyre': "they're", 'were': "we're", 'ill': "I'll", 'youll': "you'll",
            'theyll': "they'll", 'well': "we'll", 'hell': "he'll", 'shell': "she'll", 'itll': "it'll"
        }
        for word, start, end in words:
            if word in contraction_fixes:
                suggestion = contraction_fixes[word]
                errors.append({'type': 'grammar', 'position': {'start': start, 'end': end}, 'original': text[start:end], 'suggestion': suggestion, 'explanation': f'Use "{suggestion}".', 'sentenceIndex': 0})
        return errors

    def _check_quantifiers(self, text: str, words: List[Tuple[str, int, int]]) -> List[Dict]:
        errors = []
        # Pattern: "No enough" at start of ANY line (using MULTILINE flag)
        for match in re.finditer(r'^\s*(no)\s+enough\b', text, re.IGNORECASE | re.MULTILINE):
            errors.append({
                'type': 'grammar',
                'position': {'start': match.start(1), 'end': match.end(1)}, # Target 'No'
                'original': match.group(1),
                'suggestion': 'Not',
                'explanation': 'Use "Not enough" at the start of a sentence.',
                'sentenceIndex': 0
            })
        
        # Pattern: "no enough" mid-sentence
        for match in re.finditer(r'(?<!^)\s+(no)\s+enough\b', text, re.IGNORECASE):
            errors.append({
                'type': 'grammar',
                'position': {'start': match.start(1), 'end': match.end(1)},
                'original': match.group(1),
                'suggestion': 'not',
                'explanation': 'Use "not enough".',
                'sentenceIndex': 0
            })
        return errors

    def _check_double_comparatives(self, text: str, words: List[Tuple[str, int, int]]) -> List[Dict]:
        errors = []
        for match in re.finditer(r'\bmore\s+([a-z]+er)\b', text, re.IGNORECASE):
            adj = match.group(1)
            if adj not in {'never', 'ever', 'over', 'under', 'river', 'paper', 'water', 'corner', 'father', 'mother', 'brother', 'sister', 'summer', 'winter', 'dinner', 'offer', 'answer'}:
                errors.append({
                    'type': 'grammar', 
                    'position': {'start': match.start(), 'end': match.end()}, 
                    'original': match.group(), 
                    'suggestion': adj, 
                    'explanation': f'Redundant comparative. Use "{adj}".', 
                    'sentenceIndex': 0
                })
        return errors

    def _check_verb_tense(self, text: str, words: List[Tuple[str, int, int]], force_past: bool = False) -> List[Dict]:
        errors = []
        for i, (word, start, end) in enumerate(words):
            if i == 0 and not force_past: continue
            
            if i == 0 and force_past:
                if word in self.VERB_FORMS and word not in {'be', 'is', 'are', 'was', 'were', 'have', 'has', 'had'}:
                    past_form = self.VERB_FORMS[word][0]
                    if word != past_form:
                        errors.append({'type': 'grammar', 'position': {'start': start, 'end': end}, 'original': text[start:end], 'suggestion': past_form.capitalize(), 'explanation': 'Use past tense.', 'sentenceIndex': 0})
                continue

            if i > 0:
                prev_word = words[i - 1][0]
                if prev_word == 'to' or prev_word in {'can', 'could', 'will', 'would', 'should', 'may', 'might', 'must', 'did', 'do', 'does'}:
                    continue
                if i > 1:
                    prev_prev = words[i-2][0]
                    if prev_prev in {'help', 'helped', 'helps', 'make', 'made', 'makes', 'let', 'lets', 'see', 'saw', 'watch', 'watched', 'hear', 'heard'}:
                        continue 
                
                if force_past:
                    if word in self.VERB_FORMS and word not in {'be', 'is', 'are', 'was', 'were', 'have', 'has', 'had'}:
                        past_form = self.VERB_FORMS[word][0]
                        if word != past_form and word == word: 
                            errors.append({'type': 'grammar', 'position': {'start': start, 'end': end}, 'original': text[start:end], 'suggestion': past_form, 'explanation': 'Use past tense.', 'sentenceIndex': 0})
        return errors

    def _check_explain_errors(self, text: str, words: List[Tuple[str, int, int]]) -> List[Dict]:
        errors = []
        pronouns = {'him', 'her', 'me', 'us', 'them', 'you'}
        for i, (word, start, end) in enumerate(words):
            if word in ('explain', 'explained', 'explains') and i + 1 < len(words):
                next_word, next_start, next_end = words[i+1]
                if next_word in pronouns:
                    errors.append({
                        'type': 'grammar',
                        'position': {'start': start, 'end': next_end},
                        'original': text[start:next_end],
                        'suggestion': f'{word} to {next_word}',
                        'explanation': f'Use "to" after "{word}" when followed by a person.',
                        'sentenceIndex': 0
                    })
        return errors

    def _check_prepositions(self, text: str, words: List[Tuple[str, int, int]]) -> List[Dict]:
        errors = []
        prep_map = {
            'married with': 'married to', 'good in': 'good at', 'angry to': 'angry with',
            'depend of': 'depend on', 'listen her': 'listen to her', 'arrive to': 'arrive at'
        }
        tl = text.lower()
        for wrong, right in prep_map.items():
            if wrong in tl:
                idx = tl.find(wrong)
                errors.append({'type': 'grammar', 'position': {'start': idx, 'end': idx+len(wrong)}, 'original': text[idx:idx+len(wrong)], 'suggestion': right, 'explanation': f'Use "{right}".', 'sentenceIndex': 0})
        
        zero_article = {'work', 'school', 'bed', 'church', 'college', 'jail', 'class'}
        definite = {'library', 'mall', 'park', 'cinema', 'gym', 'bank', 'store', 'office', 'beach', 'zoo'}
        go_exceptions = {'to', 'into', 'in', 'out', 'up', 'down', 'back', 'on', 'home', 'away'}
        
        for i, (word, start, end) in enumerate(words):
            if word in ('go', 'goes', 'went', 'going') and i + 1 < len(words):
                next_word, next_start, next_end = words[i + 1]
                if next_word not in go_exceptions:
                    if next_word in zero_article:
                        errors.append({'type': 'grammar', 'position': {'start': next_start, 'end': next_end}, 'original': text[next_start:next_end], 'suggestion': 'to ' + text[next_start:next_end], 'explanation': 'Missing "to".', 'sentenceIndex': 0})
                    elif next_word in definite or (next_word.endswith('s') and len(next_word)>3):
                        errors.append({'type': 'grammar', 'position': {'start': next_start, 'end': next_end}, 'original': text[next_start:next_end], 'suggestion': 'to the ' + text[next_start:next_end], 'explanation': 'Missing "to the".', 'sentenceIndex': 0})
        return errors

    def _check_to_verb_form(self, text: str, words: List[Tuple[str, int, int]]) -> List[Dict]:
        errors = []
        for i, (word, start, end) in enumerate(words):
            if i > 0 and words[i-1][0] == 'to':
                if word in self.verb_base_lookup:
                    base = self.verb_base_lookup[word]
                    if word != base:
                        errors.append({
                            'type': 'grammar',
                            'position': {'start': start, 'end': end},
                            'original': text[start:end],
                            'suggestion': base,
                            'explanation': f'Use base form "{base}" after "to".',
                            'sentenceIndex': 0,
                        })
        return errors

    def _check_adverbs(self, text: str, words: List[Tuple[str, int, int]]) -> List[Dict]:
        errors = []
        adj_to_adv = {'quick': 'quickly', 'slow': 'slowly', 'loud': 'loudly', 'quiet': 'quietly', 'bad': 'badly', 'easy': 'easily', 'careful': 'carefully', 'real': 'really'}
        verbs = {'run', 'runs', 'ran', 'walk', 'walks', 'walked', 'speak', 'spoke', 'speaks', 'sing', 'sang', 'sings', 'eat', 'eats', 'ate', 'talk', 'talks', 'talked', 'drive', 'drives', 'drove'}
        for i, (word, start, end) in enumerate(words):
            if i > 0 and words[i-1][0] in verbs and word in adj_to_adv:
                 errors.append({'type': 'grammar', 'position': {'start': start, 'end': end}, 'original': text[start:end], 'suggestion': adj_to_adv[word], 'explanation': 'Use adverb.', 'sentenceIndex': 0})
        return errors

    def _check_redundancy(self, text: str, words: List[Tuple[str, int, int]]) -> List[Dict]:
        errors = []
        red = {'return back': 'return', 'repeat again': 'repeat', 'reply back': 'reply', 'join together': 'join'}
        for phrase, fix in red.items():
            if phrase in text.lower():
                idx = text.lower().find(phrase)
                errors.append({'type': 'grammar', 'position': {'start': idx, 'end': idx+len(phrase)}, 'original': text[idx:idx+len(phrase)], 'suggestion': fix, 'explanation': 'Redundant.', 'sentenceIndex': 0})
        return errors

    def _check_subject_verb_agreement(self, text: str, words: List[Tuple[str, int, int]]) -> List[Dict]:
        errors = []
        adverbs_to_skip = {'already', 'just', 'always', 'never', 'really', 'often', 'usually', 'sometimes'}
        
        for i, (word, start, end) in enumerate(words):
            if i > 0:
                prev_word = words[i - 1][0]
                actual_subject = prev_word
                if prev_word in adverbs_to_skip and i > 1:
                    actual_subject = words[i - 2][0]
                
                if actual_subject in self.SINGULAR_SUBJECTS:
                    if word == 'are':
                        errors.append({'type': 'grammar', 'position': {'start': start, 'end': end}, 'original': text[start:end], 'suggestion': 'is', 'explanation': f'"{actual_subject}" is singular, use "is".', 'sentenceIndex': 0})
                    elif word == 'were':
                        errors.append({'type': 'grammar', 'position': {'start': start, 'end': end}, 'original': text[start:end], 'suggestion': 'was', 'explanation': f'"{actual_subject}" is singular, use "was".', 'sentenceIndex': 0})
                
                elif actual_subject in self.PLURAL_SUBJECTS:
                    if word == 'is':
                        errors.append({'type': 'grammar', 'position': {'start': start, 'end': end}, 'original': text[start:end], 'suggestion': 'are', 'explanation': f'"{actual_subject}" is plural, use "are".', 'sentenceIndex': 0})
                    elif word == 'was':
                         errors.append({'type': 'grammar', 'position': {'start': start, 'end': end}, 'original': text[start:end], 'suggestion': 'were', 'explanation': f'"{actual_subject}" is plural, use "were".', 'sentenceIndex': 0})
        return errors

    def _check_possessive_pronouns(self, text: str, words: List[Tuple[str, int, int]]) -> List[Dict]:
        errors = []
        possession_indicators = {'battery', 'phone', 'car', 'house', 'name', 'book', 'life', 'work', 'job', 'friend', 'family'}
        for i, (word, start, end) in enumerate(words):
            if i < len(words) - 1:
                next_word = words[i + 1][0]
                if word == 'it' and next_word in possession_indicators:
                    errors.append({'type': 'grammar', 'position': {'start': start, 'end': end}, 'original': text[start:end], 'suggestion': 'its', 'explanation': 'Use "its".', 'sentenceIndex': 0})
        return errors

    # --- Passthrough for less common rules ---
    def _check_say_to_tell(self, t, w): return []
    def _check_past_tense_after_conjunction(self, t, w): return []
    def _check_gerund_patterns(self, t, w): return []
    def _check_plural_nouns(self, t, w): return []
    def _check_incorrect_regularized_past(self, t, w): return []
    def _check_infinitive_patterns(self, t, w): return []
    def _check_articles(self, t, w): return []
    def _check_confused_words(self, t, w): return []
    def _check_prepositions_context(self, t, w): return []
    def _check_possessives_context(self, t, w): return []
    def _check_progressive_tense(self, t, w): return []
    def _check_third_person_verbs(self, t, w): return []

# Global instance
_grammar_rules_checker = None
def get_grammar_rules_checker() -> GrammarRulesChecker:
    global _grammar_rules_checker
    if _grammar_rules_checker is None:
        _grammar_rules_checker = GrammarRulesChecker()
    return _grammar_rules_checker
