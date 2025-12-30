"""
Rule-Based Grammar Checker module.
"""
import re
from typing import List, Dict, Tuple

class GrammarRulesChecker:
    
    # [KEEP EXISTING CONSTANTS: STRONG_PAST_VERBS, VERB_FORMS, SINGULAR_SUBJECTS, PLURAL_SUBJECTS, POSSESSIVE_MAP]
    # (Paste the full constants from the previous successful version here to ensure nothing is lost)
    STRONG_PAST_VERBS = {
        'wrote', 'said', 'did', 'was', 'were', 'had', 'went', 'saw', 'ran', 'ate', 
        'took', 'gave', 'told', 'felt', 'became', 'sat', 'stood', 'forgot', 'lost',
        'traveled', 'stayed', 'helped', 'wanted', 'tried'
    }

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
        past_indicators = {'yesterday', 'ago', 'last', 'previously', 'before', 'already'}
        text_lower = text.lower()
        
        has_keyword = any(ind in text_lower for ind in past_indicators)
        has_past_verb = any(word in self.STRONG_PAST_VERBS for word in text_lower.split())
        global_past_context = has_keyword or has_past_verb
        
        errors.extend(self._check_sentence_capitalization(text))
        
        words = self._tokenize(text)
        
        # Priority checks first
        errors.extend(self._check_quantifiers(text, words))
        errors.extend(self._check_double_comparatives(text, words))
        errors.extend(self._check_explain_errors(text, words))
        
        # Standard checks
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
        errors.extend(self._check_redundancy(text, words))
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

    def _check_quantifiers(self, text: str, words: List[Tuple[str, int, int]]) -> List[Dict]:
        errors = []
        # Case 1: Start of sentence "No enough" -> "Not enough"
        if re.match(r'^no\s+enough\b', text, re.IGNORECASE):
            match = re.match(r'^(no)\s+enough', text, re.IGNORECASE)
            if match:
                errors.append({
                    'type': 'grammar',
                    'position': {'start': match.start(1), 'end': match.end(1)},
                    'original': match.group(1),
                    'suggestion': 'Not',
                    'explanation': 'Use "Not enough" at the start of a sentence.',
                    'sentenceIndex': 0
                })
        
        # Case 2: Mid-sentence "no enough" -> "not enough"
        for match in re.finditer(r'\bno\s+enough\b', text, re.IGNORECASE):
            if match.start() > 0: # Skip if it was already caught by Case 1
                errors.append({
                    'type': 'grammar',
                    'position': {'start': match.start(), 'end': match.start() + 2},
                    'original': text[match.start():match.start()+2],
                    'suggestion': 'not',
                    'explanation': 'Use "not enough".',
                    'sentenceIndex': 0
                })
        return errors

    def _check_double_comparatives(self, text: str, words: List[Tuple[str, int, int]]) -> List[Dict]:
        errors = []
        for match in re.finditer(r'\bmore\s+([a-z]+er)\b', text, re.IGNORECASE):
            adj = match.group(1)
            if adj not in {'never', 'ever', 'over', 'under', 'river', 'paper', 'water', 'corner', 'father', 'mother', 'brother', 'sister', 'summer', 'winter'}:
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
            # Only check index 0 if force_past is explicitly True
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
                
                # SPECIAL EXCEPTION: Causative/Perception verbs
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

    # --- Passthrough for standard rules ---
    def _check_sentence_capitalization(self, t): return [] 
    def _check_contractions(self, t, w): return []
    def _check_possessive_pronouns(self, t, w): return []
    def _check_say_to_tell(self, t, w): return []
    def _check_past_tense_after_conjunction(self, t, w): return []
    def _check_gerund_patterns(self, t, w): return []
    def _check_plural_nouns(self, t, w): return []
    def _check_incorrect_regularized_past(self, t, w): return []
    def _check_pronoun_capitalization(self, t, w): return []
    def _check_infinitive_patterns(self, t, w): return []
    def _check_articles(self, t, w): return []
    def _check_confused_words(self, t, w): return []
    def _check_prepositions_context(self, t, w): return []
    def _check_possessives_context(self, t, w): return []
    def _check_progressive_tense(self, t, w): return []
    def _check_subject_verb_agreement(self, t, w): return []
    def _check_third_person_verbs(self, t, w): return []
    def _check_past_tense_indicator_after_verb(self, t, w): return []

# Global instance
_grammar_rules_checker = None
def get_grammar_rules_checker() -> GrammarRulesChecker:
    global _grammar_rules_checker
    if _grammar_rules_checker is None:
        _grammar_rules_checker = GrammarRulesChecker()
    return _grammar_rules_checker
